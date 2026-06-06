# config/fields.py
# PURPOSE: Single source of truth for the entire CRM data model.
#
# WHY THIS FILE EXISTS:
#   Before this file, column names, display labels, widths, and reference lists
#   were duplicated across extractor.py, storage.py, and dashboard.py.
#   If you renamed a column you had to find and update three files.
#   Now: change it here once — everything else updates automatically.
#
# WHAT'S IN THIS FILE:
#   FIELDS          — master list of all 55 field definitions (ordered = column order)
#   Reference lists — PSL_CATEGORIES, REQUIREMENT_STAGES, VALID_CATEGORIES, etc.
#   Colour maps     — STATUS_COLOURS, URGENCY_COLOURS (used by storage + dashboard)
#   Derived lookups — CRM_COLUMNS, DISPLAY_NAMES, COLUMN_WIDTHS, etc.
#                     (all computed from FIELDS — never hardcode these elsewhere)
#
# HOW TO ADD A NEW FIELD:
#   1. Add one dict entry to FIELDS below (in the right section, right position)
#   2. Update extractor.py to populate it (SYSTEM_PROMPT + build_multi_role_rows)
#   3. Done — storage.py and dashboard.py pick it up automatically

# ---------------------------------------------------------------------------
# MASTER FIELD LIST — 55 fields, one dict per field, in Excel column order
# ---------------------------------------------------------------------------
# Each field dict has these keys:
#   name         — snake_case key used in Python dicts, DataFrames, and Excel headers
#   display_name — human-readable label shown in the dashboard and Excel header
#   type         — "str", "int", "float", "date", or "bool_str"
#   section      — which of the 7 SharePoint sections this field belongs to
#   source       — who populates it: "llm", "system" (auto-code), or "manual" (AM)
#   excel_width  — column width in Excel character units
#   required     — True if this field must always have a value (used for validation)
#   wrap_text    — True for long free-text fields (enables word-wrap in Excel)
#   dashboard    — True if this field appears in standard dashboard table views

FIELDS = [

    # =========================================================================
    # SECTION 1 — Identity & System  (6 fields)
    # Populated automatically by extractor.py — AM fills am_name only
    # =========================================================================
    {
        "name":         "req_id",
        "display_name": "Req ID",
        "type":         "str",
        "section":      "Identity & System",
        "source":       "system",
        "excel_width":  18,
        "required":     True,
        "wrap_text":    False,
        "dashboard":    True,
    },
    {
        "name":         "email_id",
        "display_name": "Email ID",
        "type":         "str",
        "section":      "Identity & System",
        "source":       "system",
        "excel_width":  20,
        "required":     True,
        "wrap_text":    False,
        "dashboard":    False,
    },
    {
        "name":         "received_date",
        "display_name": "Received",
        "type":         "date",
        "section":      "Identity & System",
        "source":       "system",
        "excel_width":  14,
        "required":     True,
        "wrap_text":    False,
        "dashboard":    True,
    },
    {
        "name":         "subject",
        "display_name": "Subject",
        "type":         "str",
        "section":      "Identity & System",
        "source":       "system",
        "excel_width":  40,
        "required":     False,
        "wrap_text":    False,
        "dashboard":    False,
    },
    {
        "name":         "source_mailbox",
        "display_name": "Source Mailbox",
        "type":         "str",
        "section":      "Identity & System",
        "source":       "system",
        "excel_width":  28,
        "required":     False,
        "wrap_text":    False,
        "dashboard":    False,
    },
    {
        "name":         "am_name",
        "display_name": "AM Name",
        "type":         "str",
        "section":      "Identity & System",
        "source":       "manual",
        "excel_width":  16,
        "required":     False,
        "wrap_text":    False,
        "dashboard":    True,
    },

    # =========================================================================
    # SECTION 2 — Client Information  (8 fields)
    # All populated by the LLM
    # =========================================================================
    {
        "name":         "client_name",
        "display_name": "Client",
        "type":         "str",
        "section":      "Client Information",
        "source":       "llm",
        "excel_width":  22,
        "required":     True,
        "wrap_text":    False,
        "dashboard":    True,
    },
    {
        "name":         "client_country",
        "display_name": "Country",
        "type":         "str",
        "section":      "Client Information",
        "source":       "llm",
        "excel_width":  16,
        "required":     False,
        "wrap_text":    False,
        "dashboard":    True,
    },
    {
        "name":         "client_sector",
        "display_name": "Sector",
        "type":         "str",
        "section":      "Client Information",
        "source":       "llm",
        "excel_width":  12,
        "required":     False,
        "wrap_text":    False,
        "dashboard":    True,
    },
    {
        "name":         "contact_person",
        "display_name": "Contact",
        "type":         "str",
        "section":      "Client Information",
        "source":       "llm",
        "excel_width":  22,
        "required":     False,
        "wrap_text":    False,
        "dashboard":    False,
    },
    {
        "name":         "contact_email",
        "display_name": "Contact Email",
        "type":         "str",
        "section":      "Client Information",
        "source":       "llm",
        "excel_width":  28,
        "required":     False,
        "wrap_text":    False,
        "dashboard":    False,
    },
    {
        "name":         "contact_phone",
        "display_name": "Contact Phone",
        "type":         "str",
        "section":      "Client Information",
        "source":       "llm",
        "excel_width":  16,
        "required":     False,
        "wrap_text":    False,
        "dashboard":    False,
    },
    {
        "name":         "client_ref_number",
        "display_name": "Client Ref #",
        "type":         "str",
        "section":      "Client Information",
        "source":       "llm",
        "excel_width":  18,
        "required":     False,
        "wrap_text":    False,
        "dashboard":    False,
    },
    {
        "name":         "psl_categories",
        "display_name": "PSL Category",
        "type":         "str",
        "section":      "Client Information",
        "source":       "llm",
        "excel_width":  22,
        "required":     True,
        "wrap_text":    False,
        "dashboard":    True,
    },

    # =========================================================================
    # SECTION 3 — Role & Requirements  (15 fields)
    # All populated by the LLM. Per-role fields (designation, headcount, rates,
    # technical_requirements, certifications, experience_years) are extracted
    # per-role when an email mentions multiple positions.
    # =========================================================================
    {
        "name":         "designation",
        "display_name": "Role / Designation",
        "type":         "str",
        "section":      "Role & Requirements",
        "source":       "llm",
        "excel_width":  28,
        "required":     True,
        "wrap_text":    False,
        "dashboard":    True,
    },
    {
        "name":         "headcount",
        "display_name": "Headcount",
        "type":         "int",
        "section":      "Role & Requirements",
        "source":       "llm",
        "excel_width":  11,
        "required":     False,
        "wrap_text":    False,
        "dashboard":    True,
    },
    {
        "name":         "location",
        "display_name": "Location",
        "type":         "str",
        "section":      "Role & Requirements",
        "source":       "llm",
        "excel_width":  20,
        "required":     False,
        "wrap_text":    False,
        "dashboard":    True,
    },
    {
        "name":         "mobilization_date",
        "display_name": "Mob. Date",
        "type":         "date",
        "section":      "Role & Requirements",
        "source":       "llm",
        "excel_width":  16,
        "required":     False,
        "wrap_text":    False,
        "dashboard":    True,
    },
    {
        "name":         "duration",
        "display_name": "Duration",
        "type":         "str",
        "section":      "Role & Requirements",
        "source":       "llm",
        "excel_width":  14,
        "required":     False,
        "wrap_text":    False,
        "dashboard":    True,
    },
    {
        "name":         "contract_type",
        "display_name": "Contract Type",
        "type":         "str",
        "section":      "Role & Requirements",
        "source":       "llm",
        "excel_width":  14,
        "required":     False,
        "wrap_text":    False,
        "dashboard":    False,
    },
    {
        "name":         "work_schedule",
        "display_name": "Work Schedule",
        "type":         "str",
        "section":      "Role & Requirements",
        "source":       "llm",
        "excel_width":  14,
        "required":     False,
        "wrap_text":    False,
        "dashboard":    False,
    },
    {
        "name":         "technical_requirements",
        "display_name": "Technical Reqs",
        "type":         "str",
        "section":      "Role & Requirements",
        "source":       "llm",
        "excel_width":  45,
        "required":     False,
        "wrap_text":    True,
        "dashboard":    False,
    },
    {
        "name":         "certifications",
        "display_name": "Certifications",
        "type":         "str",
        "section":      "Role & Requirements",
        "source":       "llm",
        "excel_width":  30,
        "required":     False,
        "wrap_text":    True,
        "dashboard":    False,
    },
    {
        "name":         "experience_years",
        "display_name": "Experience",
        "type":         "str",
        "section":      "Role & Requirements",
        "source":       "llm",
        "excel_width":  16,
        "required":     False,
        "wrap_text":    False,
        "dashboard":    True,
    },
    {
        "name":         "nationality_preference",
        "display_name": "Nationality Pref.",
        "type":         "str",
        "section":      "Role & Requirements",
        "source":       "llm",
        "excel_width":  20,
        "required":     False,
        "wrap_text":    False,
        "dashboard":    False,
    },
    {
        "name":         "rates",
        "display_name": "Rates",
        "type":         "str",
        "section":      "Role & Requirements",
        "source":       "llm",
        "excel_width":  16,
        "required":     False,
        "wrap_text":    False,
        "dashboard":    True,
    },
    {
        "name":         "rates_currency",
        "display_name": "Currency",
        "type":         "str",
        "section":      "Role & Requirements",
        "source":       "llm",
        "excel_width":  12,
        "required":     False,
        "wrap_text":    False,
        "dashboard":    False,
    },
    {
        "name":         "project_name",
        "display_name": "Project",
        "type":         "str",
        "section":      "Role & Requirements",
        "source":       "llm",
        "excel_width":  30,
        "required":     False,
        "wrap_text":    False,
        "dashboard":    True,
    },
    {
        "name":         "urgency",
        "display_name": "Urgency",
        "type":         "str",
        "section":      "Role & Requirements",
        "source":       "llm",
        "excel_width":  10,
        "required":     False,
        "wrap_text":    False,
        "dashboard":    True,
    },

    # =========================================================================
    # SECTION 4 — Stage & Status  (4 fields)
    # category + deadline + requirement_stage from LLM. status starts as "New".
    # =========================================================================
    {
        "name":         "category",
        "display_name": "Category",
        "type":         "str",
        "section":      "Stage & Status",
        "source":       "llm",
        "excel_width":  20,
        "required":     True,
        "wrap_text":    False,
        "dashboard":    True,
    },
    {
        "name":         "requirement_stage",
        "display_name": "Stage",
        "type":         "str",
        "section":      "Stage & Status",
        "source":       "llm",
        "excel_width":  28,
        "required":     False,
        "wrap_text":    False,
        "dashboard":    True,
    },
    {
        "name":         "status",
        "display_name": "Status",
        "type":         "str",
        "section":      "Stage & Status",
        "source":       "system",
        "excel_width":  14,
        "required":     True,
        "wrap_text":    False,
        "dashboard":    True,
    },
    {
        "name":         "deadline",
        "display_name": "Deadline",
        "type":         "date",
        "section":      "Stage & Status",
        "source":       "llm",
        "excel_width":  14,
        "required":     False,
        "wrap_text":    False,
        "dashboard":    True,
    },

    # =========================================================================
    # SECTION 5 — Fulfillment Tracking  (7 fields)
    # Populated by LLM when processing follow-up emails (CV submissions,
    # interview outcomes, mobilization confirmations).
    # =========================================================================
    {
        "name":         "cvs_requested",
        "display_name": "CVs Requested",
        "type":         "int",
        "section":      "Fulfillment Tracking",
        "source":       "llm",
        "excel_width":  14,
        "required":     False,
        "wrap_text":    False,
        "dashboard":    False,
    },
    {
        "name":         "cvs_shared",
        "display_name": "CVs Shared",
        "type":         "int",
        "section":      "Fulfillment Tracking",
        "source":       "llm",
        "excel_width":  12,
        "required":     False,
        "wrap_text":    False,
        "dashboard":    False,
    },
    {
        "name":         "profiles_shortlisted",
        "display_name": "Shortlisted",
        "type":         "int",
        "section":      "Fulfillment Tracking",
        "source":       "llm",
        "excel_width":  14,
        "required":     False,
        "wrap_text":    False,
        "dashboard":    False,
    },
    {
        "name":         "interview_date",
        "display_name": "Interview Date",
        "type":         "date",
        "section":      "Fulfillment Tracking",
        "source":       "llm",
        "excel_width":  14,
        "required":     False,
        "wrap_text":    False,
        "dashboard":    False,
    },
    {
        "name":         "interview_outcome",
        "display_name": "Interview Outcome",
        "type":         "str",
        "section":      "Fulfillment Tracking",
        "source":       "llm",
        "excel_width":  20,
        "required":     False,
        "wrap_text":    False,
        "dashboard":    False,
    },
    {
        "name":         "candidate_selected",
        "display_name": "Candidate Selected",
        "type":         "str",
        "section":      "Fulfillment Tracking",
        "source":       "llm",
        "excel_width":  22,
        "required":     False,
        "wrap_text":    False,
        "dashboard":    False,
    },
    {
        "name":         "candidate_mobilized",
        "display_name": "Mobilized",
        "type":         "bool_str",
        "section":      "Fulfillment Tracking",
        "source":       "llm",
        "excel_width":  12,
        "required":     False,
        "wrap_text":    False,
        "dashboard":    False,
    },

    # =========================================================================
    # SECTION 6 — Communication  (4 fields)
    # email_summary + next_action from LLM. am_notes + service_order_id manual.
    # =========================================================================
    {
        "name":         "email_summary",
        "display_name": "Summary",
        "type":         "str",
        "section":      "Communication",
        "source":       "llm",
        "excel_width":  55,
        "required":     False,
        "wrap_text":    True,
        "dashboard":    True,
    },
    {
        "name":         "next_action",
        "display_name": "Next Action",
        "type":         "str",
        "section":      "Communication",
        "source":       "llm",
        "excel_width":  45,
        "required":     False,
        "wrap_text":    True,
        "dashboard":    True,
    },
    {
        "name":         "am_notes",
        "display_name": "AM Notes",
        "type":         "str",
        "section":      "Communication",
        "source":       "manual",
        "excel_width":  35,
        "required":     False,
        "wrap_text":    True,
        "dashboard":    False,
    },
    {
        "name":         "service_order_id",
        "display_name": "Service Order ID",
        "type":         "str",
        "section":      "Communication",
        "source":       "manual",
        "excel_width":  18,
        "required":     False,
        "wrap_text":    False,
        "dashboard":    False,
    },

    # =========================================================================
    # SECTION 7 — Compliance & Audit  (11 fields)
    # All populated automatically by the system — never by the LLM or AM
    # =========================================================================
    {
        "name":         "sender_email",
        "display_name": "Sender Email",
        "type":         "str",
        "section":      "Compliance & Audit",
        "source":       "system",
        "excel_width":  28,
        "required":     False,
        "wrap_text":    False,
        "dashboard":    True,
    },
    {
        "name":         "sender_name",
        "display_name": "Sender Name",
        "type":         "str",
        "section":      "Compliance & Audit",
        "source":       "system",
        "excel_width":  22,
        "required":     False,
        "wrap_text":    False,
        "dashboard":    False,
    },
    {
        "name":         "has_attachments",
        "display_name": "Has Attachments",
        "type":         "bool_str",
        "section":      "Compliance & Audit",
        "source":       "system",
        "excel_width":  14,
        "required":     False,
        "wrap_text":    False,
        "dashboard":    False,
    },
    {
        "name":         "is_follow_up",
        "display_name": "Follow-up",
        "type":         "bool_str",
        "section":      "Compliance & Audit",
        "source":       "system",
        "excel_width":  12,
        "required":     False,
        "wrap_text":    False,
        "dashboard":    False,
    },
    {
        "name":         "language_detected",
        "display_name": "Language",
        "type":         "str",
        "section":      "Compliance & Audit",
        "source":       "system",
        "excel_width":  14,
        "required":     False,
        "wrap_text":    False,
        "dashboard":    False,
    },
    {
        "name":         "total_roles_in_email",
        "display_name": "Roles in Email",
        "type":         "int",
        "section":      "Compliance & Audit",
        "source":       "system",
        "excel_width":  14,
        "required":     False,
        "wrap_text":    False,
        "dashboard":    False,
    },
    {
        "name":         "role_index",
        "display_name": "Role Index",
        "type":         "str",
        "section":      "Compliance & Audit",
        "source":       "system",
        "excel_width":  12,
        "required":     False,
        "wrap_text":    False,
        "dashboard":    False,
    },
    {
        "name":         "processing_log",
        "display_name": "Processing Log",
        "type":         "str",
        "section":      "Compliance & Audit",
        "source":       "system",
        "excel_width":  35,
        "required":     False,
        "wrap_text":    False,
        "dashboard":    False,
    },
    {
        "name":         "llm_confidence",
        "display_name": "AI Confidence",
        "type":         "float",
        "section":      "Compliance & Audit",
        "source":       "system",
        "excel_width":  14,
        "required":     False,
        "wrap_text":    False,
        "dashboard":    False,
    },
    {
        "name":         "missing_fields_flag",
        "display_name": "Missing Fields",
        "type":         "str",
        "section":      "Compliance & Audit",
        "source":       "system",
        "excel_width":  28,
        "required":     False,
        "wrap_text":    True,
        "dashboard":    False,
    },
    {
        "name":         "review_status",
        "display_name": "Review Status",
        "type":         "str",
        "section":      "Compliance & Audit",
        "source":       "system",
        "excel_width":  16,
        "required":     False,
        "wrap_text":    False,
        "dashboard":    False,
    },
]


# ---------------------------------------------------------------------------
# PIPELINE THRESHOLDS
# ---------------------------------------------------------------------------

# Records where llm_confidence is below this value are flagged for human review
# in data/review_queue.xlsx. Scale is 0.0–1.0 (set by the LLM in the prompt).
# 0.7 means: "most fields found but some were inferred" — review anything below this.
CONFIDENCE_REVIEW_THRESHOLD = 0.7


# ---------------------------------------------------------------------------
# REFERENCE LISTS — valid values for controlled-vocabulary fields
# These were previously duplicated in extractor.py.
# The AI prompt and validation logic both import from here.
# ---------------------------------------------------------------------------

VALID_CATEGORIES = [
    "RFQ",
    "Manpower Request",
    "Client Enquiry",
    "Proposal Request",
    "Deployment Request",
    "Vendor Communication",
    "Internal Communication",
]

VALID_SECTORS = ["NOC", "OFS", "EPC", "EPCI", "Government", "Other"]

VALID_CONTRACT_TYPES = ["Contract", "Permanent", "Secondment", "Other"]

VALID_URGENCIES = ["High", "Medium", "Low"]

PSL_CATEGORIES = [
    "Artificial Lift", "Cementing", "Coiled Tubing", "Completion",
    "Drilling", "Drilling Fluids", "EPF", "Fishing", "FPSO", "Fracturing",
    "Geology", "HSE", "HWO", "Maintenance", "MLWD", "Mud Engineering",
    "Mud Logging", "Pipeline & Process", "PSCM", "Pumping", "Reservoir",
    "Rig", "Rigless", "Slickline", "Sub Sea", "TCP", "Thru Tubing",
    "Training", "TRS", "Well Completion", "Well Head", "Well Services",
    "Well Testing", "Wireline",
]

REQUIREMENT_STAGES = [
    "Requirement Received",
    "Under Internal Review",
    "Service Order Created",
    "CVs Being Sourced",
    "CVs Requested by Client",
    "CVs Shared with Client",
    "Client Reviewing Profiles",
    "Profiles Shortlisted by Client",
    "Interview Scheduled",
    "Interview Completed",
    "Candidate Selected by Client",
    "Offer Negotiation",
    "Mobilization in Progress",
    "Candidate Mobilized",
    "Position Filled",
    "Requirement Cancelled",
    "Requirement On Hold",
    "No Suitable Candidate",
    "Filled by Competitor",
]


# ---------------------------------------------------------------------------
# COLOUR MAPS — used by storage.py (Excel) and dashboard.py (Streamlit)
# ---------------------------------------------------------------------------

# Status column colour-coding (hex strings without the # prefix — openpyxl format)
STATUS_COLOURS = {
    "New":         "FFF2CC",   # yellow
    "In Progress": "DDEBF7",   # blue
    "Done":        "E2EFDA",   # green
    "On Hold":     "FCE4D6",   # orange
}

# Urgency column colour-coding
URGENCY_COLOURS = {
    "High":   "FFB3B3",   # red-pink
    "Medium": "FFE5B3",   # amber
    "Low":    "D9F0D9",   # light green
}

# Dashboard badge colours (CSS/hex with # prefix — used in Streamlit markdown)
URGENCY_BADGE_COLOURS = {
    "High":   "#ff4b4b",
    "Medium": "#ffa500",
    "Low":    "#21c354",
}


# ---------------------------------------------------------------------------
# DERIVED LOOKUPS — computed once from FIELDS at import time
# Never define these manually elsewhere; always import from here.
# ---------------------------------------------------------------------------

# Ordered list of column names — defines Excel column order
CRM_COLUMNS = [f["name"] for f in FIELDS]

# Dict: column_name → display label (for dashboard table headers)
DISPLAY_NAMES = {f["name"]: f["display_name"] for f in FIELDS}

# Dict: column_name → Excel width
COLUMN_WIDTHS = {f["name"]: f["excel_width"] for f in FIELDS}

# Set of column names that need word-wrap in Excel
WRAP_COLUMNS = {f["name"] for f in FIELDS if f["wrap_text"]}

# Lists of column names grouped by who fills them
LLM_FIELDS    = [f["name"] for f in FIELDS if f["source"] == "llm"]
SYSTEM_FIELDS = [f["name"] for f in FIELDS if f["source"] == "system"]
MANUAL_FIELDS = [f["name"] for f in FIELDS if f["source"] == "manual"]

# List of columns that hold date values (parsed to datetime in dashboard)
DATE_COLUMNS = [f["name"] for f in FIELDS if f["type"] == "date"]

# List of fields marked as required (used for missing-field validation)
REQUIRED_FIELDS = [f["name"] for f in FIELDS if f["required"]]

# List of fields shown in dashboard table views (excludes audit/system noise)
DASHBOARD_FIELDS = [f["name"] for f in FIELDS if f["dashboard"]]

# Dict: section_name → [list of field names in that section]
# Preserves the section order as it appears in FIELDS above.
SECTION_FIELDS = {}
for _f in FIELDS:
    _section = _f["section"]
    SECTION_FIELDS.setdefault(_section, []).append(_f["name"])


# ---------------------------------------------------------------------------
# QUICK TEST — run this file directly to verify the schema is consistent
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=== CRM Schema — config/fields.py ===\n")
    print(f"  Total fields         : {len(FIELDS)}")
    print(f"  LLM-extracted fields : {len(LLM_FIELDS)}")
    print(f"  System-generated     : {len(SYSTEM_FIELDS)}")
    print(f"  Manual (AM fills)    : {len(MANUAL_FIELDS)}")
    print(f"  Required fields      : {len(REQUIRED_FIELDS)}")
    print(f"  Date columns         : {DATE_COLUMNS}")
    print(f"  Wrap-text columns    : {sorted(WRAP_COLUMNS)}")
    print()

    print("  Sections:")
    for section, names in SECTION_FIELDS.items():
        print(f"    {section:<30} {len(names)} fields")

    print()

    # Integrity checks
    errors = []
    names = [f["name"] for f in FIELDS]
    if len(names) != len(set(names)):
        errors.append("DUPLICATE field names found!")
    if len(FIELDS) != 55:
        errors.append(f"Expected 55 fields, got {len(FIELDS)}")
    for f in FIELDS:
        for key in ("name", "display_name", "type", "section", "source",
                    "excel_width", "required", "wrap_text", "dashboard"):
            if key not in f:
                errors.append(f"Field '{f.get('name', '?')}' is missing key: {key}")

    if errors:
        print("  ERRORS:")
        for e in errors:
            print(f"    - {e}")
    else:
        print("  All integrity checks passed.")
