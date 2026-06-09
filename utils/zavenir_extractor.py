# utils/zavenir_extractor.py
# PURPOSE: Groq-based AI extractor for the Zavenir Daubert pipeline.
#
# Given a cleaned email text, this file sends it to Groq and extracts the
# fields defined in configs/zavenir_daubert.py into a flat dict.
#
# KEY DIFFERENCES from the GET Global extractor (04_email_parser/extractor.py):
#   - One record per email — no multi-role expansion
#   - Fields are product/commercial (quantity, product_brand, delivery_date)
#     instead of manpower/HR (designation, headcount, mobilization_date)
#   - Product categories and industry segments replace PSL categories
#
# SAFETY RULE: never crashes the pipeline.
#   Any exception → log a warning → return a partial dict with what was found.

import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# Add project root to sys.path so we can import from configs/ and utils/
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from utils.retry import retry_api_call
from utils.json_utils import parse_json_response
from configs.zavenir_daubert import PRODUCT_CATEGORIES, INDUSTRY_SEGMENTS

# Load .env from project root — same file used by the GET Global pipeline
load_dotenv(dotenv_path=PROJECT_ROOT / ".env")

logger = logging.getLogger(__name__)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL   = "llama-3.3-70b-versatile"

# ---------------------------------------------------------------------------
# SYSTEM PROMPT
# ---------------------------------------------------------------------------

_PRODUCT_CATEGORIES_STR = " | ".join(PRODUCT_CATEGORIES)
_INDUSTRY_SEGMENTS_STR  = " | ".join(INDUSTRY_SEGMENTS)

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


# ---------------------------------------------------------------------------
# MAIN EXTRACTION FUNCTION
# ---------------------------------------------------------------------------

def extract_zavenir_record(email_text: str) -> dict:
    """
    Send a cleaned email text to Groq and extract Zavenir CRM fields.

    Parameters:
        email_text — cleaned plain-text email (subject + sender + date + body),
                     as produced by parser.prepare_email_for_ai()

    Returns:
        A flat dict with keys matching the AI-extracted fields in FIELDS
        (configs/zavenir_daubert.py). System-filled fields (req_id, status,
        received_date, sender_email, email_subject) are NOT set here — the
        pipeline runner adds those.

        Returns a partial dict (with whatever was extracted) on any error.
        Never raises an exception.
    """
    if not GROQ_API_KEY:
        logger.error("GROQ_API_KEY not set — cannot extract Zavenir record.")
        return _empty_record()

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type":  "application/json",
    }

    payload = {
        "model":           GROQ_MODEL,
        "temperature":     0.1,        # low temperature = consistent, deterministic output
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": email_text},
        ],
    }

    import requests  # imported here to mirror extractor.py's scoping pattern

    def _call_groq():
        r = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=30)
        r.raise_for_status()
        return r

    try:
        response = retry_api_call(_call_groq, label="Groq API (Zavenir)")
        raw_json = response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        logger.warning(f"Zavenir extractor: Groq call failed — {e}")
        print(f"  [Zavenir] Groq API error: {e}")
        return _empty_record()

    # parse_json_response handles malformed JSON gracefully — returns {} on failure
    extracted = parse_json_response(raw_json)
    if not extracted:
        logger.warning("Zavenir extractor: Groq returned empty or unparseable JSON.")
        print("  [Zavenir] WARNING: AI returned empty JSON — partial record created.")
        return _empty_record()

    # Build the output dict, mapping AI field names to our FIELDS schema.
    # _safe() coerces blank strings to None so the CRM stores clean NULLs.
    record = {
        "customer":         _safe(extracted.get("customer")),
        "industry_segment": _validate(extracted.get("industry_segment"), INDUSTRY_SEGMENTS),
        "product_category": _validate(extracted.get("product_category"), PRODUCT_CATEGORIES),
        "product_brand":    _safe(extracted.get("product_brand")),
        "quantity":         _safe_number(extracted.get("quantity")),
        "quantity_unit":    _safe(extracted.get("quantity_unit")),
        "location":         _safe(extracted.get("location")),
        "delivery_date":    _safe(extracted.get("delivery_date")),
        "email_summary":    _safe(extracted.get("email_summary")),
        "next_action":      _safe(extracted.get("next_action")),
        "llm_confidence":   _safe_float(extracted.get("llm_confidence")),
    }

    conf = record.get("llm_confidence") or 0.0
    print(f"  [Zavenir] Extraction complete. "
          f"customer={record.get('customer') or '(unknown)'} | "
          f"product={record.get('product_category') or '(unknown)'} | "
          f"confidence={conf:.0%}")

    return record


# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------

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
    }


def _safe(value) -> object:
    """Return None if value is None, empty string, or the literal 'null'."""
    if value is None:
        return None
    s = str(value).strip()
    return None if s in ("", "null", "None") else s


def _safe_float(value) -> object:
    """Parse a confidence score to float, or return None."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _safe_number(value) -> object:
    """Parse quantity to a number (int preferred, float if needed), or None."""
    if value is None:
        return None
    try:
        f = float(value)
        return int(f) if f == int(f) else f
    except (TypeError, ValueError):
        return None


def _validate(value, valid_list: list) -> object:
    """
    Return value if it matches (case-insensitively) an entry in valid_list,
    otherwise return None.  Prevents the AI from inventing categories.
    """
    if value is None:
        return None
    v = str(value).strip()
    for item in valid_list:
        if item.lower() == v.lower():
            return item   # return the canonical casing from our list
    return None           # AI returned something not in our list — discard it
