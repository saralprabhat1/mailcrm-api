# email_reader.py
# PURPOSE: Connect to Microsoft Graph API and fetch the latest emails from Outlook.
# This is Phase 3 of the CRM pipeline. It reads emails and returns them as
# a list of dictionaries, ready to be passed to the AI parser in Phase 4.
#
# HOW IT WORKS:
#   1. Loads Azure credentials from .env
#   2. Authenticates silently using the cached token (from auth_test.py login)
#   3. Calls the Graph API endpoint: GET /me/messages
#   4. Extracts the fields we need for CRM processing
#   5. Prints a summary and returns the data

import os
import sys
import base64
import requests
from pathlib import Path

# Add the project root to Python's path so we can import from utils/ and config/
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.auth import get_access_token, get_access_token_or_none, CLIENT_ID
from utils.retry import retry_api_call
from config.email_filters import filter_emails

# The Microsoft Graph API base URL — all email endpoints start with this
GRAPH_BASE_URL = "https://graph.microsoft.com/v1.0"


def fetch_emails(access_token, max_emails=10, folder="inbox"):
    """
    Fetch the latest emails from Outlook using the Microsoft Graph API.

    Parameters:
        access_token  — the Bearer token from get_access_token()
        max_emails    — how many emails to fetch (default: 10)
        folder        — which folder to read: "inbox" or "sentitems" etc.

    Returns:
        A list of dicts, one per email, with the fields we need for CRM parsing.
    """

    print(f"\nFetching latest {max_emails} emails from {folder}...")

    # Build the request headers — the token proves we are allowed to read this mailbox
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    # Build the API URL with query parameters:
    #   $select   — only fetch the fields we actually need (saves bandwidth)
    #   $top      — how many emails to return
    #   $orderby  — newest emails first
    #   $filter   — only unread emails (remove this line to get all emails)
    fields = ",".join([
        "id",
        "subject",
        "receivedDateTime",
        "from",
        "toRecipients",
        "body",
        "bodyPreview",
        "isRead",
        "hasAttachments",
        "importance"
    ])

    url = (
        f"{GRAPH_BASE_URL}/me/mailFolders/{folder}/messages"
        f"?$select={fields}"
        f"&$top={max_emails}"
        f"&$orderby=receivedDateTime desc"
    )

    # Make the GET request to the Graph API, with retry on transient failures.
    # headers is a dict captured by the closure — updating headers["Authorization"]
    # outside and then calling _call_graph() again picks up the new token.
    def _call_graph():
        r = requests.get(url, headers=headers, timeout=30)
        r.raise_for_status()
        return r

    try:
        response = retry_api_call(_call_graph, label="Graph API")
    except requests.exceptions.HTTPError as e:
        status = e.response.status_code if e.response is not None else "?"

        if status == 401:
            # Token expired mid-pipeline — attempt a silent refresh once.
            # This handles the case where the pipeline pauses for a long time
            # between authentication and the first API call.
            print("  Graph API 401 Unauthorized — attempting silent token refresh...")
            new_token = get_access_token_or_none()
            if new_token:
                headers["Authorization"] = f"Bearer {new_token}"
                try:
                    response = retry_api_call(_call_graph, label="Graph API (refreshed)")
                    print("  Token refreshed. Continuing.")
                except requests.exceptions.RequestException as e2:
                    print(f"  Graph API error after token refresh: {e2}")
                    return []
            else:
                print("  Silent token refresh failed — interactive re-login required.")
                print("  Run the pipeline again; it will prompt for device code login.")
                return []
        else:
            print(f"  Graph API HTTP {status} error (all retries failed): {e}")
            return []

    except requests.exceptions.RequestException as e:
        print(f"  Graph API network error (all retries failed): {e}")
        return []

    # Parse the JSON response — Graph API returns emails inside a 'value' list
    data = response.json()
    raw_emails = data.get("value", [])

    if not raw_emails:
        print("No emails found in this folder.")
        return []

    print(f"Retrieved {len(raw_emails)} emails. Extracting fields...")

    # --- Transform each raw email into a clean dictionary ---
    # We only keep the fields relevant to the CRM pipeline
    emails = []
    for item in raw_emails:

        # The sender info is nested inside from.emailAddress
        sender_info = item.get("from", {}).get("emailAddress", {})
        sender_name  = sender_info.get("name", "Unknown")
        sender_email = sender_info.get("address", "Unknown")

        # The email body comes in HTML by default — we use bodyPreview (plain text snippet)
        # for now. Phase 4 will handle the full HTML body with AI parsing.
        body_preview = item.get("bodyPreview", "")

        # The full body content (HTML or text) — needed for AI extraction in Phase 4
        body_content = item.get("body", {}).get("content", "")
        body_type    = item.get("body", {}).get("contentType", "text")  # "html" or "text"

        # Build the clean email record
        email_record = {
            "email_id":       item.get("id", ""),
            "received_date":  item.get("receivedDateTime", ""),
            "subject":        item.get("subject", "(No subject)"),
            "sender_name":    sender_name,
            "sender_email":   sender_email,
            "body_preview":   body_preview,
            "body_content":   body_content,
            "body_type":      body_type,
            "is_read":        item.get("isRead", False),
            "has_attachments": item.get("hasAttachments", False),
            "importance":     item.get("importance", "normal"),
        }

        emails.append(email_record)

    # Apply domain whitelist — drop any email whose sender is not on the approved list.
    # Filtered emails are silently discarded here, before parsing, AI, or storage.
    # To change which domains are allowed, edit config/email_filters.py only.
    emails = filter_emails(emails)

    return emails


def get_email_attachments(access_token, message_id):
    """
    Download all file attachments for a single email message.

    Why: Many requirement emails carry the actual RFQ data in a PDF or Word
    attachment rather than in the email body. We download the attachment bytes
    here so the pipeline can extract their text before calling the AI extractor.

    Parameters:
        access_token — Bearer token from get_access_token()
        message_id   — the Graph API message ID (stored as email["email_id"])

    Returns:
        List of dicts:  {name, content_type, size, bytes}
        Returns [] on any error so the pipeline can continue without attachments.

    Filtering rules:
        - Skip inline images (content_type starts with "image/") — logos, signatures
        - Skip files over 5 MB — too large to process efficiently
        - Skip items with no contentBytes — cannot decode them
    """
    MAX_ATTACHMENT_BYTES = 5 * 1024 * 1024  # 5 MB

    url = f"{GRAPH_BASE_URL}/me/messages/{message_id}/attachments"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    # Fetch the attachment list for this message
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"         [attachment] Graph API error fetching attachments: {e}")
        return []

    raw_attachments = response.json().get("value", [])

    attachments = []
    for att in raw_attachments:
        name         = att.get("name", "unknown")
        content_type = att.get("contentType", "")
        size         = att.get("size", 0)

        # Inline images are signatures, logos, etc. — not useful text content
        if content_type.startswith("image/"):
            print(f"         [attachment] Skipping inline image: '{name}'")
            continue

        # Very large files would slow down the pipeline and flood the AI prompt
        if size > MAX_ATTACHMENT_BYTES:
            size_mb = size / (1024 * 1024)
            print(f"         [attachment] Skipping '{name}' — {size_mb:.1f} MB exceeds 5 MB limit")
            continue

        # contentBytes is the base64-encoded file content returned by Graph API
        content_b64 = att.get("contentBytes", "")
        if not content_b64:
            print(f"         [attachment] '{name}' has no contentBytes — skipping")
            continue

        try:
            file_bytes = base64.b64decode(content_b64)
        except Exception as e:
            print(f"         [attachment] Could not base64-decode '{name}': {e}")
            continue

        size_kb = size / 1024
        print(f"         [attachment] Downloaded '{name}' ({size_kb:.1f} KB)")

        attachments.append({
            "name":         name,
            "content_type": content_type,
            "size":         size,
            "bytes":        file_bytes,
        })

    return attachments


def print_email_summary(emails):
    """
    Print a readable summary of fetched emails to the terminal.
    Useful for confirming we are fetching the right data before passing to AI.
    """
    print("\n" + "=" * 60)
    print(f"  EMAIL SUMMARY — {len(emails)} email(s) fetched")
    print("=" * 60)

    for i, email in enumerate(emails, start=1):
        # Truncate long subjects/previews so the output stays readable
        subject  = email["subject"][:55] + "..." if len(email["subject"]) > 55 else email["subject"]
        preview  = email["body_preview"][:80] + "..." if len(email["body_preview"]) > 80 else email["body_preview"]
        is_read  = "Read" if email["is_read"] else "UNREAD"
        has_att  = " [HAS ATTACHMENT]" if email["has_attachments"] else ""

        print(f"\n[{i}] {subject}")
        print(f"     From:    {email['sender_name']} <{email['sender_email']}>")
        print(f"     Date:    {email['received_date'][:10]}")
        print(f"     Status:  {is_read}{has_att}")
        print(f"     Preview: {preview}")

    print("\n" + "=" * 60)


# --- Main entry point ---
# This block only runs when you execute this file directly (not when imported)
if __name__ == "__main__":

    # Validate credentials loaded correctly
    if not CLIENT_ID:
        print("ERROR: AZURE_CLIENT_ID not found in .env file.")
        sys.exit(1)

    # Step 1: Get access token from persistent cache (no login prompt after first run)
    token = get_access_token()

    # Step 2: Fetch emails from the inbox
    # Change max_emails to fetch more or fewer; change folder to "sentitems" etc.
    emails = fetch_emails(token, max_emails=10, folder="inbox")

    # Step 3: Print a readable summary
    if emails:
        print_email_summary(emails)
        print(f"\nDone. {len(emails)} email(s) ready for AI parsing in Phase 4.")
    else:
        print("No emails were returned. Check the folder name or your permissions.")
