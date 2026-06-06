# role_taxonomy.py
# PURPOSE: Define the ~380-role taxonomy for oil & gas manpower, organised by PSL category.
#
# USED BY: extractor.py — the AI prompt references PSL category names from this file,
# and detect_roles_in_text() gives a fallback role-detection pass on raw email text.
#
# HOW IT WORKS:
#   ROLE_TAXONOMY  — dict: {psl_category: [list of role titles]}
#   ALL_ROLES      — flat set for fast "is this string a known role?" checks
#   ROLE_TO_PSL    — reverse lookup: role title → PSL category
#   detect_roles_in_text() — scans email text, returns every known role it finds
#   get_psl_for_role()     — maps a single designation to its PSL category

# ---------------------------------------------------------------------------
# ROLE TAXONOMY — 34 PSL categories, ~380 role titles
# ---------------------------------------------------------------------------

ROLE_TAXONOMY = {

    "Drilling": [
        "Drilling Engineer",
        "Senior Drilling Engineer",
        "Drilling Supervisor",
        "Rig Superintendent",
        "Senior Rig Superintendent",
        "Toolpusher",
        "Senior Toolpusher",
        "Driller",
        "Senior Driller",
        "Assistant Driller",
        "Derrickman",
        "Floorman",
        "Motorman",
        "Crane Operator",
        "Roughneck",
        "Roustabout",
        "Drilling Foreman",
        "Well Site Leader",
        "Directional Driller",
        "Rig Manager",
        "Drilling Project Manager",
        "Drilling Operations Manager",
        "Drilling Consultant",
        "Area Drilling Manager",
        "Wellbore Engineer",
    ],

    "Drilling Fluids": [
        "Drilling Fluids Engineer",
        "Senior Drilling Fluids Engineer",
        "Drilling Fluids Specialist",
        "Drilling Fluids Coordinator",
        "Fluids Systems Engineer",
        "Drilling Fluids Supervisor",
        "Drilling Fluids Technician",
        "Mud Engineer",
        "Senior Mud Engineer",
        "Chief Mud Engineer",
    ],

    "MLWD": [
        "MWD Engineer",
        "LWD Engineer",
        "Senior MWD Engineer",
        "Senior LWD Engineer",
        "MWD/LWD Engineer",
        "Directional Driller (MWD)",
        "MWD Operator",
        "LWD Operator",
        "MWD Supervisor",
        "LWD Specialist",
        "Formation Evaluation Engineer",
        "Petrophysicist (MLWD)",
        "MWD/LWD Supervisor",
        "Real Time Operations Engineer",
        "MWD Consultant",
        "LWD Consultant",
    ],

    "Cementing": [
        "Cementing Engineer",
        "Senior Cementing Engineer",
        "Field Cementing Engineer",
        "Cementing Supervisor",
        "Cementing Operator",
        "Cementing Specialist",
        "Bulk Plant Operator",
        "Cementing Crew Chief",
        "Cementing Coordinator",
        "Well Services Engineer (Cementing)",
        "Cementing Project Manager",
        "Slurry Design Engineer",
        "Cementing Consultant",
    ],

    "Coiled Tubing": [
        "Coiled Tubing Engineer",
        "Senior Coiled Tubing Engineer",
        "CT Supervisor",
        "CT Operator",
        "CT Field Supervisor",
        "Coiled Tubing Specialist",
        "CT Crew Supervisor",
        "CT Field Engineer",
        "Coiled Tubing Foreman",
        "CT Equipment Operator",
    ],

    "Completion": [
        "Completion Engineer",
        "Senior Completion Engineer",
        "Completion Supervisor",
        "Well Completion Specialist",
        "Completion Foreman",
        "Completion Technician",
        "Downhole Completion Engineer",
        "Sand Control Engineer",
        "Gravel Pack Engineer",
        "Subsurface Completion Engineer",
        "Completion Operations Supervisor",
        "Wellbore Completion Engineer",
        "Completion Data Engineer",
        "Multilateral Well Engineer",
        "Intelligent Completion Engineer",
    ],

    "Fracturing": [
        "Fracturing Engineer",
        "Senior Fracturing Engineer",
        "Stimulation Engineer",
        "Fracturing Supervisor",
        "Pumping Supervisor",
        "Frac Field Engineer",
        "Stimulation Specialist",
        "Pumping Operator",
        "Fracturing Coordinator",
        "Perforation Engineer (Frac)",
    ],

    "Wireline": [
        "Wireline Engineer",
        "Senior Wireline Engineer",
        "Field Engineer (Wireline)",
        "Wireline Supervisor",
        "Wireline Operator",
        "Cased Hole Engineer",
        "Open Hole Engineer",
        "Wireline Field Specialist",
        "Wireline Crew Chief",
        "Perforating Engineer",
        "Wireline Evaluation Engineer",
        "Wireline Technician",
    ],

    "Slickline": [
        "Slickline Engineer",
        "Senior Slickline Engineer",
        "Slickline Operator",
        "Slickline Supervisor",
        "Slickline Crew Chief",
        "Slickline Specialist",
        "Slickline Field Engineer",
        "Slickline Technician",
    ],

    "Well Testing": [
        "Well Testing Engineer",
        "Senior Well Testing Engineer",
        "Well Test Supervisor",
        "DST Engineer",
        "Well Test Operator",
        "Surface Testing Engineer",
        "Production Testing Engineer",
        "Well Testing Specialist",
        "Well Testing Foreman",
        "Test Separator Operator",
        "Well Test Project Manager",
        "Well Testing Consultant",
        "Surface Equipment Operator",
    ],

    "Thru Tubing": [
        "Thru Tubing Engineer",
        "Senior Thru Tubing Engineer",
        "Thru Tubing Specialist",
        "Thru Tubing Supervisor",
        "Thru Tubing Operator",
        "Thru Tubing Field Engineer",
        "Intervention Specialist",
        "Thru Tubing Crew Chief",
    ],

    "Well Services": [
        "Well Services Engineer",
        "Senior Well Services Engineer",
        "Well Services Supervisor",
        "Well Intervention Engineer",
        "Well Services Field Engineer",
        "Service Technician",
        "Well Services Coordinator",
        "Well Services Manager",
        "Field Service Engineer",
        "Service Line Manager",
        "Well Services Project Manager",
        "Senior Field Service Engineer",
    ],

    "Well Completion": [
        "Well Completion Engineer",
        "Senior Well Completion Engineer",
        "Well Completion Supervisor",
        "Subsurface Engineer",
        "Well Completion Coordinator",
        "Well Completion Specialist",
        "Well Completion Project Manager",
        "Production Engineer (Well Completion)",
    ],

    "Well Head": [
        "Wellhead Engineer",
        "Senior Wellhead Engineer",
        "Wellhead Technician",
        "Wellhead Supervisor",
        "Christmas Tree Operator",
        "Wellhead Operator",
        "Wellhead Maintenance Technician",
        "Wellhead Field Engineer",
    ],

    "HWO": [
        "Hydraulic Workover Engineer",
        "Senior HWO Engineer",
        "HWO Supervisor",
        "HWO Operator",
        "HWO Specialist",
        "HWO Foreman",
        "Workover Engineer",
        "Workover Supervisor",
    ],

    "Rigless": [
        "Rigless Operations Engineer",
        "Rigless Supervisor",
        "Rigless Specialist",
        "ESP Engineer",
        "ESP Technician",
        "Rigless Field Engineer",
        "Rigless Operations Supervisor",
        "Pump Technician",
    ],

    "TCP": [
        "TCP Engineer",
        "Senior TCP Engineer",
        "Perforation Engineer",
        "TCP Specialist",
        "TCP Field Engineer",
        "Perforation Supervisor",
    ],

    "Fishing": [
        "Fishing Engineer",
        "Senior Fishing Engineer",
        "Fishing Supervisor",
        "Fishing Specialist",
        "Tool Specialist (Fishing)",
        "Junk Milling Engineer",
        "Well Recovery Engineer",
        "Fishing Tool Operator",
    ],

    "Sub Sea": [
        "Subsea Engineer",
        "Senior Subsea Engineer",
        "Subsea Supervisor",
        "ROV Pilot",
        "ROV Supervisor",
        "Subsea Technician",
        "Subsea Installation Engineer",
        "Subsea Pipeline Engineer",
        "Subsea Structures Engineer",
        "Subsea Project Engineer",
        "Diving Supervisor",
        "Saturation Diver",
        "Subsea Control Engineer",
        "Subsea Asset Integrity Engineer",
    ],

    "Pipeline & Process": [
        "Pipeline Engineer",
        "Senior Pipeline Engineer",
        "Process Engineer",
        "Pipeline Inspector",
        "Piping Engineer",
        "Pipeline Supervisor",
        "Pipeline Field Engineer",
        "Pipeline Integrity Engineer",
        "Flow Assurance Engineer",
        "Corrosion Engineer",
        "Pipeline Technician",
        "Process Supervisor",
        "Pipeline Project Manager",
        "Process Safety Engineer (Pipeline)",
    ],

    "FPSO": [
        "FPSO Engineer",
        "FPSO Superintendent",
        "FPSO Operations Manager",
        "FPSO Commissioning Engineer",
        "Marine Superintendent",
        "Production Operator (FPSO)",
        "FPSO Maintenance Engineer",
        "FPSO Safety Officer",
        "Topsides Engineer",
        "Mooring Engineer",
        "FPSO Project Engineer",
        "FPSO Technician",
        "FPSO Operations Superintendent",
        "FPSO Process Engineer",
    ],

    "EPF": [
        "EPF Engineer",
        "EPF Superintendent",
        "EPF Commissioning Engineer",
        "Process Facility Engineer",
        "EPF Operations Manager",
        "EPF Technician",
        "EPF Supervisor",
        "Facility Engineer",
        "Production Facility Engineer",
        "EPF Maintenance Engineer",
    ],

    "Reservoir": [
        "Reservoir Engineer",
        "Senior Reservoir Engineer",
        "Reservoir Geologist",
        "Petrophysicist",
        "Reservoir Simulation Engineer",
        "Reservoir Characterization Engineer",
        "Production Geologist",
        "Geomodeller",
        "Static Modelling Engineer",
        "Dynamic Modelling Engineer",
        "Enhanced Oil Recovery Engineer",
        "Reservoir Data Analyst",
    ],

    "Geology": [
        "Geologist",
        "Senior Geologist",
        "Wellsite Geologist",
        "Formation Evaluation Geologist",
        "Sedimentologist",
        "Stratigrapher",
        "Structural Geologist",
        "Exploration Geologist",
        "Geological Engineer",
        "Mud Logger (Geology)",
        "Senior Exploration Geologist",
        "Geophysicist",
        "Seismic Interpreter",
    ],

    "Pumping": [
        "Pumping Engineer",
        "Senior Pumping Engineer",
        "Pumping Supervisor",
        "Pump Operator",
        "Field Pumping Engineer",
        "Pumping Crew Chief",
        "Pump Technician (Pumping)",
        "High Pressure Pumping Engineer",
    ],

    "Mud Engineering": [
        "Mud Engineer",
        "Senior Mud Engineer",
        "Chief Mud Engineer",
        "Drilling Fluids Engineer (Mud)",
        "Mud Engineering Supervisor",
        "Mud Specialist",
        "Mud Engineering Coordinator",
        "Mud Engineer (Deepwater)",
    ],

    "Mud Logging": [
        "Mud Logger",
        "Senior Mud Logger",
        "Chief Mud Logger",
        "Mud Logging Engineer",
        "Unit Supervisor (Mud Logging)",
        "Mud Logging Data Engineer",
        "Formation Evaluation Mud Logger",
        "Geologist Mud Logger",
    ],

    "Rig": [
        "Rig Manager",
        "Rig Superintendent",
        "Senior Rig Superintendent",
        "Rig Toolpusher",
        "Rig Foreman",
        "Rig Mechanic",
        "Rig Electrician",
        "Rig Crane Operator",
        "Rig Safety Officer",
        "Rig Medic",
        "Rig Welder",
        "Rig Clerk",
        "Rig Operations Manager",
        "Rig Commissioning Engineer",
    ],

    "Artificial Lift": [
        "Artificial Lift Engineer",
        "Senior Artificial Lift Engineer",
        "ESP Engineer (Artificial Lift)",
        "Gas Lift Engineer",
        "Gas Lift Supervisor",
        "Rod Pump Technician",
        "Pump Jack Technician",
        "ESP Field Engineer",
        "Artificial Lift Specialist",
        "Artificial Lift Supervisor",
    ],

    "HSE": [
        "HSE Engineer",
        "Senior HSE Engineer",
        "HSE Supervisor",
        "HSE Manager",
        "Safety Officer",
        "HSE Coordinator",
        "Environmental Engineer",
        "Process Safety Engineer",
        "HSE Advisor",
        "HSE Auditor",
        "Safety Engineer",
        "Loss Prevention Engineer",
        "Emergency Response Coordinator",
    ],

    "Maintenance": [
        "Maintenance Engineer",
        "Senior Maintenance Engineer",
        "Mechanical Engineer",
        "Electrical Engineer",
        "Instrument Engineer",
        "Maintenance Supervisor",
        "Reliability Engineer",
        "Maintenance Technician",
        "Preventive Maintenance Engineer",
        "Maintenance Planner",
        "Rotating Equipment Engineer",
        "Condition Monitoring Engineer",
    ],

    "Training": [
        "Training Coordinator",
        "Technical Trainer",
        "HSE Trainer",
        "Drilling Trainer",
        "Operations Trainer",
        "Competency Assessor",
        "Training Manager",
        "OFS Instructor",
        "Well Control Instructor",
        "Training Quality Assessor",
        "E-Learning Developer",
        "Technical Writing Specialist",
    ],

    "PSCM": [
        "Procurement Manager",
        "Supply Chain Manager",
        "Logistics Coordinator",
        "Materials Manager",
        "PSCM Analyst",
        "Procurement Engineer",
        "Vendor Manager",
        "Materials Coordinator",
        "Supply Chain Analyst",
        "Contract Administrator",
        "Procurement Specialist",
        "Inventory Management Specialist",
    ],

    "TRS": [
        "Technical Recruiter",
        "Senior Technical Recruiter",
        "TRS Coordinator",
        "Recruitment Manager",
        "HR Business Partner",
        "Talent Acquisition Specialist",
        "Technical Staffing Specialist",
        "TRS Manager",
    ],
}


# ---------------------------------------------------------------------------
# DERIVED LOOKUPS — built once at import time, used throughout the codebase
# ---------------------------------------------------------------------------

# Flat set of all role titles — for fast "is this a known role?" checks
ALL_ROLES = {role for roles in ROLE_TAXONOMY.values() for role in roles}

# Reverse lookup: role title → PSL category
ROLE_TO_PSL = {
    role: psl_category
    for psl_category, roles in ROLE_TAXONOMY.items()
    for role in roles
}

# Total count (for documentation purposes)
ROLE_COUNT = len(ALL_ROLES)


# ---------------------------------------------------------------------------
# FUNCTIONS
# ---------------------------------------------------------------------------

def detect_roles_in_text(text: str) -> list:
    """
    Scan email text and return every known role title found in it.

    This is a fallback check used AFTER the AI extraction.
    If the AI missed a role that's clearly in the text, this catches it.

    Parameters:
        text — raw email text (subject + body)

    Returns:
        List of (role_title, psl_category) tuples, in order of appearance.
        Example: [("Drilling Engineer", "Drilling"), ("HSE Supervisor", "HSE")]
    """
    text_lower = text.lower()
    found = []
    seen = set()  # Avoid duplicate entries

    for role, psl_category in ROLE_TO_PSL.items():
        if role.lower() in text_lower and role not in seen:
            found.append((role, psl_category))
            seen.add(role)

    return found


def get_psl_for_role(designation: str) -> str:
    """
    Return the PSL category for a given designation/job title.
    Tries exact match first, then case-insensitive match.
    Returns 'Other' if the role is not in the taxonomy.

    Parameters:
        designation — job title string (e.g. "Drilling Engineer")

    Returns:
        PSL category string (e.g. "Drilling") or "Other"
    """
    if not designation:
        return "Other"

    # Exact match (fastest)
    if designation in ROLE_TO_PSL:
        return ROLE_TO_PSL[designation]

    # Case-insensitive fallback
    designation_lower = designation.lower()
    for role, psl_category in ROLE_TO_PSL.items():
        if role.lower() == designation_lower:
            return psl_category

    return "Other"


def get_roles_for_psl(psl_category: str) -> list:
    """
    Return all known role titles for a given PSL category.

    Parameters:
        psl_category — e.g. "Drilling" or "HSE"

    Returns:
        List of role title strings, or empty list if PSL not found.
    """
    return ROLE_TAXONOMY.get(psl_category, [])


# ---------------------------------------------------------------------------
# QUICK TEST — run this file directly to verify the taxonomy loaded correctly
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print(f"=== Role Taxonomy Loaded ===")
    print(f"  PSL Categories : {len(ROLE_TAXONOMY)}")
    print(f"  Total Roles    : {ROLE_COUNT}")
    print()

    # Show per-category counts
    print("  Category breakdown:")
    for psl, roles in ROLE_TAXONOMY.items():
        print(f"    {psl:<25} {len(roles)} roles")

    print()

    # Demo: detect roles in a sample email snippet
    sample = """
    We require 2 Drilling Engineers and 1 HSE Supervisor for our Khurais project.
    The Mud Logger should have 5 years experience. MWD Engineer also required.
    """
    detected = detect_roles_in_text(sample)
    print(f"  Demo detection in sample text:")
    for role, psl in detected:
        print(f"    {role:<35} -> {psl}")

    print()
    print(f"  PSL for 'Wireline Engineer': {get_psl_for_role('Wireline Engineer')}")
    print(f"  PSL for 'Unknown Role':      {get_psl_for_role('Unknown Role')}")
