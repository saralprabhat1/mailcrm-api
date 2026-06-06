# psl_splitter.py  —  Phase 11 (PSL-based record splitting)
#
# PURPOSE:
#   Scan an email's subject and body for mentions of any of the 34 PSL categories
#   (Product Service Lines for oil & gas manpower tracking).
#   Each detected PSL becomes a separate CRM record from that email.
#   This is keyword-based detection — fast, no AI call, no API cost.
#
# WHERE IT FITS IN THE PIPELINE:
#   After LLM extraction (Phase 8), the AI returns one row per role it detected.
#   But the AI sometimes misses PSLs that ARE mentioned in the email.
#   This module fills that gap:
#     - Phase 8 LLM  → rows for roles the AI explicitly identified
#     - Phase 11 PSL → extra rows for any PSL the AI missed
#   The two sets are combined before saving to Excel.
#
# FUNCTIONS:
#   detect_psls(subject, body)
#       → list of canonical PSL names found in the email text
#
#   split_by_psl(email_record, detected_psls)
#       → list of minimal CRM row dicts, one per PSL
#         (psl_categories set; other LLM fields blank for manual/AI fill)
#
#   augment_llm_rows(email_record, llm_rows, detected_psls)
#       → combined list: LLM rows + PSL rows for any PSL not already covered
#
# KEYWORD STRATEGY:
#   Each PSL has a list of keywords/phrases.  The PSL name itself is always included.
#   Aliases cover common abbreviations and role titles used in OFS emails.
#   Single-word keywords use \b word boundaries to avoid partial matches
#   (e.g. "rig" does not match "rigging"; "HSE" does not match "HSEQ" unless we list it).
#   Multi-word phrases (e.g. "coiled tubing") are matched as literal substrings.
#   Patterns are compiled once at module load time for speed.

import re
import sys
import hashlib
import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config.fields import PSL_CATEGORIES, CRM_COLUMNS


# ---------------------------------------------------------------------------
# KEYWORD MAP — one entry per PSL category
# Keep keywords specific to oil & gas context to avoid false positives.
# Overlaps between PSLs are intentional: an email can mention both
# "Drilling" and "Mud Engineering" and should produce two separate records.
# ---------------------------------------------------------------------------

PSL_KEYWORDS = {
    "Artificial Lift": [
        "artificial lift", "gas lift", "esp",
        "electric submersible pump", "progressing cavity pump", "pcp",
        "rod pump", "beam pump", "plunger lift", "sucker rod",
    ],
    "Cementing": [
        "cementing", "cement", "well cement", "casing cement",
        "squeeze cement", "plug and abandon", "cement job",
    ],
    "Coiled Tubing": [
        "coiled tubing", "coil tubing", "ct unit", "ctd",
        "coiled tubing engineer", "coiled tubing supervisor", "coiled tubing operator",
    ],
    "Completion": [
        "completion", "completions", "completion engineer", "completion supervisor",
        "wellbore completion", "ohgp", "sand control", "gravel pack",
        "screen installation", "completion design",
    ],
    "Drilling": [
        "drilling engineer", "drilling manager", "drilling supervisor",
        "drilling consultant", "well engineer", "well supervisor",
        "driller", "toolpusher", "assistant driller", "rotary drilling",
        "drill bit", "drill string", "drilling programme", "drilling program",
        "well design", "wellbore", "borehole", "drilling operations",
    ],
    "Drilling Fluids": [
        "drilling fluid", "drilling fluids", "mud system", "fluid system",
        "obm", "wbm", "naf", "sobm", "oil based mud", "water based mud",
        "mud weight", "fluid program", "mud program", "rheology",
        "drilling fluids engineer",
    ],
    "EPF": [
        "epf", "early production facility", "early production",
    ],
    "Fishing": [
        "fishing", "fishing supervisor", "fishing tool",
        "stuck pipe", "junk retrieval", "junk basket",
        "freeing pipe", "stuck string", "fish retrieval",
    ],
    "FPSO": [
        "fpso", "floating production", "floating storage",
        "fso", "fsru", "offloading", "mooring", "turret",
    ],
    "Fracturing": [
        "fracturing", "hydraulic fracturing", "fracking",
        "frac", "stimulation", "acid stimulation", "acidizing",
        "pump down", "fracture design", "frac engineer", "frac supervisor",
    ],
    "Geology": [
        "geology", "geologist", "geological",
        "stratigraphy", "formation evaluation", "sedimentology",
        "geomechanics", "geosteering", "biostratigraphy", "petrophysics",
        "petrophysicist", "formation logging",
    ],
    "HSE": [
        "hse", "health safety", "safety officer", "safety supervisor",
        "safety engineer", "safety manager", "safety advisor",
        "ehs", "loss prevention", "hazid", "hazop",
        "nebosh", "iosh", "safety consultant",
    ],
    "HWO": [
        "hwo", "hydraulic workover", "workover supervisor",
        "workover engineer", "workover unit", "workover rig",
        "workover operations",
    ],
    "Maintenance": [
        "maintenance engineer", "maintenance technician", "maintenance planner",
        "maintenance superintendent", "mechanical maintenance",
        "instrument maintenance", "electrical maintenance",
        "e&i technician", "electrical instrumentation",
        "static equipment", "rotating equipment",
    ],
    "MLWD": [
        "mlwd", "mwd engineer", "lwd engineer",
        "measurement while drilling", "logging while drilling",
        "directional drilling", "directional driller", "directional engineer",
        "steerable", "rotary steerable", "rss",
        "mwd supervisor", "lwd supervisor",
    ],
    "Mud Engineering": [
        "mud engineering", "mud engineer",
        "drilling fluid engineer", "fluid engineer",
        "mud specialist",
    ],
    "Mud Logging": [
        "mud logging", "mud logger",
        "geological logging", "sample logging",
        "gas detection", "sample catching",
    ],
    "Pipeline & Process": [
        "pipeline", "pipeline engineer", "pipeline inspector",
        "pipeline construction", "pipeline supervisor",
        "process engineer", "process facility", "processing plant",
        "piping engineer", "flow assurance", "cswip",
        "pipeline integrity", "cathodic protection",
    ],
    "PSCM": [
        "pscm", "procurement", "supply chain",
        "contracts manager", "materials management",
        "logistics", "purchasing", "vendor management",
        "supply chain management", "scm", "buyer",
    ],
    "Pumping": [
        "pumping services", "pump operator", "pump technician",
        "high pressure pump", "pumping engineer",
        "well pumping", "pump supervisor",
    ],
    "Reservoir": [
        "reservoir engineer", "reservoir engineering",
        "reservoir simulation", "simulation engineer",
        "petrel", "eclipse", "reservoir management",
        "production engineer", "production optimization",
        "reservoir consultant",
    ],
    "Rig": [
        "rig manager", "rig superintendent", "rig supervisor",
        "rig operation", "rig move",
        "jack-up", "jackup", "semisubmersible", "semi-submersible",
        "drillship", "tender rig", "barge rig",
        "land rig", "offshore rig",
    ],
    "Rigless": [
        "rigless", "rig-less",
        "rigless operation", "rigless intervention",
        "rigless completion",
    ],
    "Slickline": [
        "slickline", "slick line",
        "slickline operator", "slickline supervisor", "slickline engineer",
        "mechanical wireline", "braided line", "swabbing", "gauge run",
    ],
    "Sub Sea": [
        "subsea", "sub-sea", "sub sea",
        "umbilical", "riser", "subsea engineer", "subsea tree",
        "bop", "blowout preventer", "rov",
        "subsea system", "surf", "subsea structure",
    ],
    "TCP": [
        "tcp gun", "tubing conveyed perforating", "tubing conveyed",
        "tcp perforating", "tcp assembly",
    ],
    "Thru Tubing": [
        "thru tubing", "through tubing", "through-tubing", "thru-tubing",
        "tt tools", "thru-tubing intervention", "through tubing operations",
    ],
    "Training": [
        "training", "trainer", "instructor",
        "training center", "training programme", "training program",
        "competency assessment", "competency training",
        "well control instructor", "training coordinator",
    ],
    "TRS": [
        "trs", "tubular running", "tubular running services",
        "casing running", "casing running tools",
        "tubing running", "liner hanger", "rtts",
    ],
    "Well Completion": [
        "well completion", "well completion engineer",
        "well completion supervisor",
        "wellbore completion", "perforating",
        "gun system", "perforating gun",
    ],
    "Well Head": [
        "wellhead", "well head",
        "christmas tree", "x-mas tree", "xmas tree",
        "wellhead technician", "wellhead engineer",
        "surface wellhead", "tree installation",
        "wellhead maintenance",
    ],
    "Well Services": [
        "well services", "well service",
        "well intervention", "well maintenance",
        "production logging", "well operations",
        "well services engineer",
    ],
    "Well Testing": [
        "well testing", "well test",
        "dst", "drillstem test",
        "production test", "production testing",
        "test separator", "well test engineer", "well testing engineer",
        "dst supervisor", "production well test",
    ],
    "Wireline": [
        "wireline", "wire line",
        "e-line", "electric line",
        "open hole wireline", "cased hole wireline",
        "wireline engineer", "wireline operator", "wireline supervisor",
        "logging engineer", "open hole logging", "cased hole logging",
    ],
}


# ---------------------------------------------------------------------------
# COMPILE PATTERNS — done once at module load, not inside detect_psls()
#
# WHY PRE-COMPILE:
#   If detect_psls() is called for every email in a run of 100 emails,
#   we would compile 34 regex patterns × 100 times = 3400 compilations.
#   Compiling once here means we compile 34 patterns total, ever.
#
# PATTERN LOGIC:
#   - Multi-word phrases (e.g. "artificial lift"): match as literal string,
#     no word boundary needed — the spaces already prevent partial matches.
#   - Single words / acronyms (e.g. "HSE", "esp", "mwd"): wrap in \b...\b
#     so "esp" doesn't match "especially" and "hse" doesn't match "hseq".
# ---------------------------------------------------------------------------

def _build_pattern(keywords):
    """
    Build a single compiled regex from a list of keywords.
    Returns a re.Pattern object ready for re.search().
    """
    parts = []
    for kw in keywords:
        escaped = re.escape(kw)
        if " " in kw or "-" in kw:
            # Multi-word or hyphenated phrase — spaces/hyphens prevent partial matches
            parts.append(escaped)
        else:
            # Single word or acronym — word boundaries prevent partial matches
            parts.append(r"\b" + escaped + r"\b")

    return re.compile("|".join(parts), re.IGNORECASE)


# Dict: PSL name → compiled regex pattern
# Built once at import time
_PSL_PATTERNS = {
    psl: _build_pattern(keywords)
    for psl, keywords in PSL_KEYWORDS.items()
}

# Fields that come from the email as a whole (not per-role).
# Used by augment_llm_rows() to copy these from the first LLM row
# into any PSL-only rows it creates — so the AM doesn't see a blank client name.
_COMMON_EMAIL_FIELDS = [
    "client_name", "client_country", "client_sector",
    "contact_person", "contact_email", "contact_phone", "client_ref_number",
    "location", "mobilization_date", "duration", "contract_type",
    "work_schedule", "nationality_preference", "project_name",
    "urgency", "category", "requirement_stage", "deadline",
    "email_summary", "next_action",
    "language_detected", "llm_confidence", "missing_fields_flag",
]


# ---------------------------------------------------------------------------
# PUBLIC FUNCTION 1 — detect_psls
# ---------------------------------------------------------------------------

def detect_psls(subject, body):
    """
    Scan an email's subject and body for any of the 34 PSL categories.

    Searches the combined text (subject + body) using pre-compiled keyword
    patterns.  Returns only canonical PSL names from PSL_CATEGORIES.

    Parameters:
        subject — email subject line (string)
        body    — plain-text email body (string)

    Returns:
        List of PSL category names (e.g. ["Drilling", "HSE", "Wireline"]).
        Empty list if no PSL keywords were found.
        List is in the same order as PSL_CATEGORIES (canonical order).
    """
    # Combine subject and body so a PSL mentioned in the subject is also detected
    combined_text = (str(subject) + " " + str(body)).strip()

    if not combined_text:
        return []

    detected = []

    # Check every PSL pattern against the combined text.
    # We iterate in PSL_CATEGORIES order so the returned list is always consistent.
    for psl in PSL_CATEGORIES:
        pattern = _PSL_PATTERNS.get(psl)
        if pattern and pattern.search(combined_text):
            detected.append(psl)

    return detected


# ---------------------------------------------------------------------------
# PUBLIC FUNCTION 2 — split_by_psl
# ---------------------------------------------------------------------------

def split_by_psl(email_record, detected_psls):
    """
    Create one minimal CRM row dict for each detected PSL category.

    These rows have the same 55-field structure as rows from build_multi_role_rows()
    in extractor.py.  Fields that require LLM extraction (designation, rates,
    technical requirements, etc.) are left blank — the AM or a later AI pass fills them.

    Parameters:
        email_record   — email dict from email_reader.fetch_emails()
        detected_psls  — list of PSL names returned by detect_psls()

    Returns:
        List of CRM row dicts, one per PSL.  Empty list if detected_psls is empty.
    """
    if not detected_psls:
        return []

    # Pull the email metadata fields we can populate without LLM
    email_id     = email_record.get("email_id", "")
    subject      = email_record.get("subject", "")
    sender_email = email_record.get("sender_email", "")
    sender_name  = email_record.get("sender_name", "")
    has_attach   = email_record.get("has_attachments", False)

    received_raw  = email_record.get("received_date", "")
    received_date = received_raw[:10] if received_raw else ""

    # Build a 6-char hash of the email_id for the req_id (same approach as extractor.py)
    id_hash  = hashlib.md5(email_id.encode()).hexdigest()[:6].upper() if email_id else "000000"
    date_str = datetime.date.today().strftime("%Y%m%d")

    total_psls = len(detected_psls)
    rows = []

    for i, psl in enumerate(detected_psls, start=1):

        # PSL-split req_ids use "P" suffix to distinguish from LLM role rows.
        # e.g. REQ-20260605-A3F7B2-P01, REQ-20260605-A3F7B2-P02
        req_id = f"REQ-{date_str}-{id_hash}-P{i:02d}"

        # Build a full 55-field row dict.
        # Start with all fields set to "" (blank), then fill what we know.
        row = {col: "" for col in CRM_COLUMNS}

        # ---- Section 1: Identity & System ------------------------------------
        row["req_id"]        = req_id
        row["email_id"]      = email_id
        row["received_date"] = received_date
        row["subject"]       = subject
        row["source_mailbox"]= sender_email
        row["am_name"]       = ""

        # ---- Section 2: Client Information -----------------------------------
        # Client details are blank — LLM or AM fills them later.
        # psl_categories is the one field we DO know for certain.
        row["psl_categories"] = psl

        # ---- Section 4: Stage & Status ---------------------------------------
        row["status"]            = "New"
        row["requirement_stage"] = "Requirement Received"

        # ---- Section 7: Compliance & Audit -----------------------------------
        row["sender_email"]        = sender_email
        row["sender_name"]         = sender_name
        row["has_attachments"]     = "Yes" if has_attach else "No"
        row["is_follow_up"]        = "No"
        row["total_roles_in_email"]= total_psls
        row["role_index"]          = f"{i} of {total_psls}"
        row["processing_log"]      = (
            f"PSL split {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')} "
            f"| keyword match | psl: {psl}"
        )
        row["review_status"]       = "Pending Review"

        rows.append(row)

    return rows


# ---------------------------------------------------------------------------
# PUBLIC FUNCTION 3 — augment_llm_rows
# ---------------------------------------------------------------------------

def augment_llm_rows(email_record, llm_rows, detected_psls):
    """
    Add PSL-only rows for any PSL that the LLM did not already produce a row for.

    Use this AFTER build_multi_role_rows() to make sure every PSL mentioned
    in the email gets at least one CRM record, even if the LLM missed it.

    Logic:
      1. Collect all PSL values already present in the LLM rows.
      2. Find PSLs from detected_psls that are NOT in that set.
      3. Call split_by_psl() for those uncovered PSLs.
      4. For each new PSL row, copy the common email-level fields (client name,
         location, dates, etc.) from the first LLM row so the record isn't blank.
      5. Return the combined list: LLM rows first, then PSL-only rows.

    Parameters:
        email_record  — email dict from email_reader.fetch_emails()
        llm_rows      — list of CRM row dicts from build_multi_role_rows()
        detected_psls — list of PSL names from detect_psls()

    Returns:
        Combined list.  If all PSLs are already covered, returns llm_rows unchanged.
    """
    if not detected_psls:
        # Nothing detected by keyword scan — nothing to add
        return llm_rows

    # Step 1: Which PSLs are the LLM rows already covering?
    # A PSL is "covered" if any LLM row has that value in psl_categories.
    covered_psls = set()
    for row in llm_rows:
        psl_val = str(row.get("psl_categories", "")).strip()
        if psl_val:
            covered_psls.add(psl_val)

    # Step 2: Which PSLs did keyword detection find that LLM rows don't cover?
    uncovered_psls = [p for p in detected_psls if p not in covered_psls]

    if not uncovered_psls:
        # LLM already has a row for every detected PSL — nothing to add
        return llm_rows

    print(f"  PSL splitter: LLM covered {sorted(covered_psls)}")
    print(f"  PSL splitter: adding rows for uncovered PSLs: {uncovered_psls}")

    # Step 3: Build PSL-only rows for the uncovered PSLs
    psl_rows = split_by_psl(email_record, uncovered_psls)

    # Step 4: Copy common email-level fields from the first LLM row into each PSL row.
    # This avoids creating records with a blank client name when the LLM already
    # extracted the client and location for this email.
    if llm_rows:
        reference_row = llm_rows[0]
        for psl_row in psl_rows:
            for field in _COMMON_EMAIL_FIELDS:
                value = reference_row.get(field, "")
                if value:   # only copy if the LLM actually found something
                    psl_row[field] = value

    # Step 5: LLM rows come first (they have more detail); PSL rows are supplementary
    return llm_rows + psl_rows


# ---------------------------------------------------------------------------
# QUICK TEST — run this file directly to verify keyword detection
# ---------------------------------------------------------------------------

if __name__ == "__main__":

    print("=" * 65)
    print("  PSL SPLITTER — Phase 11 — Keyword Detection Test")
    print("=" * 65)

    print(f"\n  PSL categories covered : {len(PSL_KEYWORDS)}")
    print(f"  Canonical PSL count    : {len(PSL_CATEGORIES)}")

    # Check that every canonical PSL has a keyword entry
    missing = [p for p in PSL_CATEGORIES if p not in PSL_KEYWORDS]
    if missing:
        print(f"\n  WARNING: No keywords defined for: {missing}")
    else:
        print(f"  All 34 PSLs have keyword entries.")

    # Test 1: single-PSL email
    test_cases = [
        {
            "label":   "Drilling only",
            "subject": "Manpower Request - 2 Drilling Engineers - Khurais",
            "body":    "We require 2 Senior Drilling Engineers for Khurais Field. "
                       "Rate $850/day. IWCF required. Mobilization July 2025.",
            "expect":  ["Drilling"],
        },
        {
            "label":   "Multi-PSL email",
            "subject": "RFQ - Multiple Positions - Abu Dhabi",
            "body":    "ADNOC Drilling requires: 1 Toolpusher, 2 MWD Engineers, "
                       "1 HSE Supervisor, 1 Wireline Operator. 28/28 rotation. "
                       "Abu Dhabi onshore.",
            "expect":  ["Drilling", "HSE", "MLWD", "Wireline"],
        },
        {
            "label":   "FPSO + Subsea",
            "subject": "Manpower - FPSO Marine Superintendent + Subsea Engineer",
            "body":    "Shell requires a Marine Superintendent for their FPSO Bonga "
                       "offshore Nigeria. Also looking for an experienced Subsea Engineer "
                       "with ROV experience for SURF installation.",
            "expect":  ["FPSO", "Sub Sea"],
        },
        {
            "label":   "Well Testing + Cementing",
            "subject": "Requirement - Well Test Engineer + Cementing Supervisor",
            "body":    "QatarEnergy requires a Well Testing Engineer for DST operations "
                       "and a Cementing Supervisor for our North Field project. "
                       "Both positions 28/28 rotation. Start October 2025.",
            "expect":  ["Cementing", "Well Testing"],
        },
        {
            "label":   "Artificial Lift (ESP)",
            "subject": "Fw: ESP Engineer Required - Oman PDO",
            "body":    "PDO requires an ESP (Electric Submersible Pump) Engineer for "
                       "artificial lift operations at Marmul field. 6-month contract.",
            "expect":  ["Artificial Lift"],
        },
        {
            "label":   "Unrelated email (no PSLs)",
            "subject": "Invoice #INV-2025-0442 - Manpower Services",
            "body":    "Please find attached invoice for manpower services in April 2025. "
                       "Total amount USD 48500. Payment due in 30 days.",
            "expect":  [],
        },
    ]

    all_passed = True

    for tc in test_cases:
        detected = detect_psls(tc["subject"], tc["body"])
        # Check that all expected PSLs are in detected (may detect more — that's fine)
        expected_found = all(p in detected for p in tc["expect"])
        no_false_blocks = True   # We allow extra detections, not missed ones

        status = "PASS" if expected_found else "FAIL"
        if not expected_found:
            all_passed = False

        print(f"\n  [{status}] {tc['label']}")
        print(f"    Expected (min): {tc['expect']}")
        print(f"    Detected      : {detected}")

    print()
    if all_passed:
        print("  All detection tests passed.")
    else:
        print("  Some tests failed — review PSL_KEYWORDS entries above.")

    print()
    print("=" * 65)
    print("  SPLIT TEST — split_by_psl() row structure")
    print("=" * 65)

    sample_email = {
        "email_id":       "test-phase11-001",
        "received_date":  "2026-06-05T10:00:00Z",
        "subject":        "RFQ - Drilling Engineers and HSE Supervisor - Kuwait",
        "sender_name":    "Khalid Al-Mansoori",
        "sender_email":   "khalid@kockw.com",
        "has_attachments": False,
    }

    detected_psls = detect_psls(
        sample_email["subject"],
        "KOC requires 2 Senior Drilling Engineers and 1 HSE Supervisor. "
        "Rate $800/day. NEBOSH required for HSE role.",
    )
    print(f"\n  Detected PSLs : {detected_psls}")

    rows = split_by_psl(sample_email, detected_psls)
    print(f"  Rows created  : {len(rows)}")

    for row in rows:
        print(f"\n  req_id        : {row['req_id']}")
        print(f"  psl_categories: {row['psl_categories']}")
        print(f"  status        : {row['status']}")
        print(f"  review_status : {row['review_status']}")
        print(f"  processing_log: {row['processing_log']}")
        print(f"  Field count   : {len(row)} / {len(CRM_COLUMNS)} expected")
        missing_fields = [c for c in CRM_COLUMNS if c not in row]
        if missing_fields:
            print(f"  MISSING KEYS  : {missing_fields}")
        else:
            print(f"  All 55 field keys present.")
