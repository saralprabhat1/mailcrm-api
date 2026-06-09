# debug_extractor.py  —  Phase 16 diagnostic tool
#
# PURPOSE:
#   Run a single email end-to-end through the GET CRM pipeline and print
#   every stage in full detail. Nothing is saved — read-only debug run.
#
# HOW TO USE:
#   python debug_extractor.py
#
# WHAT IT PRINTS:
#   A. RAW EMAIL      — metadata from Graph API
#   B. CLEANED TEXT   — after parser.py HTML strip (before truncation)
#   C. TRUNCATED INPUT — exactly what gets sent to Groq (3000-char cap)
#   D. GROQ RAW RESPONSE — full JSON string from the API
#   E. PARSED FIELDS  — each of the 39 LLM fields, marking [EMPTY] ones
#   F. CONFIDENCE SCORE
#   G. SUMMARY        — populated vs empty counts

import sys
import os
import re
import requests
from pathlib import Path

# ---- Path setup (mirrors run_parser.py) ------------------------------------
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "03_outlook"))
sys.path.insert(0, str(PROJECT_ROOT / "04_email_parser"))
sys.path.insert(0, str(PROJECT_ROOT / "05_classifier"))
sys.path.insert(0, str(PROJECT_ROOT / "08_advanced"))

from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / ".env")

from utils.auth import get_access_token
from email_reader import fetch_emails, get_email_attachments
from utils.attachment_extractor import extract_text_from_attachment
import parser as email_parser
from edge_case_handler import preprocess_email
from followup_matcher import is_followup_email
from extractor import GROQ_API_KEY, GROQ_API_URL, GROQ_MODEL, SYSTEM_PROMPT
from utils.json_utils import parse_json_response

# ---- Classifier imports (needed to decide which emails are relevant) --------
from email_classifier import classify_email, load_model
from config.fields import CONFIDENCE_REVIEW_THRESHOLD
from tier3_classifier import classify_with_llm

# ---- Print helpers ----------------------------------------------------------

SEP  = "=" * 70
SEP2 = "-" * 70

def header(title):
    print(f"\n{SEP}")
    print(f"  {title}")
    print(SEP)

def section(title):
    print(f"\n{SEP2}")
    print(f"  {title}")
    print(SEP2)

def safe(text):
    """Encode to cp1252 (Windows console), replacing unmappable chars with '?'."""
    if text is None:
        return "(none)"
    return str(text).encode("cp1252", errors="replace").decode("cp1252")


# ---- Main debug flow --------------------------------------------------------

def run_debug():
    print(SEP)
    print("  DEBUG EXTRACTOR  —  Phase 16 single-email diagnostic")
    print("  READ-ONLY: nothing is saved to Excel or Supabase")
    print(SEP)

    # ------------------------------------------------------------------ AUTH
    print("\n[Auth] Authenticating with Microsoft Graph API...")
    token = get_access_token()
    if not token:
        print("  ERROR: Could not get access token. Exiting.")
        return

    # ------------------------------------------------------------------ FETCH
    # Fetch 50 emails so we have enough depth to find a GET Global requirement.
    print("\n[Fetch] Fetching 50 most recent emails from inbox...")
    emails = fetch_emails(token, max_emails=50)

    if not emails:
        print("  ERROR: No emails returned. Exiting.")
        return

    print(f"  {len(emails)} emails fetched.")

    # ------------------------------------------------------------------ FIND TARGET
    # Load the ML classifier once.
    print("\n[Classifier] Loading ML classifier...")
    ml_bundle = load_model()

    target = None  # the email we will run through the full debug

    # Subject keywords that suggest a genuine GET Global manpower requirement.
    TARGET_KEYWORDS = [
        "fishing supervisor", "amo technician", "callout",
        "hiring", "requirement", "rfq", "manpower", "position",
        "mobilization", "vacancy", "cv", "profile",
    ]

    # Internal/own-company domains — emails FROM these are outbound replies, not inbound RFQs.
    # We pull EXCLUDED_DOMAINS from config so we don't hardcode getglobalgroup.com here.
    from config.email_filters import EXCLUDED_DOMAINS
    INTERNAL_DOMAINS = set(d.lower() for d in EXCLUDED_DOMAINS)
    INTERNAL_DOMAINS.add("getglobalgroup.com")   # pilot forwarding domain

    print("\n[Filter] Scanning emails — prefer inbound client RFQs with keyword match...")
    print(f"         Keywords:        {', '.join(TARGET_KEYWORDS)}")
    print(f"         Internal domains:{', '.join(sorted(INTERNAL_DOMAINS))}")
    print()

    candidates = []   # list of (score, reason, processed_email)

    for email in emails:
        subject      = email.get("subject", "")
        sender_email = email.get("sender_email", "")
        subj_lower   = subject.lower()
        sender_domain = sender_email.split("@")[-1].lower() if "@" in sender_email else ""

        # Hard-exclude Zavenir — it has its own pipeline
        if "zavenir.com" in sender_domain:
            print(f"  SKIP (zavenir):      {safe(subject[:65])}")
            continue

        # Must contain at least one target keyword in the subject
        matched_keyword = next(
            (kw for kw in TARGET_KEYWORDS if kw in subj_lower), None
        )
        if not matched_keyword:
            print(f"  SKIP (no keyword):   {safe(subject[:65])}")
            continue

        # Phase 12: preprocess (strips HTML, recovers original sender)
        processed = preprocess_email(email)

        # Skip Re: replies — these are our own team's responses, not client RFQs.
        # Fw: is fine — Saral forwards inbound client emails.
        stripped_subj = re.sub(r"^(re:\s*)+", "", subj_lower).strip()
        if subj_lower.startswith("re:"):
            print(f"  SKIP (Re: reply):    {safe(subject[:65])}")
            continue

        # Score this candidate:
        #   +2  if sender is external (inbound from client — most valuable)
        #   +1  if sender is internal (Fw: of client email — still useful)
        #   +body_len  so longer emails (more RFQ detail) rank higher
        is_internal_sender = any(
            sender_domain == d or sender_domain.endswith("." + d)
            for d in INTERNAL_DOMAINS
        )
        direction_score = 0 if is_internal_sender else 2
        body_len = len(processed.get("body_content", ""))
        score = direction_score + body_len

        reason_parts = []
        reason_parts.append("external" if not is_internal_sender else "internal-fwd")
        reason_parts.append(f"keyword={matched_keyword!r}")
        reason_parts.append(f"body={body_len}c")
        reason = ", ".join(reason_parts)

        print(f"  CANDIDATE (score={score:6}): {safe(subject[:55])}  [{reason}]")
        candidates.append((score, reason, matched_keyword, processed))

    if not candidates:
        print("\n  No matching email found in the 50 most recent.")
        print("  Try adding more keywords or increasing max_emails in this script.")
        return

    # Pick the highest-scoring candidate (longest body, preferring external senders)
    candidates.sort(key=lambda x: x[0], reverse=True)
    best_score, best_reason, best_keyword, target = candidates[0]

    # Log ML verdict for the selected email — informational only, does not filter
    if ml_bundle:
        ml_result = classify_email(target, model_bundle=ml_bundle)
        ml_label  = ml_result["label"]
        ml_conf   = ml_result["confidence"]
    else:
        ml_label, ml_conf = "unknown", 0.0

    print()
    print(f"  SELECTED (best of {len(candidates)} candidate(s)):")
    print(f"    Subject:         {safe(target.get('subject', ''))}")
    print(f"    Sender:          {safe(target.get('sender_email', ''))}")
    print(f"    Body length:     {len(target.get('body_content', ''))} chars")
    print(f"    Reason:          {best_reason}")
    print(f"    ML verdict:      {ml_label} ({ml_conf:.0%})  <-- debug note: classifier bypassed")

    # ================================================================ STAGE A
    header("A. RAW EMAIL — metadata from Graph API")
    print(f"  Subject:         {safe(target.get('subject', '(none)'))}")
    print(f"  Sender:          {safe(target.get('sender_name', ''))} <{safe(target.get('sender_email', ''))}>")
    print(f"  Date:            {target.get('received_date', '')[:10]}")
    print(f"  Has attachments: {target.get('has_attachments', False)}")
    raw_body = target.get("body_content", "")
    print(f"  Body length:     {len(raw_body)} chars (raw, before HTML strip)")
    print(f"  Body type:       {target.get('body_type', 'unknown')}")

    # ================================================================ ATTACHMENT EXTRACTION
    # Mirroring what run_parser.py does: if has_attachments, download and append text.
    if target.get("has_attachments"):
        section("ATTACHMENT EXTRACTION")
        email_id = target.get("email_id", "")
        try:
            attachments = get_email_attachments(token, email_id)
            att_texts = []
            for att in attachments:
                att_name  = att.get("name", "unknown")
                att_bytes = att.get("bytes")          # key is "bytes" — already base64-decoded
                if not att_bytes:
                    print(f"  SKIP (no bytes): {att_name}  [keys: {list(att.keys())}]")
                    continue
                print(f"  Extracting: {att_name} ({len(att_bytes):,} raw bytes)")
                extracted = extract_text_from_attachment(att_name, att_bytes)
                char_count = len(extracted)
                print(f"  Result:     {char_count} chars extracted")
                if extracted:
                    att_texts.append(f"\n\n--- ATTACHMENT: {att_name} ---\n{extracted}")
            if att_texts:
                target["body_content"] = target.get("body_content", "") + "".join(att_texts)
                print(f"\n  Body after attachment append: {len(target['body_content'])} chars total")
            else:
                print("  No text extracted from any attachment.")
        except Exception as e:
            print(f"  WARNING: Attachment extraction failed: {e}")

    # ================================================================ STAGE B
    header("B. CLEANED TEXT — after parser.py HTML strip (NO truncation)")

    # prepare_email_for_ai() always truncates at 3000 chars, so we reproduce
    # the cleaning step manually here to show the full pre-truncation length.
    body_content = target.get("body_content", "")
    body_type    = target.get("body_type", "text")

    sender_name  = (
        target.get("_original_sender_name")
        or target.get("sender_name", "")
    )
    sender_email_addr = (
        target.get("_original_sender")
        or target.get("sender_email", "")
    )

    if body_type == "html":
        from parser import strip_html
        clean_body = strip_html(body_content)
    else:
        clean_body = body_content.strip()

    lang_code = target.get("_language", "en")
    lang_note = ""
    if lang_code != "en":
        lang_name = target.get("_language_name", lang_code)
        lang_note = f"[NOTE: This email contains {lang_name} content. Extract all fields.]\n"

    full_text = (
        f"SUBJECT: {target.get('subject', '')}\n"
        f"FROM: {sender_name} <{sender_email_addr}>\n"
        f"DATE: {target.get('received_date', '')[:10]}\n"
        f"---\n"
        f"{lang_note}"
        f"{clean_body}"
    )

    print(f"  Full cleaned length: {len(full_text)} chars")
    print()
    print(safe(full_text))

    # ================================================================ STAGE C
    header("C. TRUNCATED INPUT — exactly what gets sent to Groq")

    MAX_CHARS = 12000   # mirrors parser.py — Phase 16 increased from 3000 to handle ZIP attachments
    if len(full_text) > MAX_CHARS:
        truncated_text = full_text[:MAX_CHARS] + "\n\n[... email truncated ...]"
        print(f"  TRUNCATED from {len(full_text)} -> {MAX_CHARS} chars  "
              f"({len(full_text) - MAX_CHARS} chars cut off)")
    else:
        truncated_text = full_text
        print(f"  No truncation needed ({len(full_text)} chars, under {MAX_CHARS} limit)")

    print(f"  Final input length: {len(truncated_text)} chars")
    print()
    print(safe(truncated_text))

    # ================================================================ STAGE D
    header("D. GROQ RAW RESPONSE — full JSON string from the API")

    if not GROQ_API_KEY:
        print("  ERROR: GROQ_API_KEY not set in .env. Cannot call API.")
        return

    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system",  "content": SYSTEM_PROMPT},
            {"role": "user",    "content": f"Extract all CRM fields from this email:\n\n{truncated_text}"},
        ],
        "temperature": 0.1,
        "response_format": {"type": "json_object"},
        "max_tokens": 2500,
    }

    headers_groq = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type":  "application/json",
    }

    print("  Calling Groq API...")
    try:
        response = requests.post(GROQ_API_URL, headers=headers_groq, json=payload, timeout=45)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        status = e.response.status_code if e.response is not None else "?"
        print(f"  ERROR: Groq API HTTP {status}: {e}")
        return
    except requests.exceptions.RequestException as e:
        print(f"  ERROR: Groq network error: {e}")
        return

    raw_json_str = response.json()["choices"][0]["message"]["content"]

    print(f"  Raw response length: {len(raw_json_str)} chars")
    print()
    print(safe(raw_json_str))

    # ================================================================ STAGE E
    header("E. PARSED FIELDS — all 39 LLM fields, [EMPTY] shown explicitly")

    extracted = parse_json_response(raw_json_str)

    if not extracted:
        print("  ERROR: JSON parsing failed. Raw string above was not valid JSON.")
        return

    # All top-level scalar fields (excluding 'roles' array — handled separately)
    SCALAR_FIELDS = [
        "category", "client_name", "client_country", "client_sector",
        "contact_person", "contact_email", "contact_phone", "client_ref_number",
        "project_name", "location", "mobilization_date", "duration",
        "contract_type", "work_schedule", "nationality_preference",
        "deadline", "urgency", "requirement_stage",
        "cvs_requested", "cvs_shared", "profiles_shortlisted",
        "interview_date", "interview_outcome", "candidate_selected", "candidate_mobilized",
        "email_summary", "next_action", "language_detected",
        "llm_confidence", "missing_fields_flag",
    ]

    populated_scalar = 0
    empty_scalar     = 0

    print("  -- Common fields --")
    for field in SCALAR_FIELDS:
        val = extracted.get(field)
        is_empty = val is None or val == "" or val == "null"
        tag = "[EMPTY]" if is_empty else ""
        print(f"  {field:<28} {safe(str(val)):<45} {tag}")
        if is_empty:
            empty_scalar += 1
        else:
            populated_scalar += 1

    # Roles array
    roles = extracted.get("roles") or []
    print(f"\n  -- Roles array ({len(roles)} role(s) detected) --")

    ROLE_FIELDS = [
        "designation", "headcount", "psl_category",
        "rates", "rates_currency",
        "technical_requirements", "certifications", "experience_years",
    ]

    populated_role = 0
    empty_role     = 0

    for ri, role in enumerate(roles, 1):
        print(f"\n  Role {ri}:")
        for field in ROLE_FIELDS:
            val = role.get(field)
            is_empty = val is None or val == "" or val == "null"
            tag = "[EMPTY]" if is_empty else ""
            print(f"    {field:<26} {safe(str(val)):<45} {tag}")
            if is_empty:
                empty_role += 1
            else:
                populated_role += 1

    # ================================================================ STAGE F
    header("F. CONFIDENCE SCORE")
    conf = extracted.get("llm_confidence")
    if conf is not None:
        try:
            pct = float(conf) * 100
            bar_len = int(pct / 5)
            bar = "[" + "#" * bar_len + "." * (20 - bar_len) + "]"
            print(f"  llm_confidence = {conf}  ({pct:.0f}%)  {bar}")
        except (ValueError, TypeError):
            print(f"  llm_confidence = {conf}  (could not convert to float)")
    else:
        print("  llm_confidence = [EMPTY]")

    missing_flag = extracted.get("missing_fields_flag", "")
    if missing_flag:
        print(f"  missing_fields_flag = {safe(str(missing_flag))}")
    else:
        print("  missing_fields_flag = (none flagged by AI)")

    # ================================================================ STAGE G
    header("G. SUMMARY")

    total_scalar = populated_scalar + empty_scalar
    total_role   = populated_role   + empty_role
    total_all    = total_scalar + total_role
    populated_all = populated_scalar + populated_role

    print(f"  Common fields:  {populated_scalar:>2} populated / {empty_scalar:>2} empty  "
          f"(out of {total_scalar})")
    if roles:
        print(f"  Role fields:    {populated_role:>2} populated / {empty_role:>2} empty  "
              f"(out of {total_role}, across {len(roles)} role(s))")
    print(f"  TOTAL:          {populated_all:>2} populated / {total_all - populated_all:>2} empty  "
          f"(out of {total_all})")

    fill_rate = (populated_all / total_all * 100) if total_all > 0 else 0
    bar_len = int(fill_rate / 5)
    bar = "[" + "#" * bar_len + "." * (20 - bar_len) + "]"
    print(f"  Fill rate:      {fill_rate:.0f}%  {bar}")

    print()
    print("  READ-ONLY RUN COMPLETE — no records were saved.")
    print(SEP)


if __name__ == "__main__":
    run_debug()
