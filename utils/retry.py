# utils/retry.py
# PURPOSE: Retry API calls with exponential backoff.
#
# Used by email_reader.py (Microsoft Graph API) and extractor.py (Groq API).
# A single network hiccup or temporary server error will not fail the pipeline —
# it retries automatically up to 3 times before giving up.
#
# BACKOFF SCHEDULE (default):
#   Attempt 1 fails → wait 2 seconds → attempt 2
#   Attempt 2 fails → wait 4 seconds → attempt 3
#   Attempt 3 fails → raise the last exception to the caller
#
# WHAT GETS RETRIED:
#   - Connection errors (network down, DNS failure)
#   - Timeouts
#   - HTTP 5xx errors (server-side problems — 500, 503, 504)
#   - HTTP 429 (rate limit — too many requests)
#
# WHAT IS NOT RETRIED (fails immediately):
#   - HTTP 401 Unauthorized (bad/expired token — retrying won't help)
#   - HTTP 403 Forbidden (permission issue)
#   - HTTP 400 Bad Request (malformed request — retrying won't fix the request)

import time
import requests

# Default retry settings — change these here to affect all API calls at once
MAX_ATTEMPTS = 3   # 1 original attempt + 2 retries
BASE_DELAY   = 2   # seconds; delay doubles each retry: 2s → 4s → 8s


def retry_api_call(api_func, max_attempts=MAX_ATTEMPTS, base_delay=BASE_DELAY, label="API"):
    """
    Call api_func() and retry up to max_attempts times on transient failures.

    HOW TO USE:
        Instead of:
            response = requests.get(url, headers=headers, timeout=30)

        Write:
            def _call():
                r = requests.get(url, headers=headers, timeout=30)
                r.raise_for_status()
                return r
            response = retry_api_call(_call, label="Graph API")

    Parameters:
        api_func     — a zero-argument callable that makes the API call and returns a response
        max_attempts — total number of tries including the first (default: 3)
        base_delay   — base seconds for backoff (default: 2 → delays are 2s, 4s, 8s)
        label        — short name shown in retry messages, e.g. "Graph API" or "Groq API"

    Returns:
        Whatever api_func() returns on success.

    Raises:
        The last exception if all attempts are exhausted.
    """
    last_error = None

    for attempt in range(1, max_attempts + 1):
        try:
            return api_func()

        except requests.exceptions.HTTPError as e:
            # Check the HTTP status code to decide whether retrying makes sense
            status = e.response.status_code if e.response is not None else 0

            if status in (400, 401, 403):
                # Client-side errors — retrying won't fix these
                # 400: bad request   401: auth failed   403: forbidden
                print(f"  [{label}] HTTP {status} error — not retrying (client-side issue).")
                raise

            # 5xx server errors and 429 rate-limit are worth retrying
            last_error = e

            # For 429, use Retry-After header if present (Groq returns this).
            # Override the standard exponential delay with the actual reset time.
            if status == 429 and e.response is not None and attempt < max_attempts:
                raw = (
                    e.response.headers.get("Retry-After")
                    or e.response.headers.get("x-ratelimit-reset-requests")
                    or e.response.headers.get("x-ratelimit-reset-tokens")
                )
                if raw:
                    try:
                        override = float(raw) + 2  # small buffer
                        print(f"  [{label}] Rate-limit: Retry-After={raw}s — waiting {override:.0f}s...")
                        time.sleep(override)
                        continue  # skip the standard sleep below
                    except (ValueError, TypeError):
                        pass
                # No header — fall back to a 60s wait for rate-limit errors
                print(f"  [{label}] Rate-limit 429 (no Retry-After header) — waiting 60s...")
                time.sleep(60)
                continue  # skip the standard sleep below

        except (requests.exceptions.ConnectionError,
                requests.exceptions.Timeout,
                requests.exceptions.RequestException) as e:
            # Network-level errors — almost always transient
            last_error = e

        # If we get here, this attempt failed and there are retries left (or not)
        if attempt < max_attempts:
            delay = base_delay ** attempt  # 2, 4, 8, ... seconds
            print(f"  [{label}] Attempt {attempt}/{max_attempts} failed: {last_error}")
            print(f"  [{label}] Retrying in {delay}s...")
            time.sleep(delay)
        else:
            print(f"  [{label}] All {max_attempts} attempts failed.")

    # Raise the last recorded error so the caller can handle it
    raise last_error


# ---------------------------------------------------------------------------
# QUICK TEST — run this file directly
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=== retry.py self-test ===\n")

    # Test 1: function that succeeds on first try
    call_count = {"n": 0}
    def _succeed():
        call_count["n"] += 1
        return "ok"
    result = retry_api_call(_succeed, label="test-success")
    assert result == "ok" and call_count["n"] == 1, "Should succeed on first try"
    print("  PASS: succeeds on first try")

    # Test 2: function that fails twice then succeeds
    call_count["n"] = 0
    def _fail_twice():
        call_count["n"] += 1
        if call_count["n"] < 3:
            raise requests.exceptions.ConnectionError("simulated network error")
        return "ok-after-retries"
    result = retry_api_call(_fail_twice, base_delay=0, label="test-retry")
    assert result == "ok-after-retries" and call_count["n"] == 3
    print("  PASS: retries twice then succeeds")

    # Test 3: function that always fails — should raise after max_attempts
    def _always_fail():
        raise requests.exceptions.Timeout("simulated timeout")
    try:
        retry_api_call(_always_fail, max_attempts=2, base_delay=0, label="test-exhausted")
        assert False, "Should have raised"
    except requests.exceptions.Timeout:
        print("  PASS: raises after all attempts exhausted")

    # Test 4: 401 error — should raise immediately without retrying
    call_count["n"] = 0
    mock_resp = type("R", (), {"status_code": 401})()
    def _auth_fail():
        call_count["n"] += 1
        raise requests.exceptions.HTTPError(response=mock_resp)
    try:
        retry_api_call(_auth_fail, max_attempts=3, base_delay=0, label="test-401")
        assert False, "Should have raised"
    except requests.exceptions.HTTPError:
        assert call_count["n"] == 1, "Should not retry on 401"
        print("  PASS: 401 raises immediately without retrying")

    print("\n  All tests passed.")
