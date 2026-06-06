# followup_extractor.py  —  Phase 9 (follow-up field extraction)
#
# PURPOSE:
#   Send a follow-up email to Groq AI and extract ONLY the fulfillment tracking
#   fields — the Section 5 fields that a follow-up email updates (CVs shared,
#   interview date, candidate selected, etc.) plus the new requirement stage.
#
# WHY NOT USE extractor.py?
#   The full 39-field prompt in extractor.py is designed for NEW requirements.
#   Sending a follow-up ("Re: please find 2 CVs attached") to that prompt wastes
#   tokens and confuses the AI (no new roles, no mobilization date, etc.).
#   This prompt is smaller, faster, and focused on what follow-ups actually tell us.
#
# OUTPUTS:
#   A dict with: followup_type, requirement_stage, and Section 5 fulfillment fields.
#   Passed to run_parser.py which builds the update dict for storage.update_record().

import os
import sys
import requests
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from utils.retry import retry_api_call
from utils.json_utils import parse_json_response
from config.fields import REQUIREMENT_STAGES

env_path = PROJECT_ROOT / ".env"
load_dotenv(dotenv_path=env_path)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL   = "llama-3.3-70b-versatile"

# ---------------------------------------------------------------------------
# FOLLOW-UP TYPE → STATUS MAPPING
# Used by run_parser.py to decide whether to set status to "In Progress" / "Done"
# ---------------------------------------------------------------------------

# What status should the CRM record move to when each follow-up type arrives?
FOLLOWUP_TYPE_TO_STATUS = {
    "cv_requested":        "In Progress",
    "cv_submitted":        "In Progress",
    "shortlisted":         "In Progress",
    "interview_scheduled": "In Progress",
    "interview_completed": "In Progress",
    "candidate_selected":  "In Progress",
    "offer_extended":      "In Progress",
    "mobilization":        "In Progress",
    "mobilized":           "Done",
    "position_filled":     "Done",
    "cancelled":           "On Hold",
    "on_hold":             "On Hold",
    "no_candidate":        "On Hold",
    "general_update":      None,          # No status change — just update notes
}


# ---------------------------------------------------------------------------
# SYSTEM PROMPT — targeted for follow-up content only
# ---------------------------------------------------------------------------

# Build the valid stage list dynamically from the single config source
_STAGES_LIST = " | ".join(REQUIREMENT_STAGES)

FOLLOWUP_SYSTEM_PROMPT = f"""You are a CRM update assistant for an oil & gas manpower consultancy.

You will receive a FOLLOW-UP email that relates to an ongoing recruitment requirement.
Your job: extract ONLY the fields that this follow-up email updates.
Do NOT re-extract the original requirement details (roles, rates, location, etc.).

FOLLOW-UP TYPE — choose exactly ONE that best describes this email:
cv_requested | cv_submitted | shortlisted | interview_scheduled | interview_completed |
candidate_selected | offer_extended | mobilization | mobilized | position_filled |
cancelled | on_hold | no_candidate | general_update

REQUIREMENT STAGE — choose the most appropriate UPDATED stage for this requirement:
{_STAGES_LIST}

Return ONLY this JSON (no markdown, no explanation, no extra keys):
{{
  "followup_type": "...",
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
  "llm_confidence": 0.9,
  "missing_fields_flag": ""
}}

FIELD GUIDANCE:
- followup_type: the single most accurate classification of what this email does
- requirement_stage: which stage does this email move the requirement to?
- cvs_requested: how many CVs did the client ask for? (integer or null)
- cvs_shared: how many CVs were sent to the client? (integer or null)
- profiles_shortlisted: how many profiles did the client shortlist? (integer or null)
- interview_date: date of interview if mentioned (YYYY-MM-DD or null)
- interview_outcome: brief result (e.g. "2 of 3 shortlisted", "Passed", "Deferred", null)
- candidate_selected: "Yes" if a candidate was chosen, "No" if rejected, null if unknown
- candidate_mobilized: "Yes" if the candidate has joined/mobilized, null otherwise
- email_summary: 1–2 sentences describing what happened in this follow-up email
- next_action: what the BD/AM team should do next based on this update
- llm_confidence: 0.0–1.0 (1.0 = every field clearly stated, <0.7 = many guesses)
- missing_fields_flag: comma-separated list of fields you could not determine"""


# ---------------------------------------------------------------------------
# MAIN FUNCTION
# ---------------------------------------------------------------------------

def extract_followup_fields(email_text):
    """
    Send a follow-up email to Groq AI and extract the fulfillment tracking update.

    This is intentionally a smaller, faster extraction than extract_fields() in
    extractor.py. It only asks for the fields that follow-up emails provide.

    Parameters:
        email_text — cleaned email string from parser.prepare_email_for_ai()

    Returns:
        A dict with followup_type, requirement_stage, and Section 5 fields.
        Returns None if the API call or JSON parsing failed.
    """
    if not GROQ_API_KEY:
        print("  ERROR: GROQ_API_KEY not found in .env file.")
        return None

    print("  Sending follow-up email to Groq AI (Phase 9 — follow-up extraction)...")

    payload = {
        "model":  GROQ_MODEL,
        "messages": [
            {"role": "system", "content": FOLLOWUP_SYSTEM_PROMPT},
            {
                "role":    "user",
                "content": f"Extract the follow-up CRM update fields from this email:\n\n{email_text}"
            }
        ],
        "temperature":     0.1,
        "response_format": {"type": "json_object"},
        "max_tokens":      800,   # Much smaller than the full extraction — follow-ups are simple
    }

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type":  "application/json"
    }

    # Wrap in retry — same pattern as extractor.py (3 attempts, exponential backoff)
    def _call_groq():
        r = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=45)
        r.raise_for_status()
        return r

    try:
        response = retry_api_call(_call_groq, label="Groq API (follow-up extractor)")
    except requests.exceptions.HTTPError as e:
        status = e.response.status_code if e.response is not None else "?"
        print(f"  Groq HTTP {status} error (all retries failed): {e}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"  Groq network error (all retries failed): {e}")
        return None

    raw_content = response.json()["choices"][0]["message"]["content"]
    extracted   = parse_json_response(raw_content)

    if extracted:
        ftype = extracted.get("followup_type", "unknown")
        stage = extracted.get("requirement_stage", "")
        conf  = extracted.get("llm_confidence", "")
        print(f"  Follow-up type  : {ftype}")
        print(f"  New stage       : {stage}")
        print(f"  AI confidence   : {conf}")

    return extracted


# ---------------------------------------------------------------------------
# QUICK TEST — run this file directly to verify follow-up extraction
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    sys.path.insert(0, str(PROJECT_ROOT / "04_email_parser"))
    import parser as email_parser

    # Simulate a "CVs submitted" follow-up
    test_cv_email = {
        "email_id":       "test-phase9-cv-001",
        "received_date":  "2026-06-05T11:00:00Z",
        "subject":        "Re: Manpower Request - Drilling Engineers - Khurais Project",
        "sender_name":    "Ahmed Al-Rashid",
        "sender_email":   "ahmed@aramco.com",
        "body_type":      "text",
        "has_attachments": True,
        "body_content":   """
Hi Ahmed,

Further to your requirement, please find attached the CVs for 2 Senior Drilling Engineers
for the Khurais Field Expansion project.

We have submitted 3 profiles for your review. Please shortlist by 12 June 2026.

Regards,
Saral
MailCRM
        """
    }

    # Simulate an "Interview scheduled" follow-up
    test_interview_email = {
        "email_id":       "test-phase9-int-001",
        "received_date":  "2026-06-06T09:00:00Z",
        "subject":        "Re: Manpower Request - Drilling Engineers - Khurais Project",
        "sender_name":    "Ahmed Al-Rashid",
        "sender_email":   "ahmed@aramco.com",
        "body_type":      "text",
        "has_attachments": False,
        "body_content":   """
Dear Saral,

Thank you for the profiles. We have shortlisted 2 candidates and would like to
schedule interviews on 15 June 2026 at 10:00 AM GST via Teams.

Please confirm candidate availability.

Regards,
Ahmed
        """
    }

    for label, test_email in [("CV Submission", test_cv_email), ("Interview Scheduled", test_interview_email)]:
        print(f"\n{'='*65}")
        print(f"  TEST: {label}")
        print("=" * 65)

        email_text = email_parser.prepare_email_for_ai(test_email)
        result     = extract_followup_fields(email_text)

        if result:
            print("\n  Extracted fields:")
            for key, val in result.items():
                if val not in (None, "", "null"):
                    print(f"    {key:<25} {val}")
        else:
            print("  FAILED: extract_followup_fields() returned None")
