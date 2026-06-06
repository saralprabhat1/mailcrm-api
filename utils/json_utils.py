# json_utils.py — shared JSON parsing helper for all extractor modules
#
# Moved here from extractor.py and followup_extractor.py to avoid duplication.

import json
import re


def parse_json_response(raw_content):
    """
    Parse an AI response string into a Python dict.
    Handles edge cases where the AI wraps JSON in markdown code blocks.
    """
    try:
        return json.loads(raw_content)
    except json.JSONDecodeError:
        pass

    # Fallback: extract the JSON object if it's wrapped in markdown ```json ... ```
    match = re.search(r"\{.*\}", raw_content, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    print(f"  WARNING: Could not parse AI response as JSON.")
    print(f"  Raw response (first 200 chars): {raw_content[:200]}")
    return None
