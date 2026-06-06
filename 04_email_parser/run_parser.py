# run_parser.py  —  Phase 13 (full error handling added)
#
# PURPOSE: Main entry point for the CRM pipeline. Ties all phases together:
#   0. Edge case preprocessing — strip HTML + Fw: chains, detect language (Phase 12)
#   1. Fetch emails from Outlook (Phase 3 — email_reader)
#   2a. ML classifier gate — label + confidence (Phase 10)
#   2b. Tier 3 LLM classifier — for emails where ML confidence < 0.75 (Phase 13 — NEW)
#        If both tiers uncertain → flag for human review, treat as relevant
#   3. Detect whether each email is a follow-up or new requirement (Phase 9)
#   4a. NEW REQUIREMENT: full 55-field AI extraction → multi-role rows → dedup → Excel
#   4b. FOLLOW-UP: match existing record → extract update fields → patch row (Phase 9)
#   5. Semantic duplicate detection before saving any new row (Phase 13 — NEW)
#   6. All failures and low-confidence records → review queue (Phase 6)
#
# ERROR HANDLING SUMMARY (Phase 13):
#   Graph API 401: email_reader.py silently refreshes token and retries once
#   Graph API 5xx/429: utils/retry.py exponential backoff (2s → 4s → 8s → give up)
#   Groq API failure: retry_api_call in extractor.py; None returned → logged + queued
#   ML uncertain: Tier 3 LLM classification → human review if still uncertain
#   Semantic duplicate: blocked (>= 80% match) or flagged for review (60-79%)
#   Any exception: try/except per email; pipeline continues to next email

import sys
import datetime
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "03_outlook"))
sys.path.insert(0, str(PROJECT_ROOT / "04_email_parser"))
sys.path.insert(0, str(PROJECT_ROOT / "05_classifier"))
sys.path.insert(0, str(PROJECT_ROOT / "06_data_storage"))
sys.path.insert(0, str(PROJECT_ROOT / "08_advanced"))

from email_reader import fetch_emails
from utils.auth import get_access_token
from utils.pipeline_logger import log_failure, add_to_review_queue, get_review_queue_count
from config.fields import CONFIDENCE_REVIEW_THRESHOLD
import parser as email_parser
from extractor import extract_fields, build_multi_role_rows
from storage import save_records, save_to_excel, update_record, CRM_FILE_PATH
from followup_matcher import is_followup_email, find_best_match
from followup_extractor import extract_followup_fields, FOLLOWUP_TYPE_TO_STATUS
from email_classifier import classify_email, load_model, train_classifier, MODEL_PATH
from psl_splitter import detect_psls, augment_llm_rows
from tier3_classifier import classify_with_llm, TIER3_CONFIDENCE_THRESHOLD
from edge_case_handler import preprocess_email, get_edge_case_summary
from duplicate_detector import find_semantic_duplicate

GROQ_MODEL = "llama-3.3-70b-versatile"

# Labels that mean "do not process — route elsewhere or drop"
_SKIP_LABELS = {"irrelevant", "financial", "sensitive", "confidential"}


def run_pipeline(max_emails=5):
    """
    Full pipeline: Outlook → ML classify → detect type → AI extract → save or update.

    Parameters:
        max_emails — how many emails to process (keep low during testing)

    Returns:
        A flat list of NEW CRM row dicts created this run.
        Follow-up updates are saved directly to Excel (not returned in this list).
    """

    print("=" * 65)
    print("  CRM PIPELINE — Phase 13 (Full Error Handling)")
    print("  Preprocess -> Classify (ML+T3) -> Dedup -> Extract -> Save")
    print("=" * 65)

    # Load the ML model once here so we don't reload it inside the loop for every email.
    # If no model file exists, auto-train it now from the training CSV.
    print("\n[Step 0] Loading ML email classifier...")
    ml_bundle = load_model()
    if ml_bundle is None:
        print("  No trained model found — training now from data/training_emails.csv...")
        train_classifier()
        ml_bundle = load_model()
    if ml_bundle:
        print(f"  ML model loaded. ({ml_bundle.get('n_samples', '?')} training samples)")
    else:
        print("  WARNING: ML model could not be loaded or trained — classifier will be skipped.")

    # Step 1: Auth + fetch emails
    print("\n[Step 1] Fetching emails from Outlook...")
    token  = get_access_token()
    emails = fetch_emails(token, max_emails=max_emails, folder="inbox")

    if not emails:
        print("  No emails fetched. Check your Outlook connection.")
        return []

    print(f"  Fetched {len(emails)} email(s).\n")

    # Step 2: Load existing CRM data once — needed for follow-up matching
    # We load it here rather than inside the loop so we don't re-read the file
    # for every email (which would be slow if there are many emails to process).
    print("[Step 2] Loading existing CRM data for follow-up matching...")
    crm_df = pd.DataFrame()
    if CRM_FILE_PATH.exists():
        crm_df = pd.read_excel(CRM_FILE_PATH, engine="openpyxl", dtype=str).fillna("")
        print(f"  Loaded {len(crm_df)} existing record(s) from {CRM_FILE_PATH.name}")
    else:
        print("  No existing CRM file found — all emails will be treated as new records.")

    print()

    # Step 3: Route each email to the correct processing branch
    crm_rows          = []    # New records to save at the end
    total_new         = 0
    total_updated     = 0
    failed_count      = 0
    review_count      = 0
    ml_skipped        = 0
    tier3_calls       = 0    # how many times Tier 3 LLM was invoked
    duplicates_blocked = 0   # rows blocked as definite duplicates
    possible_dups      = 0   # rows flagged as possible duplicates

    for i, email in enumerate(emails, start=1):
        subject = email.get("subject", "(No subject)")
        sender  = email.get("sender_email", "")
        body    = email.get("body_content", "")

        print(f"[{i}/{len(emails)}] {subject[:55]}")
        print(f"         From: {sender}")

        # Wrap every email in try/except — one bad email never crashes the run
        try:

            # --- Phase 12: Edge case preprocessing ---
            # Strip HTML + forwarding headers, recover original client sender,
            # detect language, flag attachments. All downstream steps see the
            # cleaned body and the real sender — not Saral's forwarding wrapper.
            email = preprocess_email(email)
            ec_summary = get_edge_case_summary(email)
            if ec_summary:
                print(f"         Edge cases: {ec_summary}")

            # --- TIER 2: ML classification gate (Phase 10) ---
            # Classify the email BEFORE spending Groq API tokens on it.
            # This catches irrelevant, financial, sensitive, and confidential emails
            # early so we don't waste API calls or pollute the CRM.
            if ml_bundle:
                ml_result   = classify_email(email, model_bundle=ml_bundle)
                ml_label    = ml_result["label"]
                ml_conf     = ml_result["confidence"]
                needs_tier3 = ml_result["needs_review"]
                final_label = ml_label   # may be overridden by Tier 3 below

                # Tier 3 default (used in skip-reason even if Tier 3 is not called)
                t3 = {"label": ml_label, "confidence": ml_conf, "reason": ""}

                print(f"         ML: {ml_label:<15} confidence {ml_conf:.0%}"
                      + (" [routing to Tier 3]" if needs_tier3 else ""))

                if needs_tier3:
                    # --- TIER 3: LLM-based classification (Phase 13) ---
                    # ML confidence was below threshold — ask Groq for a second opinion
                    # before deciding to skip or proceed. Much cheaper (~100 tokens) than
                    # a full extraction, and prevents both false skips and false extractions.
                    tier3_calls += 1
                    print("         Tier 3: asking Groq to classify this uncertain email...")
                    t3 = classify_with_llm(email)
                    print(f"         Tier 3: {t3['label']:<15} confidence {t3['confidence']:.0%}"
                          + (f" — {t3['reason']}" if t3.get("reason") else ""))

                    if t3["confidence"] >= TIER3_CONFIDENCE_THRESHOLD:
                        # Tier 3 is confident enough to override the ML label
                        final_label = t3["label"]
                    else:
                        # Both tiers uncertain — flag for human review but treat as relevant
                        # (safe default: process and review, rather than silently drop)
                        reason = (
                            f"Classification uncertain after 2 tiers | "
                            f"ML: {ml_label} {ml_conf:.0%} | "
                            f"Tier 3: {t3['label']} {t3['confidence']:.0%}"
                        )
                        add_to_review_queue(email, reason=reason)
                        review_count += 1
                        print("         Both tiers uncertain — flagged for review, treating as relevant.")

                # Skip or flag if the final label is non-relevant
                if final_label in _SKIP_LABELS:
                    if final_label == "irrelevant":
                        print(f"         SKIPPED: classified as irrelevant")
                    else:
                        # sensitive / financial / confidential — route to review queue
                        confidence_source = (
                            f"Tier 3 {t3['confidence']:.0%}" if needs_tier3
                            else f"ML {ml_conf:.0%}"
                        )
                        reason = f"{final_label} ({confidence_source})"
                        add_to_review_queue(email, reason=reason)
                        review_count += 1
                        print(f"         FLAGGED: {reason} — added to review queue")
                    ml_skipped += 1
                    print()
                    continue    # skip to the next email — don't extract or store

            # --- ROUTE: is this a follow-up or a new requirement? ---
            followup = is_followup_email(subject, body)

            if followup:
                print("         Type: FOLLOW-UP — searching for matching record...")
                result = _process_followup(email, crm_df)

                if result == "updated":
                    total_updated += 1
                elif result == "fallback":
                    # No match found — fall through to the new-record path below
                    print("         No match — falling back to new record path.")
                    followup = False
                else:
                    # Extraction failed — log it
                    reason = "Follow-up extraction failed after retries"
                    log_failure(email, reason=reason)
                    add_to_review_queue(email, reason=reason)
                    failed_count += 1

            if not followup:
                print("         Type: NEW REQUIREMENT — running full 55-field extraction...")
                new_rows = _process_new_requirement(email)

                if new_rows:
                    # --- Phase 13: semantic duplicate detection ---
                    # storage.py deduplicates on email_id (same email re-run).
                    # Here we also catch DIFFERENT emails that describe the same
                    # requirement (same client + role sent from a different account
                    # or via a different email chain).
                    deduped_rows = []
                    for row in new_rows:
                        dup = find_semantic_duplicate(row, crm_df)
                        if dup["is_duplicate"]:
                            # Very high similarity — almost certainly the same requirement.
                            # Block the save so the CRM stays clean.
                            duplicates_blocked += 1
                            print(f"         DUPLICATE BLOCKED: {dup['explanation']}")
                            log_failure(
                                email,
                                reason=f"Semantic duplicate of {dup['req_id_match']}: {dup['explanation']}"
                            )
                        elif dup["is_possible"]:
                            # Moderate similarity — could be a duplicate, could be a new
                            # requirement from the same client. Save it but flag for review.
                            possible_dups += 1
                            print(f"         POSSIBLE DUPLICATE: {dup['explanation']} (flagged)")
                            add_to_review_queue(
                                row,
                                reason=f"Possible duplicate ({dup['similarity_score']:.0%} match): {dup['explanation']}"
                            )
                            review_count += 1
                            deduped_rows.append(row)
                        else:
                            deduped_rows.append(row)

                    new_rows = deduped_rows

                if new_rows:
                    crm_rows.extend(new_rows)
                    total_new += len(new_rows)

                    for row in new_rows:
                        designation = row.get("designation") or "(role unknown)"
                        headcount   = row.get("headcount")   or ""
                        client      = row.get("client_name") or "(client unknown)"
                        psl         = row.get("psl_categories") or ""
                        hc_str      = f" x{headcount}" if headcount else ""
                        psl_str     = f" [{psl}]" if psl else ""
                        print(f"         -> {designation}{hc_str}{psl_str} | {client}")

                        # Flag rows that need human review
                        conf    = row.get("llm_confidence", "")
                        missing = str(row.get("missing_fields_flag", "")).strip()
                        reasons = []

                        if isinstance(conf, (int, float)) and conf < CONFIDENCE_REVIEW_THRESHOLD:
                            reasons.append(f"low confidence ({conf:.2f} < {CONFIDENCE_REVIEW_THRESHOLD})")
                        if missing:
                            reasons.append(f"missing fields: {missing}")

                        if reasons:
                            add_to_review_queue(row, reason=" | ".join(reasons))
                            review_count += 1
                            print(f"           [review queue] {' | '.join(reasons)}")

                else:
                    reason = "AI extraction failed after retries — requires manual entry"
                    log_failure(email, reason=reason)
                    add_to_review_queue(email, reason=reason)
                    failed_count += 1
                    print(f"         FAILED: extraction returned None — logged to failed_emails.log")

        except Exception as e:
            # Unexpected error — log it and keep going
            reason = f"{type(e).__name__}: {e}"
            log_failure(email, reason=reason)
            add_to_review_queue(email, reason=f"Pipeline exception: {reason}")
            failed_count += 1
            print(f"         ERROR: {reason} — logged, continuing pipeline")

        print()

    print(f"  Pipeline complete.")
    print(f"  Emails fetched      : {len(emails)}")
    if ml_skipped:
        print(f"  ML filtered out     : {ml_skipped} (irrelevant/sensitive/financial/confidential)")
    if tier3_calls:
        print(f"  Tier 3 invocations  : {tier3_calls} (low-confidence ML emails routed to LLM)")
    print(f"  Emails processed    : {len(emails) - failed_count - ml_skipped} / {len(emails)}")
    print(f"  New records created : {total_new}")
    print(f"  Follow-ups updated  : {total_updated}")
    if duplicates_blocked:
        print(f"  Duplicates blocked  : {duplicates_blocked} — see data/failed_emails.log")
    if possible_dups:
        print(f"  Possible duplicates : {possible_dups} — flagged in review_queue.xlsx")
    if failed_count:
        print(f"  Failed (logged)     : {failed_count} — see data/failed_emails.log")
    if review_count:
        print(f"  Review queue        : {review_count} added — see data/review_queue.xlsx")

    return crm_rows


# ---------------------------------------------------------------------------
# BRANCH A — follow-up email processing
# ---------------------------------------------------------------------------

def _process_followup(email, crm_df):
    """
    Handle a follow-up email: find the matching requirement and update it.

    Returns:
        "updated"  — match found, fields updated successfully
        "fallback" — no match found (caller will treat this email as a new record)
        "failed"   — match found but AI extraction failed
    """
    # Try to find the existing requirement this follow-up relates to
    req_id, match_score = find_best_match(email, crm_df)

    if not req_id:
        # No confident match — caller will fall back to the new-record path
        return "fallback"

    # Match found — extract the follow-up update fields from the email body
    email_text = email_parser.prepare_email_for_ai(email)
    fu_fields  = extract_followup_fields(email_text)

    if not fu_fields:
        return "failed"

    # Build the dict of fields to update in the existing record
    field_updates = _build_update_dict(fu_fields, match_score)

    result = update_record(req_id, field_updates)

    if result["updated"]:
        return "updated"
    else:
        return "failed"


# ---------------------------------------------------------------------------
# BRANCH B — new requirement processing (Phase 11: PSL augmentation added)
# ---------------------------------------------------------------------------

def _process_new_requirement(email):
    """
    Handle a new requirement email: full 55-field extraction + multi-role expansion
    + PSL keyword augmentation (Phase 11).

    Steps:
      1. Run PSL keyword scan on the raw subject + body (free, no API cost).
      2. Send the cleaned email to Groq AI for 55-field extraction.
      3. Expand the AI output into one row per detected role.
      4. Augment with any PSLs the AI missed, using the keyword scan results.

    Returns:
        List of CRM row dicts (LLM rows first, PSL-only rows appended), or [] on failure.
    """
    subject = email.get("subject", "")
    body    = email.get("body_content", "")

    # Phase 11: scan for PSL keywords BEFORE calling the LLM.
    # This is instant (no API call) and tells us what to expect from the AI.
    detected_psls = detect_psls(subject, body)
    if detected_psls:
        print(f"         PSL scan: {detected_psls}")

    # Phase 8: LLM extraction — 55 fields, multi-role aware
    email_text = email_parser.prepare_email_for_ai(email)
    extracted  = extract_fields(email_text)

    if not extracted:
        return []

    llm_rows = build_multi_role_rows(email, extracted)

    # Phase 11: add rows for any PSL the LLM did not already produce a row for
    if detected_psls:
        llm_rows = augment_llm_rows(email, llm_rows, detected_psls)

    return llm_rows


# ---------------------------------------------------------------------------
# HELPER — build the field update dict from follow-up extraction output
# ---------------------------------------------------------------------------

def _build_update_dict(fu_fields, match_score):
    """
    Convert the follow-up extraction result into a dict of fields to patch
    on the existing CRM record.

    Only includes fields with actual values (skips nulls and empty strings).
    Also sets status, is_follow_up, and appends a processing_log entry.

    Parameters:
        fu_fields   — dict returned by extract_followup_fields()
        match_score — the 0–100 confidence score from the matcher

    Returns:
        dict of {field_name: new_value} to pass to update_record()
    """
    followup_type = fu_fields.get("followup_type", "general_update")
    now_str       = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    updates = {}

    # Update the requirement stage (e.g., "CVs Shared with Client")
    stage = fu_fields.get("requirement_stage")
    if stage:
        updates["requirement_stage"] = stage

    # Update status based on follow-up type
    # (e.g., "mobilized" → "Done", "cancelled" → "On Hold", most others → "In Progress")
    new_status = FOLLOWUP_TYPE_TO_STATUS.get(followup_type)
    if new_status:
        updates["status"] = new_status

    # Section 5 fulfillment fields — only update if the AI found a value
    fulfillment_fields = [
        "cvs_requested", "cvs_shared", "profiles_shortlisted",
        "interview_date", "interview_outcome",
        "candidate_selected", "candidate_mobilized",
    ]
    for field in fulfillment_fields:
        val = fu_fields.get(field)
        if val is not None and str(val).strip() not in ("", "null"):
            updates[field] = val

    # Update the communication fields with the follow-up's summary and next action
    summary = fu_fields.get("email_summary")
    if summary:
        updates["email_summary"] = summary

    next_action = fu_fields.get("next_action")
    if next_action:
        updates["next_action"] = next_action

    # Always mark this record as having a follow-up
    updates["is_follow_up"] = "Yes"

    # Append a new timestamped line to the audit log
    # The update_record() function will concatenate this with the existing log
    updates["processing_log"] = (
        f"{now_str} | Phase 9 follow-up | type: {followup_type} "
        f"| match score: {match_score}/100 | {GROQ_MODEL}"
    )

    return updates


def print_crm_preview(crm_rows):
    """
    Print a formatted preview of extracted CRM rows in the terminal.
    Shows key fields from all 55 columns to confirm extraction quality.
    """
    if not crm_rows:
        print("  No CRM rows to display.")
        return

    print()
    print("=" * 65)
    print(f"  CRM EXTRACTION RESULTS — {len(crm_rows)} record(s)")
    print("=" * 65)

    preview_fields = [
        ("req_id",            "Req ID"),
        ("client_name",       "Client"),
        ("client_country",    "Country"),
        ("designation",       "Role"),
        ("headcount",         "Headcount"),
        ("psl_categories",    "PSL"),
        ("location",          "Location"),
        ("mobilization_date", "Mob. Date"),
        ("rates",             "Rates"),
        ("deadline",          "Deadline"),
        ("requirement_stage", "Stage"),
        ("urgency",           "Urgency"),
        ("llm_confidence",    "AI Confidence"),
        ("missing_fields_flag","Missing Fields"),
        ("role_index",        "Role Index"),
    ]

    for i, row in enumerate(crm_rows, start=1):
        sender = row.get("sender_email", "")
        date   = row.get("received_date", "")
        print(f"\n--- Record {i}: {sender} | {date} ---")

        for field_key, field_label in preview_fields:
            value = row.get(field_key, "")
            if value:
                value_str = str(value)
                if len(value_str) > 55:
                    value_str = value_str[:55] + "..."
                print(f"  {field_label:<18} {value_str}")

        # Show summary on its own wrapped line
        summary = row.get("email_summary", "")
        if summary:
            print(f"\n  Summary:")
            words = summary.split()
            line  = "    "
            for word in words:
                if len(line) + len(word) > 70:
                    print(line)
                    line = "    " + word + " "
                else:
                    line += word + " "
            if line.strip():
                print(line)

    print()
    print("=" * 65)
    print(f"  {len(crm_rows)} CRM record(s) ready to save.")
    print("=" * 65)


# ---------------------------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    crm_rows = run_pipeline(max_emails=5)

    if crm_rows:
        print_crm_preview(crm_rows)

        print("\n[Step 3] Saving to Excel + Supabase...")
        result = save_records(crm_rows)   # writes Excel AND pushes each row to Supabase

        print(f"\n  Done.")
        print(f"  Saved:      {result['saved']} new record(s)")
        print(f"  Duplicates: {result['skipped_duplicates']} skipped")
        print(f"  Total rows: {result['total_rows']} in CRM file")
        print(f"\n  Open: data\\crm_data.xlsx")
