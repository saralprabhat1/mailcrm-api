# utils/zavenir_extractor.py
# PURPOSE: Groq-based AI extractor for the Zavenir Daubert pipeline.
#
# Given a cleaned email text (or a stitched thread), sends it to Groq and
# extracts the fields defined in configs/clients/zavenir.py.
#
# KEY DIFFERENCES from the GET Global extractor (04_email_parser/extractor.py):
#   - Thread-aware: fetches full conversation via Graph API before extraction
#   - Multi-product: one Groq call can return N records for N products in thread
#   - Fields are product/commercial (quantity, product_brand, delivery_date)
#     instead of manpower/HR (designation, headcount, mobilization_date)
#
# Phase 17 additions:
#   fetch_conversation(access_token, conversation_id) → list of email dicts
#   stitch_thread(email_list)                         → single stitched string
#   extract_zavenir_thread(thread_text)               → list of record dicts
#
# SAFETY RULE: never crashes the pipeline.
#   Any exception → log a warning → return empty/partial dict.

import os
import re
import sys
import html
import logging
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from utils.retry import retry_api_call
from utils.json_utils import parse_json_response
from configs.clients.zavenir import PRODUCT_CATEGORIES, INDUSTRY_SEGMENTS, SENDER_FILTER

load_dotenv(dotenv_path=PROJECT_ROOT / ".env")

logger = logging.getLogger(__name__)

GROQ_API_KEY   = os.getenv("GROQ_API_KEY")
GROQ_API_URL   = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL     = "llama-3.3-70b-versatile"
GRAPH_BASE_URL = "https://graph.microsoft.com/v1.0"

# Regexes used by stitch_thread to clean raw HTML from Graph API responses
_HTML_TAG_RE = re.compile(r"<[^>]+>", re.DOTALL)
_WS_RE       = re.compile(r"[ \t]{4,}")

# ---------------------------------------------------------------------------
# Phase 18 — forwarded sender + assignment detection regexes
# ---------------------------------------------------------------------------

# A "From:" line inside a forwarded header block (case-insensitive)
_FROM_LINE_RE = re.compile(r"^\s*from\s*:\s*(.+?)\s*$", re.IGNORECASE)

# A line that confirms the From: line above is part of a forward header,
# not a random "From" mention elsewhere in the body.
_FORWARD_CTX_RE = re.compile(r"^\s*(sent|date|to|subject)\s*:", re.IGNORECASE)

# "Name <email@domain.com>"
_NAME_EMAIL_ANGLE_RE = re.compile(r"^(.*?)<\s*([^<>\s]+@[^<>\s]+)\s*>\s*$")

# Older Outlook style: "Name [mailto:email@domain.com]"
_NAME_EMAIL_MAILTO_RE = re.compile(r"^(.*?)\[mailto:\s*([^\]\s]+@[^\]\s]+)\s*\]\s*$", re.IGNORECASE)

# Bare email address with no display name
_BARE_EMAIL_RE = re.compile(r"^[^\s<>\[\]]+@[^\s<>\[\]]+$")

# Assignment language scanned in the forwarder's note (text above the forward block)
_ASSIGNMENT_PHRASES_RE = re.compile(
    r"please\s+handle|assign(?:ed)?\s+to|over\s+to\s+you|your\s+lead|"
    r"take\s+this|follow[\s\-]?up|kindly\s+handle|please\s+action|"
    r"please\s+take|for\s+your\s+action|requesting\s+you\s+to",
    re.IGNORECASE,
)

# ---------------------------------------------------------------------------
# SYSTEM PROMPTS
# ---------------------------------------------------------------------------

_PRODUCT_CATEGORIES_STR = " | ".join(PRODUCT_CATEGORIES)
_INDUSTRY_SEGMENTS_STR  = " | ".join(INDUSTRY_SEGMENTS)

# Single-email prompt (kept for backward-compatibility / fallback)
SYSTEM_PROMPT = f"""You are a CRM data extraction assistant for a specialty chemicals and lubricants company called Zavenir Daubert.

Your job: read a business email and extract the commercial enquiry fields into a structured JSON object.

CRITICAL RULES:
- Respond with ONLY a valid JSON object. No explanation, no markdown, no code blocks.
- If a field is not found in the email, use null.
- Dates: YYYY-MM-DD format wherever possible.
- quantity must be a number only (e.g. 500). Put the unit (kg, litres, drums, MT) in quantity_unit.

PRODUCT CATEGORY — choose exactly ONE from this list:
{_PRODUCT_CATEGORIES_STR}

INDUSTRY SEGMENT — choose exactly ONE from this list:
{_INDUSTRY_SEGMENTS_STR}

PRODUCT / BRAND NAMES — Zavenir Daubert brands include:
TecPlex | Nox-Rust | Tectyl | Cool Form | SACI | DAUBOND
Extract the brand or product name exactly as stated in the email. If none is named, use null.

OUTPUT FORMAT — return exactly this JSON structure:
{{
  "customer":          "<company name of the buyer>",
  "industry_segment":  "<one value from the INDUSTRY SEGMENT list above>",
  "product_category":  "<one value from the PRODUCT CATEGORY list above>",
  "product_brand":     "<brand or product name, or null>",
  "quantity":          <number, or null>,
  "quantity_unit":     "<kg | litres | drums | MT | units | or as stated, or null>",
  "location":          "<plant, city, or country of delivery, or null>",
  "delivery_date":     "<YYYY-MM-DD, or null>",
  "email_summary":     "<one sentence summary of what is being requested>",
  "next_action":       "<suggested next action for the sales team>",
  "llm_confidence":    <float 0.0–1.0 reflecting how complete the extracted data is>
}}"""

# Thread prompt — used by extract_zavenir_thread()
THREAD_SYSTEM_PROMPT = f"""You are a CRM data extraction assistant for Zavenir Daubert, a specialty chemicals and lubricants company.

You will receive a stitched email thread — multiple emails combined chronologically, each prefixed with [DATE | Sender Name <sender@domain>].
The thread may contain enquiries for MULTIPLE DISTINCT PRODUCTS.

Your job:
1. Extract one CRM record per distinct product enquiry found in the thread.
2. ALSO extract a "conversation_timeline" — a structured, sequential summary of the
   ENTIRE thread (covering ALL messages, not just product details), one line per
   message, in this exact format:
   [Mon D | Sender Name | Company] -> short summary of what they said/requested/confirmed

   - Mon D = short month name + day (e.g. Jun 9), derived from each message's date.
   - Sender Name = the display name from that message's [DATE | Sender Name <email>] prefix.
     If no name is given, use the part of the email before the @ sign.
   - Company = the organisation the sender appears to belong to, inferred from their
     email domain or signature (e.g. "Zavenir" for @zavenir.com addresses, or the
     customer's company name for external senders).
   - summary = one short clause describing the action/request/confirmation in that message.
   - Join all lines with "\\n" (newline) into a single string.
   - Example:
     "[Jun 9 | Rajesh Kumar | Unominda] -> RFQ for X-Clean 2070, 20 Ltr, delivery to Bhiwadi\\n[Jun 9 | Tarul Arora | Zavenir] -> Forwarded to sales team, assigned to Priya\\n[Jun 10 | Priya Sharma | Zavenir] -> Sent quote Rs 850/Ltr, awaiting PO confirmation"

CRITICAL RULES:
- Respond with ONLY a valid JSON object in this exact wrapper: {{"enquiries": [<array of records>], "conversation_timeline": "<string, see above>"}}
- No explanation, no markdown, no code blocks.
- If a field is not found, use null.
- Return an array with ONE entry per distinct product. If only one product, still return an array with one entry.
- Different model numbers or grades of the same brand are DIFFERENT products — create one record per model number (e.g. Nox-Rust 307 and Nox-Rust R-823 are two separate records, not one).
- If the exact same model number appears multiple times in the thread (e.g. price negotiation on the same SKU), use the MOST RECENT values only.
- Dates: YYYY-MM-DD format wherever possible.
- quantity must be a number only. Put the unit in quantity_unit.

PRODUCT CATEGORY — choose exactly ONE from this list:
{_PRODUCT_CATEGORIES_STR}

INDUSTRY SEGMENT — choose exactly ONE from this list:
{_INDUSTRY_SEGMENTS_STR}

PRODUCT / BRAND NAMES — Zavenir Daubert brands include:
TecPlex | Nox-Rust | Tectyl | Cool Form | SACI | DAUBOND
Extract the brand or product name exactly as stated in the email. If none is named, use null.

OUTPUT FORMAT:
{{
  "enquiries": [
    {{
      "customer":          "<company name of the buyer>",
      "industry_segment":  "<one value from the INDUSTRY SEGMENT list>",
      "product_category":  "<one value from the PRODUCT CATEGORY list>",
      "product_brand":     "<brand or product name as stated, or null>",
      "quantity":          <number, or null>,
      "quantity_unit":     "<kg | litres | drums | MT | units | or as stated, or null>",
      "location":          "<plant, city, or country of delivery, or null>",
      "delivery_date":     "<YYYY-MM-DD, or null>",
      "email_summary":     "<one sentence: what product, by whom, from the thread>",
      "next_action":       "<suggested next action for the sales team>",
      "llm_confidence":    <float 0.0–1.0 reflecting how complete the extracted data is>
    }}
  ],
  "conversation_timeline": "<string — sequential thread summary, see above>"
}}"""


# ---------------------------------------------------------------------------
# PHASE 17 — THREAD INTELLIGENCE FUNCTIONS
# ---------------------------------------------------------------------------

def fetch_conversation(access_token: str, conversation_id: str) -> list:
    """
    Fetch all emails in a conversation thread from the Microsoft Graph API.

    Uses $filter=conversationId so it retrieves every message in the thread,
    not just the one that matched the original $search query. Results are
    sorted oldest-first in Python (avoids $orderby complications with $filter).

    Parameters:
        access_token    — valid Microsoft Graph Bearer token
        conversation_id — the conversationId value from any email in the thread

    Returns:
        List of dicts {subject, received_date, sender, body_content},
        oldest-first. Returns [] on any error.
    """
    import requests as _r

    params = {
        "$filter": f"conversationId eq '{conversation_id}'",
        "$top":    "20",
        "$select": "id,subject,receivedDateTime,from,body,bodyPreview",
    }
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type":  "application/json",
    }

    try:
        resp = _r.get(
            f"{GRAPH_BASE_URL}/me/messages",
            params=params,
            headers=headers,
            timeout=30,
        )
        resp.raise_for_status()
    except Exception as e:
        logger.warning(f"fetch_conversation: Graph API error — {e}")
        print(f"  [thread] Graph API error: {e}")
        return []

    items = resp.json().get("value", [])
    items.sort(key=lambda x: x.get("receivedDateTime", ""))   # oldest first

    result = []
    for item in items:
        sender_info = item.get("from", {}).get("emailAddress", {})
        result.append({
            "subject":       item.get("subject", ""),
            "received_date": item.get("receivedDateTime", ""),
            "sender":        sender_info.get("address", "Unknown"),
            "sender_name":   sender_info.get("name", ""),
            "body_content":  item.get("body", {}).get("content", ""),
        })
    return result


def stitch_thread(email_list: list, max_chars: int = 15000) -> str:
    """
    Combine a list of email dicts into a single chronological text block.

    Each email is prefixed with [YYYY-MM-DD | Sender Name <sender@domain>]
    (or just the email if no display name is available) so the AI can track
    the negotiation timeline and attribute each message to a person.
    Total output capped at max_chars.

    Parameters:
        email_list — list of dicts from fetch_conversation(), oldest-first.
                     Expected keys: received_date, sender, sender_name, body_content.
        max_chars  — total character cap for the stitched output.

    Returns:
        Single string with all emails stitched together, ready for Groq.
    """
    parts = []
    for email in email_list:
        date_str = email.get("received_date", "")[:10]   # YYYY-MM-DD
        sender   = email.get("sender", "Unknown")
        name     = (email.get("sender_name") or "").strip()
        who      = f"{name} <{sender}>" if name else sender
        body     = _clean_body(email.get("body_content", ""))
        parts.append(f"[{date_str} | {who}]\n{body}")

    stitched = "\n\n---\n\n".join(parts)
    if len(stitched) > max_chars:
        stitched = stitched[:max_chars] + "\n[... thread truncated ...]"
    return stitched


def _clean_body(text: str) -> str:
    """Strip HTML tags, decode HTML entities, and collapse long runs of whitespace."""
    text = _HTML_TAG_RE.sub(" ", text)
    text = html.unescape(text)
    text = _WS_RE.sub(" ", text)
    return text.strip()


# ---------------------------------------------------------------------------
# PHASE 18 — FORWARDED SENDER + ASSIGNMENT DETECTION
#
# Every Zavenir email arrives forwarded from tarora@zavenir.com. The actual
# customer is named in a "From:" header inside the forwarded block, not in
# the Graph API `from` field (which is Tania's or Saral's address).
#
# These functions operate on cleaned body text WITH line breaks preserved
# (e.g. the output of 04_email_parser/parser.strip_html), since forward
# headers are always multi-line blocks.
# ---------------------------------------------------------------------------

def _parse_from_value(value: str):
    """Parse a 'From:' header value into (name, email). Either may be None."""
    value = value.strip()
    for pattern in (_NAME_EMAIL_ANGLE_RE, _NAME_EMAIL_MAILTO_RE):
        m = pattern.match(value)
        if m:
            name  = m.group(1).strip().strip('"').strip()
            email = m.group(2).strip()
            return (name or None), email
    if _BARE_EMAIL_RE.match(value):
        return None, value
    return (value or None), None


def _find_forward_header_index(lines: list, skip_emails: set = None):
    """
    Find the first 'From:' line that is part of a recognised forward header
    block (followed within 4 lines by a Sent:/Date:/To:/Subject: line).

    skip_emails — From: blocks whose email matches one of these (case-insensitive)
                  are skipped, so the search continues to the next block.

    Returns (index, name, email) of the first matching block, or (None, None, None).
    """
    skip_emails = {e.lower() for e in (skip_emails or set())}
    for i, line in enumerate(lines):
        m = _FROM_LINE_RE.match(line)
        if not m:
            continue
        window = lines[i + 1:i + 5]
        if not any(_FORWARD_CTX_RE.match(w) for w in window):
            continue
        name, email = _parse_from_value(m.group(1))
        if email and email.lower() in skip_emails:
            continue
        return i, name, email
    return None, None, None


def extract_forwarded_sender(text: str):
    """
    Find the original (customer) sender of a forwarded email.

    Scans cleaned body text for a forward header block — a "From:" line
    followed within a few lines by Sent:/Date:/To:/Subject: — skipping any
    block whose email is SENDER_FILTER (tarora@zavenir.com), since that is
    the forwarder, not the customer.

    Returns (name, email) — either may be None if nothing is found.
    """
    if not text:
        return None, None
    lines = text.splitlines()
    _, name, email = _find_forward_header_index(lines, skip_emails={SENDER_FILTER})
    return name, email


def get_forwarder_note(text: str) -> str:
    """
    Return the text written ABOVE the first forwarded header block — the
    forwarder's own note to the recipient(s). Returns the full text if no
    forward header is found.
    """
    if not text:
        return ""
    lines = text.splitlines()
    idx, _, _ = _find_forward_header_index(lines)
    if idx is None:
        return text
    return "\n".join(lines[:idx]).strip()


def detect_assigned_to(forwarder_note: str, to_recipients: list):
    """
    Detect the deal owner (assigned_to) from the forward recipients and the
    forwarder's note.

    to_recipients — list of dicts {"name": ..., "address": ...} from the
                    Graph API toRecipients field of the forwarded email.

    Returns (assigned_to, confidence):
        assigned_to — "Name <email>" (or bare email) of the internal Zavenir
                       recipient, or None if forwarded only to external
                       monitoring (e.g. saral.prabhat@outlook.com).
        confidence  — "high" if an internal recipient AND assignment language
                       were both found, "low" if only the recipient was
                       found, None if assigned_to is None.
    """
    candidate = None
    for recipient in to_recipients or []:
        addr = (recipient.get("address") or "").strip()
        if not addr or addr.lower() == SENDER_FILTER.lower():
            continue
        if addr.lower().endswith("@zavenir.com"):
            name = (recipient.get("name") or "").strip()
            candidate = f"{name} <{addr}>" if name else addr
            break

    if not candidate:
        return None, None

    has_language = bool(_ASSIGNMENT_PHRASES_RE.search(forwarder_note or ""))
    return candidate, ("high" if has_language else "low")


# ---------------------------------------------------------------------------
# EXTRACTION FUNCTIONS
# ---------------------------------------------------------------------------

def extract_zavenir_record(email_text: str) -> dict:
    """
    Send a single cleaned email text to Groq; return one record dict.
    Kept for backward-compatibility. New code should use extract_zavenir_thread.
    """
    if not GROQ_API_KEY:
        logger.error("GROQ_API_KEY not set.")
        return _empty_record()

    import requests as _r

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type":  "application/json",
    }
    payload = {
        "model":           GROQ_MODEL,
        "temperature":     0.1,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": email_text},
        ],
    }

    def _call():
        resp = _r.post(GROQ_API_URL, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        return resp

    try:
        response = retry_api_call(_call, label="Groq API (Zavenir)")
        raw_json = response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        logger.warning(f"Zavenir extractor: Groq call failed — {e}")
        print(f"  [Zavenir] Groq API error: {e}")
        return _empty_record()

    extracted = parse_json_response(raw_json)
    if not extracted:
        print("  [Zavenir] WARNING: AI returned empty JSON — partial record created.")
        return _empty_record()

    record = _build_record(extracted)
    conf   = record.get("llm_confidence") or 0.0
    print(
        f"  [Zavenir] customer={record.get('customer') or '(unknown)'} | "
        f"product={record.get('product_category') or '(unknown)'} | "
        f"confidence={conf:.0%}"
    )
    return record


def extract_zavenir_thread(thread_text: str) -> list:
    """
    Send a stitched email thread to Groq; return one record dict per product.

    Uses THREAD_SYSTEM_PROMPT which instructs the model to return
    {"enquiries": [...]} — one entry per distinct product in the thread.

    Parameters:
        thread_text — output of stitch_thread()

    Returns:
        List of record dicts (same schema as extract_zavenir_record()).
        Returns [_empty_record()] on any error so the pipeline never crashes.
    """
    if not GROQ_API_KEY:
        logger.error("GROQ_API_KEY not set.")
        return [_empty_record()]

    import requests as _r

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type":  "application/json",
    }
    payload = {
        "model":           GROQ_MODEL,
        "temperature":     0.1,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": THREAD_SYSTEM_PROMPT},
            {"role": "user",   "content": thread_text},
        ],
    }

    def _call():
        resp = _r.post(GROQ_API_URL, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        return resp

    try:
        response = retry_api_call(_call, label="Groq API (Zavenir thread)")
        raw_json = response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        logger.warning(f"Zavenir thread extractor: Groq call failed — {e}")
        print(f"  [Zavenir] Groq API error: {e}")
        return [_empty_record()]

    outer = parse_json_response(raw_json)
    if not outer:
        logger.warning("Zavenir thread extractor: Groq returned empty JSON.")
        return [_empty_record()]

    enquiries = outer.get("enquiries", [])
    if not isinstance(enquiries, list) or not enquiries:
        # Groq returned a flat object instead of {"enquiries":[...]} — treat as one record
        enquiries = [outer] if outer else []

    conversation_timeline = _safe(outer.get("conversation_timeline"))

    records = []
    for item in enquiries:
        record = _build_record(item)
        record["conversation_timeline"] = conversation_timeline
        records.append(record)
        conf  = record.get("llm_confidence") or 0.0
        brand = record.get("product_brand") or record.get("product_category") or "(unknown)"
        print(
            f"  [thread] product={brand}"
            f" | customer={record.get('customer') or '(unknown)'}"
            f" | confidence={conf:.0%}"
        )

    return records if records else [_empty_record()]


# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------

def _build_record(raw: dict) -> dict:
    """Map raw Groq output keys to our FIELDS schema, applying type coercion."""
    return {
        "customer":         _safe(raw.get("customer")),
        "industry_segment": _validate(raw.get("industry_segment"), INDUSTRY_SEGMENTS),
        "product_category": _validate(raw.get("product_category"), PRODUCT_CATEGORIES),
        "product_brand":    _safe(raw.get("product_brand")),
        "quantity":         _safe_number(raw.get("quantity")),
        "quantity_unit":    _safe(raw.get("quantity_unit")),
        "location":         _safe(raw.get("location")),
        "delivery_date":    _safe(raw.get("delivery_date")),
        "email_summary":    _safe(raw.get("email_summary")),
        "next_action":      _safe(raw.get("next_action")),
        "llm_confidence":   _safe_float(raw.get("llm_confidence")),
        "conversation_timeline": None,
    }


def _empty_record() -> dict:
    """Return a dict with all AI-extracted fields set to None."""
    return {
        "customer":         None,
        "industry_segment": None,
        "product_category": None,
        "product_brand":    None,
        "quantity":         None,
        "quantity_unit":    None,
        "location":         None,
        "delivery_date":    None,
        "email_summary":    None,
        "next_action":      None,
        "llm_confidence":   None,
        "conversation_timeline": None,
    }


def _safe(value) -> object:
    if value is None:
        return None
    s = str(value).strip()
    return None if s in ("", "null", "None") else s


def _safe_float(value) -> object:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _safe_number(value) -> object:
    if value is None:
        return None
    try:
        f = float(value)
        return int(f) if f == int(f) else f
    except (TypeError, ValueError):
        return None


def _validate(value, valid_list: list) -> object:
    """Return canonical list value if AI output matches (case-insensitive), else None."""
    if value is None:
        return None
    v = str(value).strip()
    for item in valid_list:
        if item.lower() == v.lower():
            return item
    return None
