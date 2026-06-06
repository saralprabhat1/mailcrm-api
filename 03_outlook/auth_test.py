# auth_test.py
# PURPOSE: Test that we can authenticate with Microsoft Graph API using device code flow.
# This script does NOT read emails yet — it only checks that login works.
# Run this FIRST after completing the Azure app registration steps.

import sys
from pathlib import Path

# Add the project root to Python's path so we can import from utils/
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.auth import get_access_token, CLIENT_ID, TENANT_ID, SCOPES

# --- Validate that credentials are present ---
if not CLIENT_ID:
    print("ERROR: AZURE_CLIENT_ID is missing from your .env file.")
    print("       Go back to Step 7 of the setup guide and add it.")
    sys.exit(1)

print("=== Microsoft Graph API — Authentication Test ===")
print(f"Client ID loaded: {CLIENT_ID[:8]}...{CLIENT_ID[-4:]}  (partial, for safety)")
print(f"Tenant ID:        {TENANT_ID}")
print(f"Scopes:           {SCOPES}")
print()

# --- Get a token using the persistent cache in utils/auth.py ---
# First run: asks you to log in via browser and saves the token to disk.
# Every run after that: loads the saved token silently — no browser needed.
token = get_access_token()

# --- Report result ---
if token:
    token_preview = token[:20] + "..."
    print()
    print("SUCCESS! Authentication worked.")
    print(f"Access token received: {token_preview}")
    print()
    print("Token is saved to disk — next run will not ask for login.")
    print("You are now ready to run email_reader.py to fetch real emails.")
