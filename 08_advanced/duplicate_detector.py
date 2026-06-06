# duplicate_detector.py — Phase 13
#
# PURPOSE: Detect semantic duplicates BEFORE saving a new CRM row.
#
# WHY EMAIL_ID DEDUP IN STORAGE.PY IS NOT ENOUGH:
#   storage.py deduplicates on email_id + role_index — perfect for catching a
#   pipeline re-run on the same email. But it cannot catch:
#     - Same requirement emailed twice by the client from different accounts
#     - A forwarded email chain that produces the same requirement as an earlier email
#     - Same role for same client with slightly different subject lines
#   These cases create real duplicates in the CRM that need manual cleanup.
#
# HOW IT WORKS:
#   Compares the new row against every existing CRM row using string similarity
#   (difflib.SequenceMatcher — Python built-in, no extra install needed).
#   Weights: client_name 40% + designation 40% + mobilization_date 20%.
#   If either row lacks a mobilization date, weight is split 50/50 between
#   client and role (so missing dates don't unfairly penalise the score).
#
# THRESHOLDS:
#   >= 0.80 → definite duplicate: log failure, skip save
#   0.60–0.79 → possible duplicate: save but add to review queue for human check
#   < 0.60  → not a duplicate: proceed normally

from difflib import SequenceMatcher

# Above DUPLICATE_THRESHOLD: block the row from being saved
DUPLICATE_THRESHOLD = 0.80

# Between POSSIBLE_THRESHOLD and DUPLICATE_THRESHOLD: save, but flag for human review
POSSIBLE_THRESHOLD  = 0.60

# Pre-filter: skip existing rows where client names are clearly different.
# This makes the check fast on large CRM files (no need to compare every row).
CLIENT_PREFILTER = 0.50


def find_semantic_duplicate(new_row, crm_df):
    """
    Search existing CRM records for a semantic duplicate of new_row.

    Parameters:
        new_row — CRM row dict (from build_multi_role_rows() or psl_splitter)
        crm_df  — pandas DataFrame of existing CRM records (may be empty)

    Returns dict with keys:
        is_duplicate     (bool)   — True if similarity >= DUPLICATE_THRESHOLD
        is_possible      (bool)   — True if similarity >= POSSIBLE_THRESHOLD
        req_id_match     (str)    — req_id of the best-matching existing record (or "")
        similarity_score (float)  — 0.0–1.0, best match found
        explanation      (str)    — human-readable summary of what matched
    """
    # Default: no duplicate
    _no_match = {
        "is_duplicate":    False,
        "is_possible":     False,
        "req_id_match":    "",
        "similarity_score": 0.0,
        "explanation":     "",
    }

    # Empty CRM: nothing to compare against
    if crm_df is None or crm_df.empty:
        return _no_match

    new_client = _clean(new_row.get("client_name", ""))
    new_role   = _clean(new_row.get("designation", ""))
    new_date   = _clean(new_row.get("mobilization_date", ""))

    # If we have no client AND no role to compare, skip the check entirely.
    # A blank-versus-blank match would produce artificially high similarity.
    if not new_client and not new_role:
        return _no_match

    best_score       = 0.0
    best_req_id      = ""
    best_explanation = ""

    for _, row in crm_df.iterrows():
        ex_client = _clean(str(row.get("client_name", "")))
        ex_role   = _clean(str(row.get("designation", "")))
        ex_date   = _clean(str(row.get("mobilization_date", "")))
        ex_req_id = str(row.get("req_id", "")).strip()

        # Skip rows where the email_id is the same as the new row's email_id —
        # storage.py handles exact re-runs; we are looking for DIFFERENT emails
        if str(row.get("email_id", "")) == str(new_row.get("email_id", "")):
            continue

        # Pre-filter: skip rows where client names are clearly different
        if new_client and ex_client:
            if _sim(new_client, ex_client) < CLIENT_PREFILTER:
                continue

        score, note = _row_similarity(
            new_client, new_role, new_date,
            ex_client,  ex_role,  ex_date
        )

        if score > best_score:
            best_score       = score
            best_req_id      = ex_req_id
            best_explanation = (
                f"client={ex_client!r} role={ex_role!r} "
                f"({note}) => {score:.0%} match with {ex_req_id}"
            )

    # Build return dict based on best score found
    if best_score < POSSIBLE_THRESHOLD:
        return _no_match

    return {
        "is_duplicate":    best_score >= DUPLICATE_THRESHOLD,
        "is_possible":     True,   # always True here (we're above POSSIBLE_THRESHOLD)
        "req_id_match":    best_req_id,
        "similarity_score": round(best_score, 3),
        "explanation":     best_explanation,
    }


# ---------------------------------------------------------------------------
# PRIVATE HELPERS
# ---------------------------------------------------------------------------

def _sim(a, b):
    """
    Similarity ratio between two strings using SequenceMatcher (0.0–1.0).
    Case-insensitive. Returns 0.0 if either string is empty.
    """
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def _clean(value):
    """Normalise a field value: strip whitespace, handle 'None'/'nan' strings."""
    s = str(value).strip()
    return "" if s.lower() in ("none", "nan", "null") else s


def _row_similarity(new_client, new_role, new_date, ex_client, ex_role, ex_date):
    """
    Weighted similarity between one new and one existing CRM row.

    Weights:
        client_name      40%
        designation      40%
        mobilization_date 20%  (only if both rows have a date; otherwise 50/50)

    Returns (score 0-1, note string describing the component scores).
    """
    client_sim = _sim(new_client, ex_client)
    role_sim   = _sim(new_role,   ex_role)

    # Apply date dimension only when both rows have a date.
    # Without this guard, rows with no date would score 0 on the date component
    # even if client + role are a perfect match, unfairly lowering the score.
    both_have_dates = bool(new_date and ex_date)

    if both_have_dates:
        date_sim = _sim(new_date, ex_date)
        score    = 0.40 * client_sim + 0.40 * role_sim + 0.20 * date_sim
        note     = (
            f"client {client_sim:.0%}, "
            f"role {role_sim:.0%}, "
            f"date {date_sim:.0%}"
        )
    else:
        score = 0.50 * client_sim + 0.50 * role_sim
        note  = (
            f"client {client_sim:.0%}, "
            f"role {role_sim:.0%} (no dates)"
        )

    return score, note


# ---------------------------------------------------------------------------
# QUICK SELF-TEST (run: python duplicate_detector.py)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import pandas as pd

    # Simulate an existing CRM with two records
    existing_records = [
        {
            "req_id":            "REQ-20260604-AAA001-01",
            "email_id":          "email-001",
            "client_name":       "Saudi Aramco",
            "designation":       "Senior Drilling Engineer",
            "mobilization_date": "2026-08-01",
        },
        {
            "req_id":            "REQ-20260604-BBB002-01",
            "email_id":          "email-002",
            "client_name":       "ADNOC Drilling",
            "designation":       "MWD Engineer",
            "mobilization_date": "2026-09-15",
        },
    ]
    crm_df = pd.DataFrame(existing_records)

    test_cases = [
        {
            "name": "Definite duplicate — same client, same role, same date",
            "row":  {
                "email_id": "email-999",
                "client_name": "Saudi Aramco",
                "designation": "Senior Drilling Engineer",
                "mobilization_date": "2026-08-01",
            },
            "expect_duplicate": True,
        },
        {
            "name": "Possible duplicate — same client, similar role, no date",
            "row":  {
                "email_id": "email-999",
                "client_name": "Saudi Aramco",
                "designation": "Drilling Engineer",
                "mobilization_date": "",
            },
            "expect_possible": True,
        },
        {
            "name": "Not a duplicate — different client",
            "row":  {
                "email_id": "email-999",
                "client_name": "Shell Petroleum",
                "designation": "Drilling Engineer",
                "mobilization_date": "2026-08-01",
            },
            "expect_duplicate": False,
        },
        {
            "name": "Same email_id should be ignored (storage.py handles this)",
            "row":  {
                "email_id": "email-001",   # same as existing REQ-AAA001
                "client_name": "Saudi Aramco",
                "designation": "Senior Drilling Engineer",
                "mobilization_date": "2026-08-01",
            },
            "expect_duplicate": False,   # email_id excluded from semantic check
        },
    ]

    print("=== Duplicate Detector — Self Test ===\n")
    all_pass = True

    for tc in test_cases:
        result = find_semantic_duplicate(tc["row"], crm_df)
        is_dup = result["is_duplicate"]
        is_pos = result["is_possible"]
        score  = result["similarity_score"]

        expected_dup = tc.get("expect_duplicate", False)
        expected_pos = tc.get("expect_possible", False)

        passed = True
        if "expect_duplicate" in tc and is_dup != expected_dup:
            passed = False
        if "expect_possible" in tc and is_pos != expected_pos:
            passed = False

        status = "PASS" if passed else "FAIL"
        all_pass = all_pass and passed

        print(f"  [{status}] {tc['name']}")
        print(f"         score={score:.0%}  is_duplicate={is_dup}  is_possible={is_pos}")
        if result["explanation"]:
            print(f"         {result['explanation']}")
        print()

    print("All tests passed." if all_pass else "SOME TESTS FAILED.")
