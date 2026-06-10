# scripts/upload_zavenir_customers.py
#
# PURPOSE: Upload the Zavenir customer master list to Supabase.
#
# WHAT IT DOES (in order):
#   1. Read data/zavenir_customers_base.xlsx (633-row customer master)
#   2. Normalize whatever column headers the file has into the
#      zavenir_customers table schema (see COLUMN_MAP below) — the xlsx was
#      built in a separate chat session, so header names may vary
#   3. Print which columns were mapped and which were skipped, so the schema
#      can be extended if the file has useful extra columns
#   4. Clean the rows: trim whitespace, drop rows with no customer name,
#      de-duplicate by customer name (keep first occurrence)
#   5. Upsert all rows to the zavenir_customers Supabase table in batches
#      (conflict key: customer_name — safe to re-run)
#
# PREREQUISITE: run scripts/create_zavenir_customers_table.sql in the
# Supabase SQL Editor first, so the table exists.

import os
import re
import sys
from pathlib import Path
from dotenv import load_dotenv
import pandas as pd
from supabase import create_client

# --- Locate project root (this file lives in scripts/) and load .env ---
PROJECT_ROOT = Path(__file__).parent.parent
load_dotenv(dotenv_path=PROJECT_ROOT / ".env")

XLSX_PATH    = PROJECT_ROOT / "data" / "zavenir_customers_base.xlsx"
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY")
TABLE        = "zavenir_customers"
BATCH_SIZE   = 100   # rows per Supabase upsert call

# ---------------------------------------------------------------------------
# COLUMN MAPPING
# Keys are normalized xlsx headers (lowercase, spaces/punctuation -> _).
# Values are zavenir_customers column names.
# Any xlsx column not listed here is reported and skipped.
# ---------------------------------------------------------------------------

COLUMN_MAP = {
    # customer name variants
    "customer_name": "customer_name",
    "customer":      "customer_name",
    "company_name":  "customer_name",
    "company":       "customer_name",
    "account_name":  "customer_name",
    "account":       "customer_name",
    "name":          "customer_name",
    # domain / website variants
    "domain":   "domain",
    "website":  "domain",
    "web_site": "domain",
    "url":      "domain",
    "web":      "domain",
    # location variants
    "city":     "city",
    "town":     "city",
    "state":    "state",
    "region":   "state",
    "country":  "country",
    "address":  "address",
    "location": "city",
    # industry variants
    "industry_segment": "industry_segment",
    "industry":         "industry_segment",
    "segment":          "industry_segment",
    "sector":           "industry_segment",
    # contact variants
    "contact_person": "contact_person",
    "contact_name":   "contact_person",
    "contact":        "contact_person",
    "contact_email":  "contact_email",
    "email":          "contact_email",
    "e_mail":         "contact_email",
    "email_id":       "contact_email",
    "contact_phone":  "contact_phone",
    "phone":          "contact_phone",
    "mobile":         "contact_phone",
    "phone_number":   "contact_phone",
    # notes variants
    "notes":    "notes",
    "remarks":  "notes",
    "comments": "notes",
}


def normalize_header(header: str) -> str:
    """Lowercase a header and replace spaces/punctuation with underscores,
    so 'Company Name' and 'company-name' both become 'company_name'."""
    header = str(header).strip().lower()
    header = re.sub(r"[^a-z0-9]+", "_", header)
    return header.strip("_")


def clean_domain(value: str) -> str:
    """Strip scheme, www. prefix and trailing path from a website value,
    so 'https://www.elematic.com/products' becomes 'elematic.com'."""
    value = str(value).strip().lower()
    value = re.sub(r"^https?://", "", value)
    value = re.sub(r"^www\.", "", value)
    value = value.split("/")[0].strip()
    return value


def load_and_map() -> pd.DataFrame:
    """Read the xlsx and return a DataFrame with schema column names only."""
    if not XLSX_PATH.exists():
        print(f"ERROR: {XLSX_PATH} not found.")
        print("Copy zavenir_customers_base.xlsx into the data/ folder first.")
        sys.exit(1)

    df = pd.read_excel(XLSX_PATH, dtype=str).fillna("")
    print(f"Read {len(df)} rows from {XLSX_PATH.name}")
    print(f"Columns in file: {list(df.columns)}")

    # --- Map each xlsx column to a schema column (first match wins) ---
    mapped, skipped = {}, []
    for col in df.columns:
        target = COLUMN_MAP.get(normalize_header(col))
        if target and target not in mapped:
            mapped[target] = col
        else:
            skipped.append(col)

    print(f"\nMapped columns : { {v: k for k, v in mapped.items()} }")
    if skipped:
        print(f"Skipped columns: {skipped}")
        print("  (Extend COLUMN_MAP + the DDL if any of these should be kept.)")

    if "customer_name" not in mapped:
        print("\nERROR: no customer-name column found in the xlsx.")
        print("Add its header to COLUMN_MAP and re-run.")
        sys.exit(1)

    out = pd.DataFrame({target: df[src] for target, src in mapped.items()})

    # --- Clean values ---
    out = out.apply(lambda s: s.str.strip())
    out["customer_name"] = out["customer_name"].str.strip()
    out = out[out["customer_name"] != ""]                      # drop empty names
    before = len(out)
    out = out.drop_duplicates("customer_name", keep="first")   # de-dup in-file
    if before != len(out):
        print(f"\nDropped {before - len(out)} duplicate customer-name row(s) within the file.")

    if "domain" in out.columns:
        out["domain"] = out["domain"].map(lambda v: clean_domain(v) if v else "")
        # Mark where the domain came from, for the enrichment script
        out["domain_source"] = out["domain"].map(lambda v: "xlsx" if v else None)

    print(f"\n{len(out)} clean customer row(s) ready for upload.")
    return out


def upload(df: pd.DataFrame):
    """Upsert all rows to Supabase in batches, conflict key customer_name."""
    if not (SUPABASE_URL and SUPABASE_KEY):
        print("ERROR: SUPABASE_URL / SUPABASE_SERVICE_KEY not found in .env")
        sys.exit(1)

    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    print(f"Connected to Supabase — table: {TABLE}")

    # Convert empty strings to None so Supabase stores NULL, not ""
    rows = [
        {k: (v if v not in ("", None) else None) for k, v in row.items()}
        for row in df.to_dict(orient="records")
    ]

    uploaded = 0
    for start in range(0, len(rows), BATCH_SIZE):
        batch = rows[start:start + BATCH_SIZE]
        try:
            supabase.table(TABLE).upsert(batch, on_conflict="customer_name").execute()
            uploaded += len(batch)
            print(f"  Upserted rows {start + 1}-{start + len(batch)}")
        except Exception as e:
            print(f"  ERROR upserting batch starting at row {start + 1}: {e}")

    print(f"\nDone: {uploaded}/{len(rows)} row(s) upserted to {TABLE}.")


if __name__ == "__main__":
    customers = load_and_map()
    upload(customers)
