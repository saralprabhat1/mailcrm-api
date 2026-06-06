# fetch_all_raw.py  —  One-off script: dump entire Inbox to CSV
#
# PURPOSE:
#   Fetch EVERY email from the Inbox of saral.prabhat@outlook.com and save
#   the raw content to sample_emails/raw_emails.csv.
#
#   This is NOT part of the main pipeline.  It is a data-collection tool so
#   we can manually label emails and build the Phase 10 ML training set.
#
# WHAT IT DOES:
#   1. Authenticates via the same cached token used by the main pipeline
#   2. Calls the Graph API with $top=999 (the maximum per page)
#   3. Follows @odata.nextLink to get every subsequent page
#   4. Collects EVERY email — no domain filter, no whitelist
#   5. Saves to sample_emails/raw_emails.csv with 5 columns:
#      email_id | subject | sender_email | body_preview | body_content
#
# HOW TO RUN:
#   cd C:\Python_Learning\crm-automation
#   python sample_emails/fetch_all_raw.py
#
# OUTPUT:
#   sample_emails/raw_emails.csv
#
# NOTE:
#   body_content is the full email body (HTML or plain text, as-is from Outlook).
#   It may be large.  The script uses pandas to_csv() which handles all special
#   characters (quotes, commas, newlines) safely.

import sys
import requests
import pandas as pd
from pathlib import Path

# Add project root to path so we can import utils/auth
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from utils.auth import get_access_token

# Where to save the output
OUTPUT_PATH = Path(__file__).parent / "raw_emails.csv"

# Graph API endpoint base
GRAPH_BASE_URL = "https://graph.microsoft.com/v1.0"

# $top=999 is the maximum the Graph API accepts per page for messages
# For large mailboxes the API returns a nextLink — we follow it until done
PAGE_SIZE = 999

# Only fetch these fields — avoids downloading unneeded metadata
SELECT_FIELDS = "id,subject,from,bodyPreview,body,receivedDateTime"


def fetch_all_inbox_emails(access_token: str) -> list:
    """
    Fetch every email from the Inbox, following pagination until exhausted.

    The Graph API returns at most PAGE_SIZE (999) emails per request.
    If the mailbox has more, the response includes an '@odata.nextLink' URL
    which points to the next page.  We keep following it until there is no
    more nextLink — that means we have everything.

    Parameters:
        access_token — Bearer token from get_access_token()

    Returns:
        List of raw email dicts (already cleaned to our 5-column schema).
    """
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    # First page URL — ordered newest first so the CSV reads chronologically
    # We do NOT add any $filter here — we want every email, read or unread,
    # from any sender, with any subject.
    url = (
        f"{GRAPH_BASE_URL}/me/mailFolders/inbox/messages"
        f"?$select={SELECT_FIELDS}"
        f"&$top={PAGE_SIZE}"
        f"&$orderby=receivedDateTime desc"
    )

    all_emails = []
    page_number = 0

    print(f"\nFetching all Inbox emails (page size: {PAGE_SIZE})...")
    print("This may take a few moments for large mailboxes.\n")

    # Keep fetching pages until the API says there are no more
    while url:
        page_number += 1
        print(f"  Page {page_number}: fetching up to {PAGE_SIZE} emails...")

        try:
            response = requests.get(url, headers=headers, timeout=60)
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            status = e.response.status_code if e.response is not None else "?"
            print(f"  ERROR: Graph API HTTP {status} on page {page_number}: {e}")
            print("  Stopping — saving whatever was collected so far.")
            break
        except requests.exceptions.RequestException as e:
            print(f"  ERROR: Network error on page {page_number}: {e}")
            print("  Stopping — saving whatever was collected so far.")
            break

        data = response.json()
        raw_items = data.get("value", [])

        print(f"  Got {len(raw_items)} emails on this page.")

        # Transform each raw Graph API item into our 5-column format
        for item in raw_items:
            sender_info  = item.get("from", {}).get("emailAddress", {})
            sender_email = sender_info.get("address", "")

            body_content = item.get("body", {}).get("content", "")

            all_emails.append({
                "email_id":     item.get("id", ""),
                "subject":      item.get("subject", "(No subject)"),
                "sender_email": sender_email,
                "body_preview": item.get("bodyPreview", ""),
                "body_content": body_content,
            })

        # Check if there is another page to fetch
        # '@odata.nextLink' is only present when more pages exist
        url = data.get("@odata.nextLink")
        if url:
            print(f"  More pages available — continuing...")
        else:
            print(f"  No more pages — all emails collected.")

    return all_emails


def save_to_csv(emails: list, output_path: Path) -> None:
    """
    Save the list of email dicts to a CSV file.

    Uses pandas so that special characters in email bodies (commas, quotes,
    newlines, HTML tags) are all handled safely by the CSV quoting rules.

    Parameters:
        emails      — list of dicts with our 5 columns
        output_path — where to write the CSV
    """
    if not emails:
        print("\nNo emails to save.")
        return

    # Make sure the output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    df = pd.DataFrame(emails, columns=[
        "email_id",
        "subject",
        "sender_email",
        "body_preview",
        "body_content",
    ])

    # quoting=csv.QUOTE_ALL wraps every field in double-quotes.
    # This is the safest choice when body_content contains HTML, commas, and newlines.
    import csv
    df.to_csv(output_path, index=False, quoting=csv.QUOTE_ALL, encoding="utf-8-sig")
    # utf-8-sig adds the BOM marker so Excel opens the file correctly on Windows

    print(f"\n  Saved {len(df)} rows -> {output_path}")
    print(f"  File size: {output_path.stat().st_size / 1024:.1f} KB")


# ---------------------------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------------------------
if __name__ == "__main__":

    print("=" * 65)
    print("  INBOX DUMP — fetch_all_raw.py")
    print("  Fetching ALL emails -> sample_emails/raw_emails.csv")
    print("=" * 65)

    # Step 1: Authenticate (silent if token cache exists, browser login if not)
    print("\n[Step 1] Authenticating...")
    token = get_access_token()

    # Step 2: Fetch every email from Inbox
    print("\n[Step 2] Fetching emails from Inbox...")
    emails = fetch_all_inbox_emails(token)

    # Step 3: Save to CSV
    print("\n[Step 3] Saving to CSV...")
    save_to_csv(emails, OUTPUT_PATH)

    # Summary
    print("\n" + "=" * 65)
    print(f"  Done.")
    print(f"  Total emails fetched : {len(emails)}")
    print(f"  Output file          : {OUTPUT_PATH}")
    print("=" * 65)
