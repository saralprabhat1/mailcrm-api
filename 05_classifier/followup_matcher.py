# followup_matcher.py  —  Phase 9 (follow-up email matching)
#
# PURPOSE:
#   Given a follow-up email, find the existing CRM requirement it belongs to.
#   Returns the req_id of the best-matching record and a confidence score.
#
# HOW IT WORKS:
#   1. Detect whether an email is a follow-up at all (subject prefix + body keywords)
#   2. Strip Re:/Fw: chains from the subject, then compare cleaned subject tokens
#   3. Also score on: sender domain, designation in body, client name in body
#   4. Return the best-scoring match if it exceeds MATCH_THRESHOLD (40/100)
#
# SCORING BREAKDOWN (100 pts max):
#   40 pts  —  cleaned subject token overlap (Jaccard similarity)
#   25 pts  —  sender email domain matches the existing record's sender domain
#   20 pts  —  designation from existing record appears in follow-up text
#   15 pts  —  client name from existing record appears in follow-up text

import re
import sys
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Minimum score out of 100 to accept a match.
# Raised from 40 → 60: a new-req email from the same sender domain can score
# 25 (domain) + 15 (client name) = 40, which is enough to spuriously match an
# existing record. Requiring 60 means at least subject overlap + domain, or
# domain + designation + client — a genuinely high-confidence match.
MATCH_THRESHOLD = 60

# Subject prefixes that reliably signal a CLIENT REPLY to an existing thread.
# "fw:" and "fwd:" are intentionally excluded: in this pipeline every email is
# forwarded by Saral from his inbox, so Fw: is always present and tells us
# nothing about whether the email is a new requirement or a follow-up.
# Only "re:" means a client actually replied to an ongoing thread.
FOLLOWUP_PREFIXES = ["re:", "response:", "reply:"]

# Body phrases that are SPECIFIC to follow-up emails.
# Deliberately excludes generic terms ("cv", "resume", "profile", "regarding",
# "please find attached", "update", "offer") that routinely appear in new
# requirement emails and caused false-positive follow-up detection.
# We require at least 5 hits before classifying body-only as a follow-up.
FOLLOWUP_BODY_KEYWORDS = [
    "shortlist", "interview", "selected",
    "mobiliz", "cancell", "on hold",
    "as discussed", "further to",
    "following our", "following up",
    "per our conversation", "as requested",
]


# ---------------------------------------------------------------------------
# PUBLIC FUNCTION 1 — detection
# ---------------------------------------------------------------------------

def is_followup_email(subject, body_text=""):
    """
    Decide whether an email is a follow-up to an existing requirement.

    We check two signals:
      1. Subject starts with Re:/Fw:/Fwd: — the most reliable signal
      2. Body contains 5+ follow-up-specific phrases — catches plain-text updates
         that weren't sent as a reply thread (high bar to avoid false positives)

    Parameters:
        subject   — email subject line (string)
        body_text — plain-text email body (string, optional)

    Returns:
        True if this looks like a follow-up, False if it looks like a new requirement.
    """
    subj_lower = subject.lower().strip()

    # Check subject prefix first — clearest signal
    for prefix in FOLLOWUP_PREFIXES:
        if subj_lower.startswith(prefix):
            return True

    # Check body for multiple follow-up phrases.
    # Threshold is 5 (not 3) because the keyword list is narrow — 5 hits from
    # follow-up-specific phrases is a strong signal; 3 was too easy to reach
    # with generic language in new requirement emails.
    body_lower   = body_text.lower()
    keyword_hits = sum(1 for kw in FOLLOWUP_BODY_KEYWORDS if kw in body_lower)
    if keyword_hits >= 5:
        return True

    return False


# ---------------------------------------------------------------------------
# PUBLIC FUNCTION 2 — matching
# ---------------------------------------------------------------------------

def find_best_match(follow_up_email, crm_df):
    """
    Scan all existing CRM requirements and find the one that best matches
    the follow-up email.

    Parameters:
        follow_up_email — dict from email_reader.fetch_emails()
                          (needs keys: subject, sender_email, body_content)
        crm_df          — pandas DataFrame loaded from crm_data.xlsx
                          (all existing requirements as rows)

    Returns:
        Tuple (req_id, score):
          - req_id is the matched record's ID (e.g. "REQ-20260604-A3F7B2-01")
          - score is 0–100 (how confident the match is)
          Returns (None, 0) if no match exceeded the threshold.
    """
    if crm_df is None or crm_df.empty:
        print("  No existing CRM records to match against — treating as new record.")
        return None, 0

    best_req_id = None
    best_score  = 0

    for _, existing_row in crm_df.iterrows():
        s = _score_candidate(follow_up_email, existing_row)
        if s > best_score:
            best_score  = s
            best_req_id = existing_row.get("req_id", "")

    if best_score >= MATCH_THRESHOLD:
        print(f"  Match found: {best_req_id} (score: {best_score}/100)")
        return best_req_id, best_score
    else:
        print(f"  No confident match found (best score: {best_score}/100, threshold: {MATCH_THRESHOLD})")
        return None, best_score


# ---------------------------------------------------------------------------
# INTERNAL — scoring a single candidate row
# ---------------------------------------------------------------------------

def _score_candidate(follow_up_email, existing_row):
    """
    Compute a 0–100 similarity score between a follow-up email and one
    existing CRM record.

    Called once per row in find_best_match(). Not meant to be called directly.
    """
    score = 0

    fu_subject = follow_up_email.get("subject", "")
    fu_body    = follow_up_email.get("body_content", "")
    fu_sender  = follow_up_email.get("sender_email", "")

    # Combine subject + body for text searching
    fu_full_text = (fu_subject + " " + fu_body).lower()

    # --- Signal 1: Cleaned subject token overlap (40 pts) --------------------
    # Strip Re:/Fw: from both sides, then measure word-level Jaccard similarity.
    # Example: "Re: RFQ - Drilling Engineers KSA" and "RFQ - Drilling Engineers KSA"
    # share almost all tokens → high score.
    fu_clean  = strip_followup_prefix(fu_subject)
    ex_clean  = strip_followup_prefix(str(existing_row.get("subject", "")))

    fu_tokens = _tokenize(fu_clean)
    ex_tokens = _tokenize(ex_clean)

    if fu_tokens and ex_tokens:
        overlap = len(fu_tokens & ex_tokens)
        union   = len(fu_tokens | ex_tokens)
        jaccard = overlap / union if union > 0 else 0
        score  += int(40 * jaccard)

    # --- Signal 2: Sender email domain (25 pts) ------------------------------
    # The follow-up usually comes from the same company (same domain) as the original.
    fu_domain = _get_domain(fu_sender)
    ex_domain = _get_domain(str(existing_row.get("sender_email", "")))

    if fu_domain and ex_domain and fu_domain == ex_domain:
        score += 25

    # --- Signal 3: Designation appears in follow-up text (20 pts) ------------
    # If the existing record is for a "Drilling Engineer" and the follow-up
    # mentions "drilling engineer", that's a strong signal.
    designation  = str(existing_row.get("designation", "")).lower()
    desig_tokens = _tokenize(designation)

    if desig_tokens:
        hits = sum(1 for t in desig_tokens if t in fu_full_text)
        # Require at least 50% of the designation words to appear
        if hits >= len(desig_tokens) * 0.5:
            score += 20

    # --- Signal 4: Client name appears in follow-up text (15 pts) ------------
    client_name    = str(existing_row.get("client_name", "")).lower()
    client_tokens  = _tokenize(client_name)

    if client_tokens:
        hits = sum(1 for t in client_tokens if t in fu_full_text)
        if hits >= len(client_tokens) * 0.5:
            score += 15

    return score


# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------

def strip_followup_prefix(subject):
    """
    Remove Re:/Fw:/Fwd: chains from a subject line, leaving the original topic.

    Examples:
        "Re: Manpower Request - Drilling"  →  "Manpower Request - Drilling"
        "Fw: Re: Fw: RFQ Abu Dhabi"        →  "RFQ Abu Dhabi"
    """
    # Repeatedly strip the prefix until no more prefixes remain
    pattern = re.compile(r"^\s*(re|fw|fwd|response|reply)\s*:[\s]*", re.IGNORECASE)
    cleaned = subject
    while True:
        stripped = pattern.sub("", cleaned).strip()
        if stripped == cleaned:
            break
        cleaned = stripped
    return cleaned


def _get_domain(email_address):
    """
    Extract the domain part from an email address.
    Returns '' if the address is empty or doesn't contain '@'.
    Example: 'ahmed@aramco.com' → 'aramco.com'
    """
    if not email_address or "@" not in str(email_address):
        return ""
    return str(email_address).lower().split("@")[-1].strip()


def _tokenize(text):
    """
    Split a string into a set of lowercase word tokens (3+ chars only).
    Used for Jaccard similarity — short words like 'to', 'a', 'in' are noise.
    Example: "Drilling Engineer - KSA" → {'drilling', 'engineer'}
    """
    if not text:
        return set()
    return set(re.findall(r"[a-z]{3,}", str(text).lower()))


# ---------------------------------------------------------------------------
# QUICK TEST — run this file directly to test the matching logic
# ---------------------------------------------------------------------------
if __name__ == "__main__":

    # Simulate an existing CRM record (as a dict, the way a DataFrame row looks)
    existing_record = {
        "req_id":       "REQ-20260601-A3F7B2-01",
        "subject":      "Manpower Request - Drilling Engineers - Khurais Project",
        "sender_email": "ahmed@aramco.com",
        "client_name":  "Saudi Aramco",
        "designation":  "Drilling Engineer",
    }

    # Simulate a follow-up email to the same requirement
    followup_email = {
        "subject":       "Re: Manpower Request - Drilling Engineers - Khurais Project",
        "sender_email":  "ahmed@aramco.com",
        "body_content":  "Please find attached the CVs for 2 Drilling Engineers as requested.",
    }

    # Simulate an unrelated email (should score low)
    unrelated_email = {
        "subject":      "Invoice #2456 - June Services",
        "sender_email": "accounts@randomvendor.com",
        "body_content": "Please find attached the invoice for services rendered in June.",
    }

    # Build a one-row DataFrame to test find_best_match
    crm_df = pd.DataFrame([existing_record])

    print("=== Test 1: Follow-up email (should match) ===")
    req_id, score = find_best_match(followup_email, crm_df)
    print(f"  Result: req_id={req_id}, score={score}")

    print("\n=== Test 2: Unrelated email (should NOT match) ===")
    req_id, score = find_best_match(unrelated_email, crm_df)
    print(f"  Result: req_id={req_id}, score={score}")

    print("\n=== Test 3: is_followup_email() detection ===")
    tests = [
        ("Re: RFQ - Drilling Engineers",                ""),
        ("Fw: Manpower Requirement",                    ""),
        ("New Requirement - HSE Supervisor",            ""),
        ("Feedback on submitted profiles",              "please find attached the cvs as requested following our discussion"),
    ]
    for subj, body in tests:
        result = is_followup_email(subj, body)
        print(f"  '{subj[:50]}' -> is_followup={result}")
