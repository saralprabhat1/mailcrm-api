# run_zavenir_parser.py
#
# PURPOSE: Standalone pipeline runner for the Zavenir Daubert pipeline.
#
# WHAT IT DOES (in order):
#   1. Authenticate with Outlook using utils/auth.py
#   2. Fetch emails from inbox using 03_outlook/email_reader.py
#   3. Filter to only emails where the original sender is tarora@zavenir.com
#      — checks both the sender_email field and the body for forwarded-from patterns
#   4. Download and extract attachment text (PDF / DOCX / XLSX / ZIP) if present
#   5. Clean email body using 04_email_parser/parser.py
#   6. Send to Groq AI via utils/zavenir_extractor.py — extracts commercial fields
#   7. Generate a unique req_id in the same format as the GET Global pipeline
#   8. Save all new records to data/zavenir_crm.xlsx (creates file if not exists)
#   9. Upsert all records to Supabase zavenir_requirements table
#  10. Print a run summary: fetched / found / saved to Excel / saved to Supabase
#
# ISOLATION: This file is completely standalone.
#   - Does NOT import from run_parser.py, storage.py, or any GET Global module
#   - Shares only reusable utilities: auth, email_reader, parser, attachment_extractor
#   - Has its own Excel path, Supabase table, and save logic

import os
import sys
import hashlib
import datetime
import re
import requests
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
from openpyxl import load_workbook
from openpyxl.styles import PatternFill, Font, Alignment
from supabase import create_client

# ---------------------------------------------------------------------------
# PATH SETUP
# All imports below need the project root and sub-folders on sys.path.
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "03_outlook"))
sys.path.insert(0, str(PROJECT_ROOT / "04_email_parser"))

# Load .env from project root — same file used by all pipelines
load_dotenv(dotenv_path=PROJECT_ROOT / ".env")

# ---------------------------------------------------------------------------
# IMPORTS — shared utilities (read-only; we never modify these files)
# ---------------------------------------------------------------------------

from utils.auth import get_access_token
from email_reader import fetch_emails, get_email_attachments
import parser as email_parser
from utils.attachment_extractor import extract_text_from_attachment
from utils.zavenir_extractor import extract_zavenir_record
from configs.zavenir_daubert import FIELDS, EXCEL_OUTPUT, SUPABASE_TABLE, SENDER_FILTER

# ---------------------------------------------------------------------------
# SUPABASE CLIENT — zavenir pipeline uses the same credentials as GET Global
# ---------------------------------------------------------------------------

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY")

if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("Supabase connected (zavenir pipeline)")
else:
    supabase = None
    print("WARNING: Supabase credentials not found — cloud save disabled")

# ---------------------------------------------------------------------------
# FILE PATHS
# ---------------------------------------------------------------------------

DATA_DIR   = PROJECT_ROOT / "data"
EXCEL_PATH = PROJECT_ROOT / EXCEL_OUTPUT   # data/zavenir_crm.xlsx

# ---------------------------------------------------------------------------
# SENDER FILTER — pre-compiled for speed inside the per-email loop
# Matches "tarora@zavenir.com" anywhere in the email body text.
# Used to catch emails that Saral forwarded (the sender_email is Saral's
# address, but the original From: header in the body contains Tania's address).
# ---------------------------------------------------------------------------

_ZAVENIR_EMAIL_RE = re.compile(r"tarora@zavenir\.com", re.IGNORECASE)

GRAPH_BASE_URL = "https://graph.microsoft.com/v1.0"


def _search_zavenir_emails(token: str, max_results: int = 25) -> list:
    """
    Search all Outlook folders for emails containing 'tarora@zavenir.com'.

    Uses Graph API $search (full-text) instead of inbox-only fetch, so it finds
    emails regardless of which folder they're in (inbox, archive, subfolders).
    Does NOT apply the domain whitelist — Zavenir emails are handled by this
    pipeline directly, not by email_filters.py.

    Returns a list of dicts in the same format as fetch_emails().
    """
    fields = ",".join([
        "id", "subject", "receivedDateTime", "from",
        "body", "bodyPreview", "isRead", "hasAttachments", "importance"
    ])
    url = (
        f"{GRAPH_BASE_URL}/me/messages"
        f"?$search=\"tarora@zavenir.com\""
        f"&$select={fields}"
        f"&$top={max_results}"
    )
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    try:
        resp = requests.get(url, headers=headers, timeout=30)
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"  [Zavenir search] Graph API error: {e}")
        return []

    raw_emails = resp.json().get("value", [])
    print(f"  [Zavenir search] {len(raw_emails)} email(s) found across all folders.")

    emails = []
    for item in raw_emails:
        sender_info  = item.get("from", {}).get("emailAddress", {})
        emails.append({
            "email_id":        item.get("id", ""),
            "received_date":   item.get("receivedDateTime", ""),
            "subject":         item.get("subject", "(No subject)"),
            "sender_name":     sender_info.get("name", "Unknown"),
            "sender_email":    sender_info.get("address", "Unknown"),
            "body_preview":    item.get("bodyPreview", ""),
            "body_content":    item.get("body", {}).get("content", ""),
            "body_type":       item.get("body", {}).get("contentType", "text"),
            "is_read":         item.get("isRead", False),
            "has_attachments": item.get("hasAttachments", False),
            "importance":      item.get("importance", "normal"),
        })
    return emails


# ===========================================================================
# MAIN PIPELINE
# ===========================================================================

def run_pipeline(max_emails: int = 10) -> dict:
    """
    Run the full Zavenir Daubert email pipeline.

    Parameters:
        max_emails — how many emails to fetch from Outlook (keep low for testing)

    Returns:
        A dict with:
            records        — list of extracted CRM row dicts
            emails_fetched — total emails fetched from Outlook
            zavenir_found  — how many of those matched the Zavenir sender filter
    """

    print("=" * 65)
    print("  ZAVENIR DAUBERT PIPELINE")
    print(f"  Sender filter: {SENDER_FILTER}")
    print("  Filter -> Attach -> Clean -> Extract -> Save")
    print("=" * 65)

    # ------------------------------------------------------------------
    # Step 1: Authenticate and search all folders for Zavenir emails
    # Uses Graph API $search so emails in archive/subfolders are found.
    # ------------------------------------------------------------------
    print("\n[Step 1] Searching all Outlook folders for Zavenir emails...")
    token  = get_access_token()
    emails = _search_zavenir_emails(token, max_results=max_emails)

    if not emails:
        print("  No emails found. Check Outlook connection or search index.")
        return {"records": [], "emails_fetched": 0, "zavenir_found": 0}

    print(f"  Found {len(emails)} email(s) matching 'tarora@zavenir.com'.")

    # ------------------------------------------------------------------
    # Step 2: Filter for Zavenir emails only
    # ------------------------------------------------------------------
    print(f"\n[Step 2] Filtering for sender: {SENDER_FILTER}...")
    zavenir_emails = [e for e in emails if _is_zavenir_email(e)]
    skipped = len(emails) - len(zavenir_emails)

    if skipped:
        print(f"  {skipped} email(s) skipped (not from Zavenir).")
    if not zavenir_emails:
        print("  No Zavenir emails found in this batch.")
        return {"records": [], "emails_fetched": len(emails), "zavenir_found": 0}

    print(f"  {len(zavenir_emails)} Zavenir email(s) found.\n")

    # ------------------------------------------------------------------
    # Step 3: Process each Zavenir email
    # ------------------------------------------------------------------
    records     = []
    failed      = 0

    for i, email in enumerate(zavenir_emails, start=1):
        subject = email.get("subject", "(No subject)")
        sender  = email.get("sender_email", "")

        print(f"[{i}/{len(zavenir_emails)}] {subject[:55]}")
        print(f"           From: {sender}")

        # Wrap each email in try/except — one bad email never stops the run
        try:

            # --- Attachment text extraction ---
            # Many product enquiries carry specs, quantities, or delivery dates
            # inside an attached PDF, Excel, or Word file. Appending that text
            # to the body before AI extraction prevents NULL fields.
            if email.get("has_attachments"):
                print("           Attachments: detected — downloading...")
                att_list  = get_email_attachments(token, email["email_id"])
                att_texts = []

                for att in att_list:
                    att_text = extract_text_from_attachment(att["name"], att["bytes"])
                    if att_text:
                        att_texts.append(f"[Attachment: {att['name']}]\n{att_text}")

                if att_texts:
                    combined_att = "\n\n".join(att_texts)
                    email["body_content"] = (
                        email.get("body_content", "")
                        + "\n\n--- ATTACHMENT TEXT ---\n"
                        + combined_att
                    )
                    total_chars = sum(len(t) for t in att_texts)
                    print(
                        f"           Attachments: {len(att_texts)}/{len(att_list)} "
                        f"extracted, {total_chars} chars appended to body"
                    )
                elif att_list:
                    print(
                        f"           Attachments: {len(att_list)} downloaded but "
                        "no text extracted (scanned image or unsupported format)"
                    )

            # --- Clean email body for AI ---
            # prepare_email_for_ai() strips HTML, removes excess whitespace,
            # and formats the email as: SUBJECT / FROM / DATE / body
            email_text = email_parser.prepare_email_for_ai(email)

            # --- AI extraction ---
            print("           Extracting commercial fields with Groq AI...")
            extracted = extract_zavenir_record(email_text)

            if not extracted or not any(v for v in extracted.values()):
                print("           WARNING: AI returned empty extraction — skipping")
                failed += 1
                continue

            # --- Assemble the full CRM record ---
            # System-filled fields are set here; AI fields come from extracted dict.
            req_id = _make_req_id(email.get("email_id", ""))

            record = {
                "req_id":        req_id,
                "status":        "New",
                "received_date": email.get("received_date", "")[:10],
                "sender_email":  email.get("sender_email", ""),
                "email_subject": email.get("subject", ""),
            }
            record.update(extracted)    # merge in all AI-extracted fields

            print(
                f"           -> customer={record.get('customer') or '(unknown)'}"
                f" | product={record.get('product_category') or '(unknown)'}"
                f" | qty={record.get('quantity') or '?'} "
                f"{record.get('quantity_unit') or ''}"
            )

            records.append(record)

        except Exception as e:
            failed += 1
            print(f"           ERROR: {type(e).__name__}: {e} — logged, continuing")

        print()

    if failed:
        print(f"  {failed} email(s) failed extraction — see output above.")

    return {
        "records":        records,
        "emails_fetched": len(emails),
        "zavenir_found":  len(zavenir_emails),
    }


# ===========================================================================
# SENDER FILTER HELPER
# ===========================================================================

def _is_zavenir_email(email: dict) -> bool:
    """
    Return True if this email originated from tarora@zavenir.com.

    Two checks, in order:
      1. sender_email field matches directly — catches emails sent by Tania
         directly to the monitored inbox.
      2. body_content contains the address — catches emails where Saral
         forwarded Tania's email; the original From: header appears in the
         body text even though sender_email shows Saral's address.
    """
    # Check 1: direct sender match
    if email.get("sender_email", "").lower() == SENDER_FILTER.lower():
        return True

    # Check 2: forwarded-email body scan
    body = email.get("body_content", "")
    return bool(_ZAVENIR_EMAIL_RE.search(body))


# ===========================================================================
# REQ_ID GENERATION
# ===========================================================================

def _make_req_id(email_id: str) -> str:
    """
    Generate a unique record ID in the same format as the GET Global pipeline.

    Format: REQ-YYYYMMDD-XXXXXX-01
      YYYYMMDD — today's date
      XXXXXX   — first 6 hex chars of MD5 hash of the email_id (uppercase)
      01       — always 01 for Zavenir (one record per email, no multi-role split)

    The MD5 hash is deterministic: re-running on the same email always produces
    the same req_id, which makes Excel and Supabase deduplication reliable.
    """
    id_hash  = hashlib.md5(email_id.encode()).hexdigest()[:6].upper() if email_id else "000000"
    date_str = datetime.date.today().strftime("%Y%m%d")
    return f"REQ-{date_str}-{id_hash}-01"


# ===========================================================================
# SAVE — EXCEL
# ===========================================================================

def _save_to_excel(records: list) -> int:
    """
    Save Zavenir records to data/zavenir_crm.xlsx.

    - Creates the file (and data/ folder) if they do not exist yet.
    - Uses the FIELDS list from configs/zavenir_daubert.py as the column schema.
    - Deduplicates on req_id — skips any record whose req_id already exists.
    - Returns the number of new rows actually written.
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Build a DataFrame from the records list, filling any missing schema
    # columns with None so the Excel file always has all columns in the right order.
    new_df = pd.DataFrame(records)
    for col in FIELDS:
        if col not in new_df.columns:
            new_df[col] = None
    new_df = new_df[FIELDS]   # enforce column order from schema

    if EXCEL_PATH.exists():
        existing_df  = pd.read_excel(EXCEL_PATH, dtype=str).fillna("")
        existing_ids = set(existing_df["req_id"].astype(str))
        truly_new    = new_df[~new_df["req_id"].astype(str).isin(existing_ids)]
        combined_df  = pd.concat([existing_df, truly_new], ignore_index=True)
        saved_count  = len(truly_new)
    else:
        combined_df = new_df
        saved_count = len(new_df)

    combined_df.to_excel(EXCEL_PATH, index=False)
    _format_excel()
    print(f"Excel: {saved_count} new record(s) saved -> {EXCEL_PATH.name}")
    return saved_count


def _format_excel():
    """Apply dark-header formatting to zavenir_crm.xlsx (matches GET Global style)."""
    wb = load_workbook(EXCEL_PATH)
    ws = wb.active

    header_fill = PatternFill("solid", fgColor="1F3864")
    header_font = Font(color="FFFFFF", bold=True)

    for cell in ws[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(wrap_text=True)

    ws.freeze_panes = "A2"

    for col in ws.columns:
        max_len = max((len(str(c.value)) for c in col if c.value), default=10)
        ws.column_dimensions[col[0].column_letter].width = min(max_len + 4, 40)

    wb.save(EXCEL_PATH)


# ===========================================================================
# SAVE — SUPABASE
# ===========================================================================

def _save_to_supabase(records: list) -> int:
    """
    Upsert Zavenir records into the zavenir_requirements Supabase table.

    Uses req_id as the conflict key — running the pipeline twice on the same
    email will update the existing row rather than creating a duplicate.
    Returns the number of records successfully upserted.
    """
    if not supabase:
        print("  Supabase not connected — cloud save skipped.")
        return 0

    print(f"\nPushing {len(records)} record(s) to Supabase ({SUPABASE_TABLE})...")
    saved = 0

    for record in records:
        # Build the Supabase row — keys must exactly match the table column names
        # in scripts/create_zavenir_table.sql.
        sb_row = {
            "req_id":           record.get("req_id"),
            "customer":         record.get("customer"),
            "industry_segment": record.get("industry_segment"),
            "product_category": record.get("product_category"),
            "product_brand":    record.get("product_brand"),
            "quantity":         record.get("quantity"),
            "quantity_unit":    record.get("quantity_unit"),
            "location":         record.get("location"),
            "delivery_date":    record.get("delivery_date"),
            "status":           record.get("status", "New"),
            "received_date":    record.get("received_date"),
            "sender_email":     record.get("sender_email"),
            "email_subject":    record.get("email_subject"),
            "email_summary":    record.get("email_summary"),
            "next_action":      record.get("next_action"),
            "llm_confidence":   _safe_float(record.get("llm_confidence")),
        }

        # Drop None values so Supabase does not overwrite existing data with NULL
        # on a re-run where only some fields changed.
        sb_row = {k: v for k, v in sb_row.items() if v is not None}

        try:
            supabase.table(SUPABASE_TABLE).upsert(
                sb_row, on_conflict="req_id"
            ).execute()
            print(f"   Supabase saved: {record.get('email_subject', 'no subject')[:55]}")
            saved += 1
        except Exception as e:
            print(f"   Supabase save failed for {record.get('req_id', '?')}: {e}")

    print("Supabase sync complete.")
    return saved


def save_records(records: list) -> dict:
    """
    Save all records to Excel and Supabase.
    Returns dict with excel_saved and supabase_saved counts.
    """
    if not records:
        print("  No records to save.")
        return {"excel_saved": 0, "supabase_saved": 0}

    excel_saved    = _save_to_excel(records)
    supabase_saved = _save_to_supabase(records)

    return {"excel_saved": excel_saved, "supabase_saved": supabase_saved}


# ===========================================================================
# UTILITY
# ===========================================================================

def _safe_float(value):
    """Convert llm_confidence to float, return None on failure."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


# ===========================================================================
# ENTRY POINT
# ===========================================================================

if __name__ == "__main__":

    pipeline_result = run_pipeline(max_emails=50)

    records        = pipeline_result["records"]
    emails_fetched = pipeline_result["emails_fetched"]
    zavenir_found  = pipeline_result["zavenir_found"]

    print(f"[Step 3] Saving {len(records)} record(s) to Excel + Supabase...")
    save_result = save_records(records)

    print()
    print("=" * 65)
    print("  ZAVENIR RUN SUMMARY")
    print("=" * 65)
    print(f"  Emails fetched          : {emails_fetched}")
    print(f"  Zavenir emails found    : {zavenir_found}")
    print(f"  Records extracted       : {len(records)}")
    print(f"  Saved to Excel          : {save_result['excel_saved']}")
    print(f"  Saved to Supabase       : {save_result['supabase_saved']}")
    if EXCEL_PATH.exists():
        print(f"\n  Open: {EXCEL_OUTPUT}")
