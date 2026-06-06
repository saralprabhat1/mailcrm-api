# utils/auth.py
# PURPOSE: Shared Microsoft Graph API authentication helper.
# Builds an MSAL app with a persistent token cache saved to disk.
# After the first login, the token (and its refresh token) are stored in
# data/.token_cache.bin — every subsequent run loads this file and skips login.

import os
import sys
import msal
from pathlib import Path
from dotenv import load_dotenv

# --- Locate the project root (the folder containing utils/) ---
PROJECT_ROOT = Path(__file__).parent.parent

load_dotenv(dotenv_path=PROJECT_ROOT / ".env")

CLIENT_ID = os.getenv("AZURE_CLIENT_ID")
TENANT_ID = os.getenv("AZURE_TENANT_ID", "common")
SCOPES    = os.getenv("AZURE_SCOPES", "https://graph.microsoft.com/Mail.Read").split()

# Cache file lives in data/ — never commit this file, it contains your login session
TOKEN_CACHE_PATH = PROJECT_ROOT / "data" / ".token_cache.bin"

# For personal @outlook.com / @hotmail.com / @live.com accounts, Microsoft requires
# the "consumers" authority. Using "common" causes silent refresh to fail because
# the token is stored under the consumers tenant but looked up under "common".
# If your account is a work/school account, change this back to "common".
AUTHORITY = "https://login.microsoftonline.com/consumers"


def _load_cache():
    """Read the token cache from disk. Returns an empty cache if the file doesn't exist yet."""
    cache = msal.SerializableTokenCache()
    if TOKEN_CACHE_PATH.exists():
        try:
            cache.deserialize(TOKEN_CACHE_PATH.read_text(encoding="utf-8"))
            print(f"  Cache loaded from: {TOKEN_CACHE_PATH}")
        except Exception as e:
            print(f"  WARNING: Could not read token cache ({e}). Will require fresh login.")
    return cache


def _save_cache(cache):
    """Write the token cache to disk. Always saves — does not rely on has_state_changed."""
    try:
        TOKEN_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
        TOKEN_CACHE_PATH.write_text(cache.serialize(), encoding="utf-8")
        print(f"  Token saved to: {TOKEN_CACHE_PATH}")
    except Exception as e:
        print(f"  WARNING: Could not save token cache ({e}). You may need to log in again next run.")


def _build_app(cache):
    """Create an MSAL PublicClientApplication wired to the given cache."""
    return msal.PublicClientApplication(
        client_id=CLIENT_ID,
        authority=AUTHORITY,
        token_cache=cache
    )


def get_access_token_or_none():
    """
    Attempt a silent token refresh. Returns a valid access token, or None on failure.

    Unlike get_access_token(), this function NEVER calls sys.exit() or prompts for login.
    Use this for mid-pipeline token refresh attempts (e.g. after a Graph API 401)
    where crashing the pipeline is unacceptable.

    Returns:
        access_token string if silent refresh succeeded, or None.
    """
    try:
        cache    = _load_cache()
        app      = _build_app(cache)
        accounts = app.get_accounts()
        if not accounts:
            return None
        result = app.acquire_token_silent(scopes=SCOPES, account=accounts[0])
        if result and "access_token" in result:
            _save_cache(cache)
            return result["access_token"]
        return None
    except Exception as e:
        print(f"  [auth] Token refresh error: {e}")
        return None


def get_access_token():
    """
    Return a valid Graph API access token.

    First run:        prompts you to log in via browser (device code flow).
    Every run after:  loads the saved token silently — no browser needed.
    Token refresh:    MSAL automatically uses the refresh token when the
                      access token expires (~1 hour), so login is only
                      needed once every ~90 days.
    """
    if not CLIENT_ID:
        print("ERROR: AZURE_CLIENT_ID not found in .env file.")
        sys.exit(1)

    cache = _load_cache()
    app   = _build_app(cache)

    # --- Attempt 1: silent refresh from cache ---
    # This works on every run after the first login, as long as the refresh
    # token is still valid (up to 90 days of inactivity before it expires).
    accounts = app.get_accounts()
    if accounts:
        print(f"  Found cached account: {accounts[0].get('username', '(unknown)')}")
        result = app.acquire_token_silent(scopes=SCOPES, account=accounts[0])
        if result and "access_token" in result:
            print("  Authenticated silently from cache.")
            _save_cache(cache)  # Refresh token may have been rotated — persist it
            return result["access_token"]
        else:
            # Silent refresh failed — token may be corrupted or fully expired
            err = result.get("error_description", "unknown error") if result else "no result"
            print(f"  Silent refresh failed: {err}")
            print("  Falling back to device code login...")
    else:
        print("  No cached account found. Starting first-time login...")

    # --- Attempt 2: device code flow (interactive, browser-based) ---
    print()
    flow = app.initiate_device_flow(scopes=SCOPES)

    if "user_code" not in flow:
        print(f"ERROR: Could not start device flow: {flow}")
        sys.exit(1)

    # This prints the URL and one-time code the user must enter in the browser
    print(flow["message"])
    print("\nWaiting for you to complete login in the browser...")

    result = app.acquire_token_by_device_flow(flow)

    if "access_token" not in result:
        print(f"ERROR: Login failed — {result.get('error_description', 'unknown error')}")
        sys.exit(1)

    # Save immediately after successful login so the next run is silent
    _save_cache(cache)
    print("Login successful. Future runs will not ask for login.")
    return result["access_token"]
