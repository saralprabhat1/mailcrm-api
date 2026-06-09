# edge_case_handler.py — Phase 12
#
# PURPOSE: Detect and handle email edge cases BEFORE AI extraction.
# Every email passes through preprocess_email() in run_parser.py to:
#   1. Strip HTML and remove Outlook forwarding headers so the AI sees only
#      the core message — not Saral's "From: / Sent: / To: / Subject:" wrapper.
#   2. Recover the original client sender from Fw: chains (critical for CRM
#      records — the REAL client, not Saral who forwarded the email).
#   3. Detect language (Arabic, French, etc.) so the AI prompt can include
#      a language hint for accurate extraction of MENA region emails.
#   4. Flag emails with attachments so the AI prompt and human reviewers know
#      to check Outlook manually (PDF/Word extraction is a Phase 13 task).
#
# WHY THIS EXISTS: All 33 real emails fetched are Fw: from Saral's inbox.
# Without stripping, the AI sees Saral's email in the From: field and his
# forwarding headers as body content — both wrong for CRM field extraction.

import re
import sys
from pathlib import Path

# Optional: langdetect gives accurate multi-language detection (pip install langdetect).
# If not installed, fall back to Arabic Unicode range heuristic — sufficient for MENA.
try:
    from langdetect import detect as _ld_detect, LangDetectException
    _LANGDETECT_AVAILABLE = True
except ImportError:
    _LANGDETECT_AVAILABLE = False
    LangDetectException = Exception   # dummy class so the except clause still compiles

# Import strip_html from parser.py — already written, no need to duplicate it here
_SELF_DIR = Path(__file__).parent
sys.path.insert(0, str(_SELF_DIR.parent / "04_email_parser"))
from parser import strip_html

# Import footer stripper from the classifier — strips confidentiality boilerplate
# before the body reaches the ML classifier, Tier 3 LLM, or Groq extraction.
sys.path.insert(0, str(_SELF_DIR.parent / "05_classifier"))
from email_classifier import strip_legal_footer


# ---------------------------------------------------------------------------
# COMPILED PATTERNS (built once at import — re.compile is expensive in a loop)
# ---------------------------------------------------------------------------

# Separator lines Outlook inserts when forwarding:
#   ________________________________   (underscores)
#   -----Original Message-----          (dashes + label + dashes)
_SEPARATOR_LINE = re.compile(
    r"^(?:_{4,}|-{4,}[^\n]{0,60}-{0,4})\s*$",
    re.MULTILINE | re.IGNORECASE
)

# The forwarding header block: From / Sent (or Date) / To / Subject
# Group 1 captures the From: value so we can extract the original sender email.
# MULTILINE so ^ and $ work per-line; each header field is on its own line.
_FWD_HEADER = re.compile(
    r"^From[ \t]*:[ \t]*(.+?)[ \t]*$\n"          # From: (group 1 = from value)
    r"(?:(?:Sent|Date)[ \t]*:.+?\n)?"             # Sent: or Date: (optional)
    r"(?:(?:Sent|Date)[ \t]*:.+?\n)?"             # sometimes appears twice in re-forwards
    r"To[ \t]*:.+?\n"                             # To: (required)
    r"(?:Cc[ \t]*:.+?\n)?"                        # Cc: (optional)
    r"Subject[ \t]*:.+?(?:\n|$)",                 # Subject: (required)
    re.MULTILINE | re.IGNORECASE
)

# Pull an email address out of  "Name <email@domain.com>"  or a bare email
_ANGLE_EMAIL = re.compile(r"<([^@\s<>]+@[^@\s<>]+)>")
_BARE_EMAIL  = re.compile(r"\b([A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[a-zA-Z]{2,})\b")

# Subject prefixes that always mean a forwarded / replied email
_FW_SUBJECT = re.compile(r"^\s*(?:fw|fwd)\s*:", re.IGNORECASE)

# Arabic Unicode block U+0600–U+06FF
# If more than 5 % of printable chars are Arabic → classify as Arabic
_ARABIC_RE = re.compile(r"[؀-ۿ]")

# ISO 639-1 code → human-readable name (MENA-focused; covers oil & gas region)
_LANG_NAMES = {
    "en": "English",
    "ar": "Arabic",
    "fr": "French",
    "es": "Spanish",
    "de": "German",
    "nl": "Dutch",
    "ru": "Russian",
    "pt": "Portuguese",
    "tr": "Turkish",
    "fa": "Persian",
    "ur": "Urdu",
    "zh-cn": "Chinese",
    "zh-tw": "Chinese",
}


# ---------------------------------------------------------------------------
# PUBLIC — main entry point
# ---------------------------------------------------------------------------

def preprocess_email(email_record):
    """
    Returns an enriched shallow copy of the email dict.
    The original dict is NEVER modified.

    Keys added / updated:
        body_content      — HTML stripped + forwarding headers removed (core message)
        body_type         — set to "text" (stripping already done here)
        _is_forwarded     — True if Fw:/Fwd: detected in subject or body
        _original_sender  — email address from first Fw: From: header (may be "")
        _thread_depth     — number of forward/reply layers found in the body
        _language         — detected ISO 639-1 code, e.g. "ar"
        _language_name    — human-readable name, e.g. "Arabic"
        _edge_cases       — list of tags, e.g. ["forwarded", "ar", "attachments"]
    """
    email      = dict(email_record)   # shallow copy — only top-level keys modified
    edge_cases = []

    # --- Step 1: Normalise body to plain text ---
    plain_body = _to_plain_text(email)

    # --- Step 2: Strip forwarding chain, recover core message and original sender ---
    is_fwd, original_sender, original_sender_name, depth, core_body = _strip_forwarding(
        email.get("subject", ""), plain_body
    )
    email["body_content"]          = core_body
    email["body_type"]             = "text"
    email["_is_forwarded"]         = is_fwd
    email["_original_sender"]      = original_sender
    email["_original_sender_name"] = original_sender_name
    email["_thread_depth"]         = depth

    if is_fwd:
        edge_cases.append("forwarded")

    # --- Step 3: Detect language of the core message ---
    lang_code, lang_name = _detect_lang(core_body)
    email["_language"]      = lang_code
    email["_language_name"] = lang_name
    if lang_code != "en":
        edge_cases.append(lang_code)

    # --- Step 4: Flag attachments ---
    # Actual attachment text extraction requires downloading from Graph API (Phase 13).
    # For now, add a note to the body so the AI and human reviewer are both aware.
    has_attach = str(email.get("has_attachments", "false")).lower() in ("true", "1", "yes")
    if has_attach:
        edge_cases.append("attachments")
        email["body_content"] += (
            "\n\n[ATTACHMENT PRESENT: This email has one or more file attachments "
            "(possibly CVs or requirement documents) that were not auto-extracted. "
            "Parse the email body only; manual review of attachments is required.]"
        )

    # --- Step 5: Strip legal disclaimer footer ---
    # Confidentiality boilerplate appended by mail servers pollutes the body
    # and causes false-positive "confidential" labels in the ML classifier.
    # Strip it here so every downstream consumer (ML, Tier 3, Groq) sees clean text.
    email["body_content"] = strip_legal_footer(email["body_content"])

    email["_edge_cases"] = edge_cases
    return email


def get_edge_case_summary(email_record):
    """
    Returns a short human-readable string describing detected edge cases.
    Returns "" if none.

    Example: "forwarded (2 layers) from ahmed@aramco.com | language: Arabic"
    """
    ec    = email_record.get("_edge_cases", [])
    parts = []

    if "forwarded" in ec:
        depth = email_record.get("_thread_depth", 1)
        orig  = email_record.get("_original_sender", "")
        s     = f"forwarded ({depth} layer{'s' if depth != 1 else ''})"
        if orig:
            s += f" from {orig}"
        parts.append(s)

    lang = email_record.get("_language", "en")
    if lang != "en":
        parts.append(f"language: {email_record.get('_language_name', lang)}")

    if "attachments" in ec:
        parts.append("attachments present")

    return " | ".join(parts)


# ---------------------------------------------------------------------------
# PRIVATE HELPERS
# ---------------------------------------------------------------------------

def _to_plain_text(email):
    """Return plain-text body. Strips HTML via parser.strip_html() if body_type is 'html'."""
    body = email.get("body_content", "")
    if email.get("body_type", "text") == "html":
        return strip_html(body)
    return body.strip()


def _strip_forwarding(subject, plain_body):
    """
    Detect and remove Outlook forwarding headers from a plain-text email body.

    Returns:
        is_forwarded    — bool
        original_sender — email address from the first From: header, or ""
        thread_depth    — number of forwarding layers detected
        core_body       — text with forwarding headers removed (core message only)
    """
    fwd_in_subject = bool(_FW_SUBJECT.match(subject))
    blocks         = _find_fwd_blocks(plain_body)
    depth          = len(blocks)

    if not fwd_in_subject and depth == 0:
        return False, "", "", 0, plain_body

    if depth == 0:
        # Subject says Fw: but no header blocks found in body — return body unchanged
        return True, "", "", 0, plain_body

    # blocks[0] = (block_start, header_end, from_email, from_name)
    _, first_end, original_sender, original_sender_name = blocks[0]

    # Core body = text after the first forwarding header, up to the next layer (if any)
    if depth > 1:
        second_start = blocks[1][0]
        core_body    = plain_body[first_end:second_start].strip()
    else:
        core_body = plain_body[first_end:].strip()

    return True, original_sender, original_sender_name, depth, core_body


def _find_fwd_blocks(text):
    """
    Find all forwarding header blocks (From/Sent/To/Subject) in plain text.

    Returns list of (block_start, header_end, from_email, from_name) tuples,
    sorted by document position. block_start is pulled back to include any
    preceding separator line (underscores / dashes).
    """
    blocks = []
    for m in _FWD_HEADER.finditer(text):
        from_value  = m.group(1)
        from_email  = _extract_email(from_value)
        from_name   = _extract_name(from_value)
        block_start = _find_separator_before(text, m.start())
        blocks.append((block_start, m.end(), from_email, from_name))
    blocks.sort(key=lambda x: x[0])
    return blocks


def _find_separator_before(text, header_start, look_back=150):
    """
    Look back up to look_back characters before header_start for a separator line.
    Returns its start position if found, otherwise returns header_start.
    """
    window   = text[max(0, header_start - look_back): header_start]
    last_sep = None
    for m in _SEPARATOR_LINE.finditer(window):
        last_sep = m   # keep the last separator in the window

    if last_sep is not None:
        offset = max(0, header_start - look_back)
        return offset + last_sep.start()
    return header_start


def _extract_email(from_value):
    """Extract email address from a From: line value (may be 'Name <email>' or bare)."""
    m = _ANGLE_EMAIL.search(from_value)
    if m:
        return m.group(1).lower().strip()
    m = _BARE_EMAIL.search(from_value)
    if m:
        return m.group(1).lower().strip()
    return ""


def _extract_name(from_value):
    """
    Extract display name from a From: line value.
    'Ahmed Al-Rashid <ahmed@aramco.com>'  ->  'Ahmed Al-Rashid'
    'ahmed@aramco.com'                    ->  ''
    """
    # Name is everything before the '<email>' part
    m = _ANGLE_EMAIL.search(from_value)
    if m:
        name = from_value[:m.start()].strip().strip('"').strip("'")
        return name
    # No angle-bracket form — the whole value is the email (no name)
    return ""


def _detect_lang(text):
    """
    Detect language of text. Returns (iso_code, human_name).
    Defaults to ("en", "English") when text is too short or detection fails.
    """
    if not text or len(text.strip()) < 30:
        return "en", "English"

    # Fast Arabic check using Unicode range — no library needed
    printable = [c for c in text if not c.isspace()]
    if printable:
        arabic_ratio = len(_ARABIC_RE.findall(text)) / len(printable)
        if arabic_ratio > 0.05:
            return "ar", "Arabic"

    # Full language detection if langdetect is installed
    if _LANGDETECT_AVAILABLE:
        try:
            code = _ld_detect(text[:500])   # 500 chars is sufficient for detection
            name = _LANG_NAMES.get(code, code.upper())
            return code, name
        except LangDetectException:
            pass

    return "en", "English"


# ---------------------------------------------------------------------------
# QUICK SELF-TEST (run: python edge_case_handler.py)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    OUTLOOK_FW_BODY = """Hi Saral,

Please check the below requirement.

________________________________
From: Ahmed Al-Rashid <ahmed.alrashid@aramco.com>
Sent: Wednesday, June 4, 2026 10:30 AM
To: Saral Prabhat <saral.prabhat@getglobalgroup.com>
Subject: Manpower Requirement - Drilling Engineers - KSA

Dear Team,

We require 3 Senior Drilling Engineers for our Khurais project.
Location: Dammam, Saudi Arabia
Start date: 1 August 2026
Duration: 12 months
Rate: $900/day

Regards,
Ahmed Al-Rashid
Drilling Operations Manager
Saudi Aramco

________________________________
From: Saeed Al-Mansoori <saeed@adnoc.ae>
Sent: Tuesday, June 3, 2026
To: Ahmed Al-Rashid
Subject: RE: Manpower Requirement

Earlier thread content here.
"""

    sample_email = {
        "subject":        "Fw: Manpower Requirement - Drilling Engineers - KSA",
        "sender_email":   "saral.prabhat@getglobalgroup.com",
        "body_content":   OUTLOOK_FW_BODY,
        "body_type":      "text",
        "has_attachments": "false",
        "received_date":  "2026-06-05",
    }

    print("=== Edge Case Handler — Self Test ===\n")
    enriched = preprocess_email(sample_email)

    print(f"Is forwarded    : {enriched['_is_forwarded']}")
    print(f"Original sender : {enriched['_original_sender']}")
    print(f"Thread depth    : {enriched['_thread_depth']}")
    print(f"Language        : {enriched['_language']} ({enriched['_language_name']})")
    print(f"Edge cases      : {enriched['_edge_cases']}")
    print(f"\nEdge case summary: {get_edge_case_summary(enriched)}")
    print(f"\nCore body extracted:")
    print("-" * 50)
    print(enriched["body_content"])
    print("-" * 50)

    # Test Arabic detection
    arabic_email = dict(sample_email)
    arabic_email["body_content"] = "نحتاج إلى مهندسين للحفر في المنطقة الشرقية"
    arabic_email["body_type"]    = "text"
    arabic_enriched = preprocess_email(arabic_email)
    print(f"\nArabic test — language: {arabic_enriched['_language']} ({arabic_enriched['_language_name']})")

    print("\nAll tests done.")
