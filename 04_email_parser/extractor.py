# extractor.py  —  Phase 8 (full 55-field extraction + multi-role detection)
#
# PURPOSE:
#   Send a cleaned email to Groq AI and extract ALL CRM fields into a structured dict.
#   If the email mentions multiple job roles, return ONE CRM record per role.
#
# HOW IT WORKS:
#   1. Build a detailed system prompt covering all 39 LLM-extracted fields
#   2. Send the email text to Groq (JSON mode — forces valid JSON back)
#   3. Receive a dict with common fields + a "roles" array (one entry per role found)
#   4. Call build_multi_role_rows() to expand into one CRM dict per role
#   5. Each returned dict maps directly to one row in the 55-column Excel sheet
#
# PHASE HISTORY:
#   Phase 4: 14 fields, single-role output
#   Phase 8: 39 LLM fields + 16 system fields = 55 total, multi-role support

import os
import sys
import hashlib
import datetime
import requests
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path so we can import role_taxonomy from 08_advanced/
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))              # enables: from config.fields import ...
sys.path.insert(0, str(PROJECT_ROOT / "08_advanced"))

from role_taxonomy import get_psl_for_role, detect_roles_in_text
from utils.retry import retry_api_call
from utils.json_utils import parse_json_response

# All reference lists live in config/fields.py — one place to update if they change
from config.fields import (
    VALID_CATEGORIES,
    VALID_SECTORS,
    PSL_CATEGORIES,
    REQUIREMENT_STAGES,
    VALID_CONTRACT_TYPES,
    VALID_URGENCIES,
)

# Load API key from .env at project root
env_path = PROJECT_ROOT / ".env"
load_dotenv(dotenv_path=env_path)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL   = "llama-3.3-70b-versatile"

# ---------------------------------------------------------------------------
# SYSTEM PROMPT — instructs the AI on ALL fields and output structure
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are a CRM data extraction assistant for an oil & gas manpower consultancy.

Your job: read a business email and extract all CRM fields into a structured JSON object.

CRITICAL RULES:
- Respond with ONLY a valid JSON object. No explanation, no markdown, no code blocks.
- If a field is not found in the email, use null.
- Dates: YYYY-MM-DD format wherever possible.
- MULTI-ROLE: If the email mentions multiple job positions, add ONE entry per role in the "roles" array. This is the single most important rule — do not collapse multiple roles into one.

EMAIL CATEGORY — choose exactly ONE:
RFQ | Manpower Request | Client Enquiry | Proposal Request | Deployment Request | Vendor Communication | Internal Communication

CLIENT SECTOR — choose exactly ONE:
NOC | OFS | EPC | EPCI | Government | Other

PSL CATEGORY (per role) — choose exactly ONE from this list:
Artificial Lift | Cementing | Coiled Tubing | Completion | Drilling | Drilling Fluids | EPF | Fishing | FPSO | Fracturing | Geology | HSE | HWO | Maintenance | MLWD | Mud Engineering | Mud Logging | Pipeline & Process | PSCM | Pumping | Reservoir | Rig | Rigless | Slickline | Sub Sea | TCP | Thru Tubing | Training | TRS | Well Completion | Well Head | Well Services | Well Testing | Wireline

REQUIREMENT STAGE — choose exactly ONE (infer from email context):
Requirement Received | Under Internal Review | Service Order Created | CVs Being Sourced | CVs Requested by Client | CVs Shared with Client | Client Reviewing Profiles | Profiles Shortlisted by Client | Interview Scheduled | Interview Completed | Candidate Selected by Client | Offer Negotiation | Mobilization in Progress | Candidate Mobilized | Position Filled | Requirement Cancelled | Requirement On Hold | No Suitable Candidate | Filled by Competitor

URGENCY — choose exactly ONE:
High (deadline within 2 weeks OR mobilization within 1 month)
Medium (deadline 2–6 weeks away)
Low (no deadline mentioned OR deadline > 6 weeks)

CONTRACT TYPE — choose ONE: Contract | Permanent | Secondment | Other

LLM_CONFIDENCE: float 0.0–1.0. How confident are you in the extraction quality?
  1.0 = all key fields clearly stated
  0.7–0.9 = most fields found, some inferred
  <0.7 = many fields missing or ambiguous

MISSING_FIELDS_FLAG: comma-separated list of important fields you could not find (e.g. "deadline, rates, headcount"). Empty string if all key fields were found.

Return this EXACT JSON structure (no extra keys, no markdown):
{
  "category": "...",
  "client_name": "...",
  "client_country": "...",
  "client_sector": "...",
  "contact_person": "...",
  "contact_email": "...",
  "contact_phone": "...",
  "client_ref_number": "...",
  "project_name": "...",
  "location": "...",
  "mobilization_date": "...",
  "duration": "...",
  "contract_type": "...",
  "work_schedule": "...",
  "nationality_preference": "...",
  "deadline": "...",
  "urgency": "...",
  "requirement_stage": "...",
  "cvs_requested": null,
  "cvs_shared": null,
  "profiles_shortlisted": null,
  "interview_date": null,
  "interview_outcome": null,
  "candidate_selected": null,
  "candidate_mobilized": null,
  "email_summary": "...",
  "next_action": "...",
  "language_detected": "...",
  "llm_confidence": 0.9,
  "missing_fields_flag": "...",
  "roles": [
    {
      "designation": "...",
      "headcount": 1,
      "psl_category": "...",
      "rates": "...",
      "rates_currency": "...",
      "technical_requirements": "...",
      "certifications": "...",
      "experience_years": "..."
    }
  ]
}

FIELD GUIDANCE:
- email_summary: 2–3 sentences summarising the email in plain business English.
- next_action: what the BD/AM team should do next (e.g. "Prepare CV pack for 2 Drilling Engineers and submit by 10 June 2025").
- work_schedule: rotation pattern if stated (e.g. "28/28", "14/14", "Monday–Friday").
- rates: include amount, currency and period (e.g. "$800/day", "15,000 USD/month").
- rates_currency: just the currency code (USD, EUR, SAR, AED, OMR, etc.).
- technical_requirements: key skills, software, equipment experience mentioned.
- certifications: required certs (e.g. "IWCF, OPITO BOSIET, H2S").
- experience_years: as stated in email (e.g. "5+", "minimum 8 years").
- client_ref_number: any PO number, tender reference, RFQ number mentioned.
- candidate_mobilized: use "Yes" or "No" if known, otherwise null."""


# ---------------------------------------------------------------------------
# CORE FUNCTION — extract_fields
# ---------------------------------------------------------------------------

def extract_fields(email_text):
    """
    Send an email (as plain text) to Groq AI and return a dict of extracted CRM fields.

    The returned dict contains a "roles" key — a list of per-role dicts.
    Pass this to build_multi_role_rows() to get the final CRM row list.

    Parameters:
        email_text — the cleaned email string from parser.prepare_email_for_ai()

    Returns:
        A dict with all AI-extracted fields (including "roles" array),
        or None if the API call or JSON parsing failed.
    """

    if not GROQ_API_KEY:
        print("  ERROR: GROQ_API_KEY not found in .env file.")
        return None

    print("  Sending email to Groq AI (Phase 8 — full 55-field extraction)...")

    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": f"Extract all CRM fields from this email:\n\n{email_text}"
            }
        ],
        "temperature": 0.1,
        "response_format": {"type": "json_object"},
        "max_tokens": 2500,   # Increased from 800 — multi-role responses can be large
    }

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    # Wrap the API call with retry — 3 attempts, exponential backoff (2s, 4s, 8s)
    # A temporary Groq outage or rate-limit won't fail the whole pipeline run
    def _call_groq():
        r = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=45)
        r.raise_for_status()
        return r

    try:
        response = retry_api_call(_call_groq, label="Groq API")
    except requests.exceptions.HTTPError as e:
        status = e.response.status_code if e.response is not None else "?"
        print(f"  Groq API HTTP {status} error (all retries failed): {e}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"  Groq API network error (all retries failed): {e}")
        return None

    raw_content = response.json()["choices"][0]["message"]["content"]

    extracted = parse_json_response(raw_content)

    if extracted:
        role_count = len(extracted.get("roles") or [])
        print(f"  AI extraction complete. Roles detected: {role_count}")

    return extracted


# ---------------------------------------------------------------------------
# MULTI-ROLE ROW BUILDER — the Phase 8 core
# ---------------------------------------------------------------------------

def build_multi_role_rows(email_record, extracted_fields):
    """
    Build one complete CRM row dict per role detected in the email.

    If the email contains 3 roles, this returns a list of 3 dicts.
    Each dict maps to exactly one row in the 55-column Excel sheet.

    Common fields (client, project, location, dates) are copied to every row.
    Role-specific fields (designation, headcount, rates) come from the roles array.

    Parameters:
        email_record     — dict from email_reader.fetch_emails() (raw email metadata)
        extracted_fields — dict returned by extract_fields() (AI output + roles array)

    Returns:
        List of CRM row dicts. Empty list if extraction failed.
    """
    if not extracted_fields:
        return []

    roles = extracted_fields.get("roles") or []

    # If the AI found no roles array, create a single placeholder role
    # so we still get one row of the common fields (client, project, etc.)
    if not roles:
        print("  WARNING: AI returned no roles array. Creating one row with partial data.")
        roles = [{
            "designation":           "",
            "headcount":             None,
            "psl_category":          "",
            "rates":                 "",
            "rates_currency":        "",
            "technical_requirements": "",
            "certifications":        "",
            "experience_years":      "",
        }]

    total_roles = len(roles)

    # Pull raw email metadata once, outside the loop
    email_id     = email_record.get("email_id", "")
    subject      = _clean(email_record.get("subject", ""))
    sender_email = email_record.get("sender_email", "")
    sender_name  = email_record.get("sender_name", "")
    has_attach   = email_record.get("has_attachments", False)

    received_raw  = email_record.get("received_date", "")
    received_date = received_raw[:10] if received_raw else ""

    # Detect whether this looks like a follow-up email (re:, fw:, interview mentions, etc.)
    follow_up_keywords = ["re:", "fw:", "fwd:", "follow up", "update", "feedback",
                          "interview", "shortlist", "selected", "mobiliz", "offer"]
    is_follow_up = any(kw in subject.lower() for kw in follow_up_keywords)

    # Build a short unique hash from the email_id for the req_id
    id_hash  = hashlib.md5(email_id.encode()).hexdigest()[:6].upper() if email_id else "000000"
    date_str = datetime.date.today().strftime("%Y%m%d")

    rows = []

    for i, role in enumerate(roles, start=1):

        # Unique record ID: REQ-20260604-A3F7B2-01
        req_id = f"REQ-{date_str}-{id_hash}-{i:02d}"

        # PSL category: from role dict if AI provided it, else try the taxonomy lookup
        psl_cat = _clean(role.get("psl_category")) or get_psl_for_role(_clean(role.get("designation")))

        row = {
            # ---- Section 1: Identity & System --------------------------------
            "req_id":           req_id,
            "email_id":         email_id,
            "received_date":    received_date,
            "subject":          subject,
            "source_mailbox":   sender_email,   # Pilot: sender's address. Prod: AM's mailbox.
            "am_name":          "",             # Filled manually by AM

            # ---- Section 2: Client Information -------------------------------
            "client_name":      _clean(extracted_fields.get("client_name")),
            "client_country":   _clean(extracted_fields.get("client_country")),
            "client_sector":    _clean(extracted_fields.get("client_sector")),
            "contact_person":   _clean(extracted_fields.get("contact_person")),
            "contact_email":    _clean(extracted_fields.get("contact_email")),
            "contact_phone":    _clean(extracted_fields.get("contact_phone")),
            "client_ref_number":_clean(extracted_fields.get("client_ref_number")),
            "psl_categories":   psl_cat,

            # ---- Section 3: Role & Requirements (per-role) -------------------
            "designation":      _clean(role.get("designation")),
            "headcount":        role.get("headcount") or "",
            "location":         _clean(extracted_fields.get("location")),
            "mobilization_date":_clean(extracted_fields.get("mobilization_date")),
            "duration":         _clean(extracted_fields.get("duration")),
            "contract_type":    _clean(extracted_fields.get("contract_type")),
            "work_schedule":    _clean(extracted_fields.get("work_schedule")),
            "technical_requirements": _clean(role.get("technical_requirements")),
            "certifications":   _clean(role.get("certifications")),
            "experience_years": _clean(role.get("experience_years")),
            "nationality_preference": _clean(extracted_fields.get("nationality_preference")),
            "rates":            _clean(role.get("rates")),
            "rates_currency":   _clean(role.get("rates_currency")),
            "project_name":     _clean(extracted_fields.get("project_name")),
            "urgency":          _clean(extracted_fields.get("urgency")),

            # ---- Section 4: Stage & Status -----------------------------------
            "category":         _clean(extracted_fields.get("category")),
            "requirement_stage":_clean(extracted_fields.get("requirement_stage"))
                                 or "Requirement Received",
            "status":           "New",          # Always starts as New
            "deadline":         _clean(extracted_fields.get("deadline")),

            # ---- Section 5: Fulfillment Tracking ----------------------------
            "cvs_requested":    _clean(extracted_fields.get("cvs_requested")),
            "cvs_shared":       _clean(extracted_fields.get("cvs_shared")),
            "profiles_shortlisted": _clean(extracted_fields.get("profiles_shortlisted")),
            "interview_date":   _clean(extracted_fields.get("interview_date")),
            "interview_outcome":_clean(extracted_fields.get("interview_outcome")),
            "candidate_selected":_clean(extracted_fields.get("candidate_selected")),
            "candidate_mobilized":_clean(extracted_fields.get("candidate_mobilized")),

            # ---- Section 6: Communication ------------------------------------
            "email_summary":    _clean(extracted_fields.get("email_summary")),
            "next_action":      _clean(extracted_fields.get("next_action")),
            "am_notes":         "",             # Filled manually by AM
            "service_order_id": "",             # Filled manually by AM

            # ---- Section 7: Compliance & Audit -------------------------------
            "sender_email":     sender_email,
            "sender_name":      sender_name,
            "has_attachments":  "Yes" if has_attach else "No",
            "is_follow_up":     "Yes" if is_follow_up else "No",
            "language_detected":_clean(extracted_fields.get("language_detected")) or "English",
            "total_roles_in_email": total_roles,
            "role_index":       f"{i} of {total_roles}",
            "processing_log":   (
                f"Extracted {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')} "
                f"| {GROQ_MODEL}"
            ),
            "llm_confidence":   extracted_fields.get("llm_confidence") or "",
            "missing_fields_flag": _clean(extracted_fields.get("missing_fields_flag")),
            "review_status":    "Pending Review",
        }

        rows.append(row)

    return rows


# ---------------------------------------------------------------------------
# FALLBACK — run_parser.py uses this for single-email convenience
# ---------------------------------------------------------------------------

def build_crm_row(email_record, extracted_fields):
    """
    Convenience wrapper: returns only the FIRST row from build_multi_role_rows().
    Used by any code that still expects a single dict instead of a list.

    For multi-role emails you should call build_multi_role_rows() directly
    so all roles get their own row.
    """
    rows = build_multi_role_rows(email_record, extracted_fields)
    return rows[0] if rows else {}


# ---------------------------------------------------------------------------
# HELPER
# ---------------------------------------------------------------------------

def _clean(value):
    """Convert None → empty string. Keeps all other values as-is."""
    return "" if value is None else value


# ---------------------------------------------------------------------------
# QUICK TEST — run this file directly to verify extraction end-to-end
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # We need parser.py from the same folder
    sys.path.insert(0, str(Path(__file__).parent))
    import parser as email_parser

    # --- Test 1: single-role email ---
    test_single = {
        "email_id":       "test-phase8-001",
        "received_date":  "2025-06-01T09:00:00Z",
        "subject":        "Manpower Request - Drilling Engineers - Khurais Project",
        "sender_name":    "Ahmed Al-Rashid",
        "sender_email":   "ahmed@aramco.com",
        "body_type":      "text",
        "has_attachments": False,
        "body_content":   """
Dear Team,

We require 2 Senior Drilling Engineers for our Khurais Field Expansion in Dammam, KSA.
Mobilization: 01 July 2025. Duration: 6 months. Rate: $850/day.
Min 8 years experience. IWCF required.
Submit CVs by 10 June 2025.

Regards,
Ahmed Al-Rashid | Saudi Aramco | ahmed@aramco.com
        """
    }

    # --- Test 2: multi-role email ---
    test_multi = {
        "email_id":       "test-phase8-002",
        "received_date":  "2025-06-02T10:00:00Z",
        "subject":        "Manpower Requirement - Multiple Positions - Abu Dhabi",
        "sender_name":    "Khalid Al-Mansoori",
        "sender_email":   "khalid@adnoc.ae",
        "body_type":      "text",
        "has_attachments": False,
        "body_content":   """
Dear Team,

ADNOC Drilling requires the following personnel for our Bab Field project:

1. Toolpusher x2 — $900/day — 28/28 rotation — min 10 years, offshore
2. MWD Engineer x1 — $750/day — IWCF, MWD directional experience min 5 years
3. HSE Supervisor x1 — $600/day — NEBOSH, min 6 years OFS HSE

Location: Abu Dhabi, UAE. Mobilization: 15 August 2025. Contract: 12 months.
Please submit CVs by 30 June 2025.

Best regards,
Khalid Al-Mansoori | ADNOC Drilling
        """
    }

    for label, test_email in [("Single-role", test_single), ("Multi-role", test_multi)]:
        print(f"\n{'='*65}")
        print(f"  TEST: {label} email")
        print("=" * 65)

        email_text = email_parser.prepare_email_for_ai(test_email)
        extracted  = extract_fields(email_text)

        if extracted:
            rows = build_multi_role_rows(test_email, extracted)
            print(f"\n  CRM rows generated: {len(rows)}")

            for j, row in enumerate(rows, 1):
                print(f"\n  --- Row {j} ({row.get('role_index', '')}) ---")
                key_fields = [
                    "req_id", "client_name", "client_country", "designation",
                    "headcount", "psl_categories", "rates", "mobilization_date",
                    "deadline", "requirement_stage", "urgency", "llm_confidence",
                    "missing_fields_flag"
                ]
                for field in key_fields:
                    val = row.get(field, "")
                    if val:
                        print(f"    {field:<25} {val}")
        else:
            print("  FAILED: extract_fields() returned None")
