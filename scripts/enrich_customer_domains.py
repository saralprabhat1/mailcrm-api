# scripts/enrich_customer_domains.py
#
# PURPOSE: Fill in the missing company domains in the Zavenir customer master.
#
# WHY: once every customer has a domain, an incoming enquiry's sender email
# domain (Phase 18 sender_email) can be matched directly against the customer
# master — domain matching is far more reliable than company-name matching.
#
# WHAT IT DOES (for each row in data/zavenir_customers_base.xlsx that has
# no domain yet):
#   1. EMAIL PATH  — if the row has a contact email on a business domain
#      (not gmail/yahoo/etc.), use that domain. Free and always correct.
#   2. LOOKUP PATH — query the Clearbit Autocomplete API (free, no API key:
#      autocomplete.clearbit.com) with the company name. Accept the best
#      suggestion only if its name closely matches ours (difflib ratio
#      >= 0.55 after stripping legal suffixes like "Pvt Ltd") — this guard
#      prevents wrong-company domains being written.
#   3. NO MATCH    — leave the domain blank; the row is listed at the end
#      for manual lookup.
#
# OUTPUT:
#   - data/zavenir_customers_base.xlsx updated in place
#     (adds/fills 'domain' and 'domain_source' columns)
#   - Supabase zavenir_customers rows updated (domain + domain_source)
#   - Progress is checkpointed to the xlsx every 25 lookups, so an
#     interrupted run loses at most 25 results
#
# SAFE TO RE-RUN: rows that already have a domain are skipped.

import os
import re
import sys
import time
import difflib
from pathlib import Path
from dotenv import load_dotenv
import pandas as pd
import requests
from supabase import create_client

# --- Locate project root (this file lives in scripts/) and load .env ---
PROJECT_ROOT = Path(__file__).parent.parent
load_dotenv(dotenv_path=PROJECT_ROOT / ".env")

XLSX_PATH    = PROJECT_ROOT / "data" / "zavenir_customers_base.xlsx"
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY")
TABLE        = "zavenir_customers"

CLEARBIT_URL    = "https://autocomplete.clearbit.com/v1/companies/suggest"
LOOKUP_DELAY    = 1.0    # seconds between API calls — be polite, avoid blocks
CHECKPOINT_EVERY = 25    # save the xlsx every N lookups
MIN_NAME_SIMILARITY = 0.55

# Personal-email providers — a contact on one of these tells us nothing
# about the company's own domain.
FREE_EMAIL_DOMAINS = {
    "gmail.com", "yahoo.com", "yahoo.in", "yahoo.co.in", "hotmail.com",
    "outlook.com", "live.com", "rediffmail.com", "rediff.com", "aol.com",
    "icloud.com", "protonmail.com", "mail.com", "zoho.com", "ymail.com",
}

# Legal suffixes stripped before comparing company names, so
# "Elematic India Pvt Ltd" matches Clearbit's "Elematic".
_LEGAL_SUFFIX_RE = re.compile(
    r"\b(pvt|private|ltd|limited|llp|llc|inc|incorporated|corp|corporation|"
    r"co|company|industries|india|intl|international|group|gmbh|sa|plc)\b\.?",
    re.IGNORECASE,
)


def normalize_name(name: str) -> str:
    """Lowercase a company name and strip legal suffixes + punctuation,
    leaving just the distinctive part for similarity comparison."""
    name = _LEGAL_SUFFIX_RE.sub(" ", str(name).lower())
    name = re.sub(r"[^a-z0-9 ]+", " ", name)
    return re.sub(r"\s+", " ", name).strip()


def domain_from_email(email: str) -> str | None:
    """Return the domain part of a business email, or None if it's a
    personal-provider address (gmail etc.) or not an email at all."""
    email = str(email).strip().lower()
    if "@" not in email:
        return None
    domain = email.split("@")[-1].strip()
    if not domain or "." not in domain or domain in FREE_EMAIL_DOMAINS:
        return None
    return domain


def lookup_clearbit(company_name: str) -> str | None:
    """Query Clearbit Autocomplete for the company. Returns the domain of
    the best name-matching suggestion, or None if nothing matches well."""
    try:
        resp = requests.get(
            CLEARBIT_URL, params={"query": company_name}, timeout=15
        )
        resp.raise_for_status()
        suggestions = resp.json()
    except requests.exceptions.RequestException as e:
        print(f"    Clearbit error: {e}")
        return None
    except ValueError:
        return None   # response was not JSON

    ours = normalize_name(company_name)
    if not ours or not suggestions:
        return None

    # Pick the suggestion whose name is most similar to ours
    best_domain, best_score = None, 0.0
    for s in suggestions:
        theirs = normalize_name(s.get("name", ""))
        score = difflib.SequenceMatcher(None, ours, theirs).ratio()
        if score > best_score:
            best_score, best_domain = score, s.get("domain")

    if best_score >= MIN_NAME_SIMILARITY and best_domain:
        return best_domain.strip().lower()
    return None


def main():
    if not XLSX_PATH.exists():
        print(f"ERROR: {XLSX_PATH} not found.")
        print("Copy zavenir_customers_base.xlsx into the data/ folder first.")
        sys.exit(1)

    df = pd.read_excel(XLSX_PATH, dtype=str).fillna("")
    print(f"Read {len(df)} rows from {XLSX_PATH.name}")

    # Find the customer-name column (same variants as the upload script)
    name_col = next(
        (c for c in df.columns
         if re.sub(r"[^a-z0-9]+", "_", str(c).strip().lower()).strip("_") in
         ("customer_name", "customer", "company_name", "company",
          "account_name", "account", "name")),
        None,
    )
    if not name_col:
        print("ERROR: no customer-name column found in the xlsx.")
        sys.exit(1)

    # Find an email column if one exists (for the free EMAIL PATH)
    email_col = next(
        (c for c in df.columns
         if "email" in str(c).lower() or "e-mail" in str(c).lower()),
        None,
    )

    # Make sure the output columns exist
    if "domain" not in df.columns:
        df["domain"] = ""
    if "domain_source" not in df.columns:
        df["domain_source"] = ""

    missing = df[df["domain"].str.strip() == ""]
    print(f"{len(missing)} row(s) missing a domain — starting enrichment.")
    print(f"Name column: '{name_col}' | Email column: '{email_col}'\n")

    # --- Supabase connection (updates pushed as we go) ---
    supabase = None
    if SUPABASE_URL and SUPABASE_KEY:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("Supabase connected — rows will be updated as domains are found.\n")
    else:
        print("WARNING: Supabase credentials missing — xlsx will be updated only.\n")

    found_email, found_lookup, not_found = 0, 0, []
    lookups_done = 0

    for idx in missing.index:
        company = df.at[idx, name_col].strip()
        if not company:
            continue

        domain, source = None, None

        # --- 1. EMAIL PATH — free and exact ---
        if email_col:
            domain = domain_from_email(df.at[idx, email_col])
            if domain:
                source = "email"
                found_email += 1

        # --- 2. LOOKUP PATH — Clearbit autocomplete ---
        if not domain:
            domain = lookup_clearbit(company)
            lookups_done += 1
            time.sleep(LOOKUP_DELAY)
            if domain:
                source = "clearbit"
                found_lookup += 1

        if domain:
            df.at[idx, "domain"] = domain
            df.at[idx, "domain_source"] = source
            print(f"  [{source:8}] {company[:45]:45} -> {domain}")

            # Push to Supabase immediately (keyed by customer_name)
            if supabase:
                try:
                    supabase.table(TABLE).update(
                        {"domain": domain, "domain_source": source}
                    ).eq("customer_name", company).execute()
                except Exception as e:
                    print(f"    Supabase update failed for {company}: {e}")
        else:
            not_found.append(company)
            print(f"  [no match] {company[:45]}")

        # --- Checkpoint: save xlsx every N lookups so progress survives ---
        if lookups_done and lookups_done % CHECKPOINT_EVERY == 0:
            df.to_excel(XLSX_PATH, index=False)
            print(f"  -- checkpoint saved ({lookups_done} lookups done) --")

    # --- Final save + summary ---
    df.to_excel(XLSX_PATH, index=False)
    print("\n" + "=" * 60)
    print("  DOMAIN ENRICHMENT SUMMARY")
    print("=" * 60)
    print(f"  Rows missing domain at start : {len(missing)}")
    print(f"  Found via contact email      : {found_email}")
    print(f"  Found via Clearbit lookup    : {found_lookup}")
    print(f"  Still missing                : {len(not_found)}")
    if not_found:
        print("\n  Manual lookup needed for:")
        for name in not_found[:50]:
            print(f"    - {name}")
        if len(not_found) > 50:
            print(f"    ... and {len(not_found) - 50} more")
    print(f"\n  Updated file: {XLSX_PATH}")


if __name__ == "__main__":
    main()
