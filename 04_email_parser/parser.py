# parser.py
# PURPOSE: Clean raw email body text before sending to the AI.
# Outlook emails often arrive as HTML (with tags like <div>, <p>, <br>, etc.).
# The AI works much better on plain readable text — this file strips all the
# HTML and tidies up the whitespace, leaving only the actual message content.

import re


def strip_html(html_text):
    """
    Remove all HTML tags from a string and return clean plain text.

    Example:
        "<p>Hello <b>World</b></p>" → "Hello World"
    """
    if not html_text:
        return ""

    # Remove <style> blocks entirely — CSS is noise for the AI
    text = re.sub(r"<style[^>]*>.*?</style>", " ", html_text, flags=re.DOTALL | re.IGNORECASE)

    # Remove <script> blocks entirely
    text = re.sub(r"<script[^>]*>.*?</script>", " ", text, flags=re.DOTALL | re.IGNORECASE)

    # Replace <br>, <br/>, <p>, </p>, <div>, </div> with a newline
    # This preserves paragraph structure instead of jamming everything together
    text = re.sub(r"<br\s*/?>|</?(p|div|tr|li)[^>]*>", "\n", text, flags=re.IGNORECASE)

    # Strip all remaining HTML tags (anything between < and >)
    text = re.sub(r"<[^>]+>", " ", text)

    # Decode common HTML entities
    entities = {
        "&amp;":  "&",
        "&lt;":   "<",
        "&gt;":   ">",
        "&nbsp;": " ",
        "&quot;": '"',
        "&#39;":  "'",
        "&apos;": "'",
    }
    for entity, char in entities.items():
        text = text.replace(entity, char)

    # Collapse runs of whitespace/blank lines into single newlines
    text = re.sub(r"\n{3,}", "\n\n", text)   # max 2 blank lines
    text = re.sub(r"[ \t]+", " ", text)       # collapse horizontal whitespace
    text = "\n".join(line.strip() for line in text.splitlines())

    return text.strip()


def prepare_email_for_ai(email_record):
    """
    Take an email dict and return a clean text block ready to send to the AI.

    If preprocess_email() (Phase 12) has already run, it will have:
    - Stripped HTML and forwarding headers from body_content
    - Set body_type to "text" (so we skip the HTML strip here)
    - Set _original_sender to the actual client email (not the forwarder's)
    - Set _language/_language_name if non-English content was detected
    """

    subject      = email_record.get("subject", "(No subject)")
    received     = email_record.get("received_date", "")[:10]   # date part only
    body_content = email_record.get("body_content", "")
    body_type    = email_record.get("body_type", "text")

    # For forwarded emails, Phase 12 extracts the original client's name and email
    # from the Fw: header. Using those instead of Saral's details gives the AI the
    # correct sender to extract client_name and contact fields from.
    sender_name  = (
        email_record.get("_original_sender_name")
        or email_record.get("sender_name", "")
    )
    sender_email = (
        email_record.get("_original_sender")
        or email_record.get("sender_email", "")
    )

    # Strip HTML only if it hasn't been stripped already by preprocess_email()
    if body_type == "html":
        clean_body = strip_html(body_content)
    else:
        clean_body = body_content.strip()

    # Truncate very long emails — the AI only needs the first ~3000 characters
    max_chars = 3000
    if len(clean_body) > max_chars:
        clean_body = clean_body[:max_chars] + "\n\n[... email truncated ...]"

    # Language note: if Phase 12 detected non-English content, tell the AI.
    # This prevents the AI from skipping Arabic or French fields.
    lang_code = email_record.get("_language", "en")
    lang_note = ""
    if lang_code != "en":
        lang_name = email_record.get("_language_name", lang_code)
        lang_note = f"[NOTE: This email contains {lang_name} content. Extract all fields.]\n"

    formatted = (
        f"SUBJECT: {subject}\n"
        f"FROM: {sender_name} <{sender_email}>\n"
        f"DATE: {received}\n"
        f"---\n"
        f"{lang_note}"
        f"{clean_body}"
    )

    return formatted


# --- Quick test when run directly ---
if __name__ == "__main__":
    sample_html = """
    <html><body>
    <p>Dear Team,</p>
    <p>We require <b>2 Drilling Engineers</b> for our <b>Khurais project</b> in Dammam, KSA.</p>
    <p>Mobilization: <b>01 July 2025</b> | Duration: 6 months | Rate: $800/day</p>
    <p>Please submit CVs by <b>10 June 2025</b>.</p>
    <p>Regards,<br/>Ahmed Al-Rashid<br/>ahmed@aramco.com</p>
    </body></html>
    """

    cleaned = strip_html(sample_html)
    print("=== Cleaned text ===")
    print(cleaned)
