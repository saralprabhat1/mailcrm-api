# scripts/dedup_zavenir_requirements.py
#
# PURPOSE: Remove duplicate records from the zavenir_requirements Supabase table.
#
# WHY DUPLICATES EXIST:
#   req_id format is REQ-YYYYMMDD-HASH-NN where:
#     YYYYMMDD = the date the pipeline RAN (not the email date)
#     HASH     = MD5 of the Outlook conversationId (stable across runs)
#     NN       = product index within the thread (01, 02, 03 ...)
#   Running the pipeline on different days gives the SAME conversation a
#   DIFFERENT req_id (only the date prefix changes). Supabase upsert keys on
#   req_id, so each new run-date inserts a fresh row instead of updating —
#   e.g. REQ-20260609-2ACFF3-01 and REQ-20260610-2ACFF3-01 are the same
#   enquiry stored twice.
#
# WHAT THIS SCRIPT DOES:
#   1. Fetch all rows from zavenir_requirements
#   2. Group rows by their stable key: the HASH-NN part of req_id
#   3. In each group with more than one row, keep the LATEST row
#      (highest date prefix; ties broken by created_at, then id)
#   4. Delete the older rows by primary key (id)
#   5. Print a before/after summary
#
# SAFE TO RE-RUN: a table with no duplicates results in zero deletions.

import os
import re
import sys
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client

# --- Locate project root (this file lives in scripts/) and load .env ---
PROJECT_ROOT = Path(__file__).parent.parent
load_dotenv(dotenv_path=PROJECT_ROOT / ".env")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY")
TABLE        = "zavenir_requirements"

# req_id pattern: REQ-20260610-2ACFF3-01
#   group 1 = date prefix (YYYYMMDD) — changes per run
#   group 2 = HASH-NN — stable per conversation+product, used as dedup key
_REQ_ID_RE = re.compile(r"^REQ-(\d{8})-([0-9A-F]{6}-\d{2})$", re.IGNORECASE)


def fetch_all_rows(supabase):
    """Fetch every row from the table. Returns a list of dicts."""
    try:
        resp = supabase.table(TABLE).select("*").execute()
        return resp.data or []
    except Exception as e:
        print(f"ERROR: could not fetch rows from {TABLE}: {e}")
        sys.exit(1)


def dedup_key(req_id: str):
    """
    Return the stable part of a req_id (HASH-NN), or None if the format
    doesn't match. Rows with unparseable req_ids are left untouched.
    """
    if not req_id:
        return None
    match = _REQ_ID_RE.match(req_id.strip())
    return match.group(2).upper() if match else None


def sort_newest_first(rows: list) -> list:
    """
    Sort a group of duplicate rows so the row to KEEP comes first.
    Order: date prefix in req_id (newest run first), then created_at,
    then id — all descending.
    """
    def sort_value(row):
        match = _REQ_ID_RE.match((row.get("req_id") or "").strip())
        date_prefix = match.group(1) if match else "00000000"
        return (date_prefix, row.get("created_at") or "", row.get("id") or 0)

    return sorted(rows, key=sort_value, reverse=True)


def main():
    if not (SUPABASE_URL and SUPABASE_KEY):
        print("ERROR: SUPABASE_URL / SUPABASE_SERVICE_KEY not found in .env")
        sys.exit(1)

    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    print(f"Connected to Supabase — table: {TABLE}")

    rows = fetch_all_rows(supabase)
    print(f"Total rows before dedup: {len(rows)}")

    # --- Group rows by their stable HASH-NN key ---
    groups = {}
    unparseable = 0
    for row in rows:
        key = dedup_key(row.get("req_id"))
        if key is None:
            unparseable += 1
            continue
        groups.setdefault(key, []).append(row)

    if unparseable:
        print(f"  {unparseable} row(s) had unparseable req_ids — left untouched.")

    # --- Find groups with duplicates and decide which rows to delete ---
    ids_to_delete = []
    for key, group in groups.items():
        if len(group) < 2:
            continue
        ordered = sort_newest_first(group)
        keep    = ordered[0]
        drop    = ordered[1:]
        print(f"\n  Duplicate group {key}: {len(group)} rows")
        print(f"    KEEP   {keep.get('req_id')}  (id={keep.get('id')}, created {str(keep.get('created_at'))[:19]})")
        for row in drop:
            print(f"    DELETE {row.get('req_id')}  (id={row.get('id')}, created {str(row.get('created_at'))[:19]})")
            ids_to_delete.append(row["id"])

    if not ids_to_delete:
        print("\nNo duplicates found — nothing to delete.")
        return

    # --- Delete the older rows by primary key ---
    print(f"\nDeleting {len(ids_to_delete)} duplicate row(s)...")
    deleted = 0
    for row_id in ids_to_delete:
        try:
            supabase.table(TABLE).delete().eq("id", row_id).execute()
            deleted += 1
        except Exception as e:
            print(f"  ERROR deleting id={row_id}: {e}")

    print(f"Deleted {deleted}/{len(ids_to_delete)} row(s).")
    remaining = fetch_all_rows(supabase)
    print(f"Total rows after dedup: {len(remaining)}")


if __name__ == "__main__":
    main()
