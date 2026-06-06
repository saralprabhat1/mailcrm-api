# tier3_classifier.py — Phase 13
#
# PURPOSE: LLM-based Tier 3 classifier for emails the ML model is uncertain about.
#
# WHEN IT IS CALLED:
#   Phase 10's scikit-learn ML classifier sets needs_review=True when its confidence
#   is below CONFIDENCE_THRESHOLD (0.75). At that point we don't want to either:
#     a) blindly skip the email (might miss a real requirement), OR
#     b) blindly send it for full extraction (wastes Groq tokens on irrelevant emails)
#   This module asks Groq to make the classification call instead — cheap (~100 tokens)
#   before committing to a full 2500-token extraction.
#
# WHAT IT RETURNS:
#   {"label": "relevant", "confidence": 0.82, "reason": "Contains manpower requirement..."}
#   label is one of: relevant / irrelevant / sensitive / financial / confidential
#
# FAILSAFE: always returns {"label": "relevant", "confidence": 0.5} on any error.
# Defaulting to "relevant" means uncertain emails are processed, not silently dropped.

import os
import sys
import requests
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
load_dotenv(dotenv_path=PROJECT_ROOT / ".env")

from utils.retry import retry_api_call
from utils.json_utils import parse_json_response

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL   = "llama-3.3-70b-versatile"

# Tier 3 uses the same confidence threshold as the ML classifier.
# If Groq returns confidence below this, both tiers are uncertain -> human review.
TIER3_CONFIDENCE_THRESHOLD = 0.75

# Short classification-only prompt — no field extraction, just label + confidence + reason.
# Kept intentionally brief so the model stays focused and the response is small.
_CLASSIFY_PROMPT = """You are an email classifier for an oil & gas manpower consultancy.

Classify the email into exactly ONE of these five labels:
- relevant: manpower requirement, RFQ, CV request, staffing enquiry, or any business email about hiring oil & gas personnel
- irrelevant: newsletters, subscriptions, promotional offers, or clearly off-topic emails
- sensitive: personal/private HR data, salary negotiations, personal grievances, health information
- financial: invoices, payment receipts, bank details, cost proposals, financial statements
- confidential: explicitly marked confidential, legal notices, contract disputes, NDA content

Respond ONLY with this exact JSON — no markdown, no extra text:
{"label": "<one of the five labels>", "confidence": <0.0 to 1.0>, "reason": "<one sentence>"}"""

# Valid labels — any other value from the LLM defaults to "relevant" (safe)
_VALID_LABELS = {"relevant", "irrelevant", "sensitive", "financial", "confidential"}


def classify_with_llm(email_dict):
    """
    Classify an email using Groq LLM. Called when ML confidence is below threshold.

    Uses only subject + sender + first 500 chars of body — enough to classify,
    much cheaper than the full 2500-token extraction prompt.

    Parameters:
        email_dict — email record dict; uses subject, body_content, sender_email

    Returns:
        dict with keys:
            label      (str)   — one of the five classification labels
            confidence (float) — 0.0–1.0 confidence in the label
            reason     (str)   — one-sentence explanation
    """
    # Safe fallback — returned on any error.
    # "relevant" means the email proceeds to extraction rather than being silently dropped.
    _fallback = {
        "label":      "relevant",
        "confidence": 0.5,
        "reason":     "Tier 3 LLM unavailable — defaulting to relevant (safe fallback)"
    }

    if not GROQ_API_KEY:
        print("  [Tier 3] GROQ_API_KEY not set — skipping Tier 3 classification.")
        return _fallback

    # Build a compact email summary (subject + sender + body excerpt)
    subject    = str(email_dict.get("subject", ""))
    sender     = str(
        email_dict.get("_original_sender")    # preferred: actual client sender (Phase 12)
        or email_dict.get("sender_email", "")
    )
    body       = str(email_dict.get("body_content", ""))
    body_short = body[:500].replace("\n", " ").strip()
    email_text = f"Subject: {subject}\nFrom: {sender}\nBody: {body_short}"

    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": _CLASSIFY_PROMPT},
            {"role": "user",   "content": f"Classify this email:\n\n{email_text}"}
        ],
        "temperature":    0.0,    # deterministic — no creativity needed for classification
        "response_format": {"type": "json_object"},
        "max_tokens":     150,    # classification response is small: label + float + one sentence
    }

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type":  "application/json"
    }

    def _call_groq():
        r = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=20)
        r.raise_for_status()
        return r

    try:
        response = retry_api_call(_call_groq, label="Groq Tier3")
    except requests.exceptions.RequestException as e:
        print(f"  [Tier 3] Groq API error: {e} — falling back to relevant")
        return _fallback

    raw_content = response.json()["choices"][0]["message"]["content"]
    result      = parse_json_response(raw_content)

    if not result:
        print("  [Tier 3] Could not parse Groq classification response — falling back")
        return _fallback

    # Normalise and validate the label
    label = str(result.get("label", "relevant")).lower().strip()
    if label not in _VALID_LABELS:
        label = "relevant"   # unexpected value — fail safe

    try:
        confidence = float(result.get("confidence", 0.7))
        confidence = max(0.0, min(1.0, confidence))  # clamp to 0-1 range
    except (TypeError, ValueError):
        confidence = 0.7

    return {
        "label":      label,
        "confidence": confidence,
        "reason":     str(result.get("reason", "")),
    }


# ---------------------------------------------------------------------------
# QUICK SELF-TEST (run: python tier3_classifier.py)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=== Tier 3 Classifier — Self Test ===\n")

    test_emails = [
        {
            "name": "Genuine RFQ",
            "subject": "Manpower Requirement - Drilling Engineers - KSA",
            "sender_email": "ahmed@aramco.com",
            "body_content": "We require 3 Senior Drilling Engineers for our Khurais project. Rate: $900/day.",
        },
        {
            "name": "Newsletter",
            "subject": "OilAndGasJobs Weekly Digest — June 2026",
            "sender_email": "noreply@oilandgasjobs.com",
            "body_content": "Here are this week's top job postings in the energy sector...",
        },
        {
            "name": "Invoice",
            "subject": "Invoice INV-2026-0043 — Manpower Services",
            "sender_email": "accounts@vendor.com",
            "body_content": "Please find attached invoice for services rendered. Total: $15,400. Bank: HDFC Account 12345.",
        },
    ]

    for t in test_emails:
        print(f"  Email: {t['name']}")
        result = classify_with_llm(t)
        print(f"  -> label={result['label']}  confidence={result['confidence']:.0%}")
        print(f"     reason: {result['reason']}\n")

    print("Self-test complete.")
