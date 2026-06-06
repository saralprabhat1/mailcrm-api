# config/email_filters.py
# PURPOSE: Domain whitelist for the CRM email pipeline.
#
# ONLY emails from domains on the ALLOWED_DOMAINS list are processed.
# Everything else is silently dropped before parsing, AI extraction, or storage.
#
# ============================================================================
# HOW TO EDIT THIS FILE (no Python knowledge required)
# ============================================================================
#
#   To ADD a new client domain:
#       Find the right section below and add a new line:
#           "newclient.com",
#       (The comma at the end is required. The quotes are required.)
#
#   To REMOVE a domain:
#       Delete its line entirely, or add a # in front to comment it out.
#
#   To BLOCK your own company domain (REQUIRED before going live):
#       Find EXCLUDED_DOMAINS below and replace "getglobal.com" with the
#       actual company email domain from your Outlook account.
#
#   Rules are re-read every time the pipeline runs — no restart needed.
#
# ============================================================================
# HOW MATCHING WORKS
# ============================================================================
#
#   Domain matching is subdomain-aware:
#     "aramco.com" in the list also matches "mail.aramco.com", "corp.aramco.com"
#   Matching is always case-insensitive.
#   EXCLUDED_DOMAINS take priority over ALLOWED_DOMAINS — a domain on both
#   lists is always blocked.
#
# ============================================================================


# ---------------------------------------------------------------------------
# EXCLUDED DOMAINS — always blocked, even if accidentally added to ALLOWED_DOMAINS
#
# PUT YOUR COMPANY'S OWN EMAIL DOMAIN HERE before going live.
# This prevents the system from processing your own internal emails.
# ---------------------------------------------------------------------------
EXCLUDED_DOMAINS = [
    # --- Your company's internal domains ---
    # TODO: Replace "getglobal.com" with your actual Outlook domain.
    #       Check: open Outlook → your email address → the part after the @
    "getglobal.com",

    # --- Personal / free email providers ---
    # These should never appear as sources of business requirements.
    # Keep them here as a safety net even though they won't be on the allowed list.
    "gmail.com",
    "yahoo.com",
    "hotmail.com",
    "outlook.com",
    "live.com",
    "icloud.com",
]


# ---------------------------------------------------------------------------
# ALLOWED DOMAINS — only emails from these domains are processed by the CRM
#
# Organised by type: NOCs | Major IOCs | OFS Companies | EPC/EPCI
# Add a new client here when you start receiving requirements from them.
# ---------------------------------------------------------------------------
ALLOWED_DOMAINS = [

    # ---- National Oil Companies (NOCs) — Arabian Peninsula ----
    "aramco.com",               # Saudi Aramco
    "saudiaramco.com",          # Saudi Aramco alternate domain
    "adnoc.ae",                 # ADNOC (Abu Dhabi National Oil Company)
    "adnocdrilling.ae",         # ADNOC Drilling
    "adnocrefining.ae",         # ADNOC Refining
    "adnoclogistics.ae",        # ADNOC Logistics & Services
    "gasco.ae",                 # GASCO (Abu Dhabi Gas Industries)
    "adgas.ae",                 # ADGAS (Abu Dhabi Gas Liquefaction)
    "zadco.ae",                 # ZADCO (now ADNOC Offshore)
    "taqa.com",                 # TAQA (Abu Dhabi National Energy)
    "enoc.com",                 # ENOC (Emirates National Oil Company)
    "qatarenergy.com",          # QatarEnergy
    "qp.com.qa",                # QatarEnergy legacy domain
    "kockw.com",                # Kuwait Oil Company
    "kpc.com.kw",               # Kuwait Petroleum Corporation
    "knpc.com.kw",              # Kuwait National Petroleum Company
    "kgoc.com.kw",              # Kuwait Gulf Oil Company
    "pdo.co.om",                # Petroleum Development Oman
    "oq.com",                   # OQ (Oman Oil & OmanOil)
    "omanoil.com",              # Oman Oil Company
    "bapco.net",                # BAPCO (Bahrain Petroleum)
    "bapco.com",                # BAPCO alternate domain
    "danagas.com",              # Dana Gas (UAE/Iraq/Egypt)
    "crescent petroleum.com",   # Crescent Petroleum
    "crescentpetroleum.com",    # Crescent Petroleum

    # ---- National Oil Companies — North Africa & Levant ----
    "sonatrach.dz",             # Sonatrach (Algeria)
    "noc.ly",                   # National Oil Corporation (Libya)
    "egpc.com.eg",              # Egyptian General Petroleum Corporation
    "petrojet.com.eg",          # Petrojet (Egypt)
    "gupco.com.eg",             # GUPCO (Egypt — joint BP/EGPC venture)

    # ---- National Oil Companies — Iraq ----
    "basraoil.com",             # Basra Oil Company
    "boc.gov.iq",               # Basra Oil Company government domain
    "inoc.oil.gov.iq",          # Iraq National Oil Company
    "soc.gov.iq",               # South Oil Company (Iraq)
    "noc.gov.iq",               # North Oil Company (Iraq)

    # ---- Major International Oil Companies (IOCs) ----
    "bp.com",                   # BP
    "shell.com",                # Shell
    "totalenergies.com",        # TotalEnergies
    "total.com",                # TotalEnergies legacy domain
    "exxonmobil.com",           # ExxonMobil
    "esso.com",                 # ExxonMobil (Esso brand)
    "chevron.com",              # Chevron
    "equinor.com",              # Equinor (Norway, MENA operations)
    "petronas.com",             # Petronas (Malaysia, MENA contracts)
    "inpex.co.jp",              # INPEX (Japan, ADNOC joint venture)
    "dno.no",                   # DNO (Norway, Iraq/Kurdistan operations)
    "gulfkeystone.com",         # Gulf Keystone Petroleum (Kurdistan)
    "genel.com",                # Genel Energy (Kurdistan/Turkey)

    # ---- Major OFS (Oil Field Services) Companies ----
    "halliburton.com",          # Halliburton
    "slb.com",                  # SLB (Schlumberger)
    "schlumberger.com",         # SLB legacy domain
    "bakerhughes.com",          # Baker Hughes
    "bhge.com",                 # Baker Hughes legacy (GE merger era)
    "weatherford.com",          # Weatherford
    "nov.com",                  # NOV (National Oilwell Varco)
    "technipfmc.com",           # TechnipFMC
    "saipem.com",               # Saipem (Italy)
    "mcdermott.com",            # McDermott
    "woodplc.com",              # Wood (formerly Wood Group)
    "woodgroup.com",            # Wood legacy domain
    "petrofac.com",             # Petrofac
    "expro.com",                # Expro International
    "huntingplc.com",           # Hunting PLC
    "akersolutions.com",        # Aker Solutions (Norway)
    "odfjellwellservices.com",  # Odfjell Well Services
    "welltec.com",              # Welltec (Denmark)
    "archerwell.com",           # Archer (well services)
    "tendeka.com",              # Tendeka (completions)
    "coretrax.com",             # Coretrax (drilling tools)
    "nesfircroft.com",          # NES Fircroft (staffing/manpower)
    "proserv.com",              # Proserv (control systems)
    "altusintervention.com",    # Altus Intervention
    "penspen.com",              # Penspen (pipelines)
    "rpsgroup.com",             # RPS Group (consultancy)

    # ---- Inspection & Testing ----
    "sgs.com",                  # SGS (inspection, testing)
    "bureauveritas.com",        # Bureau Veritas
    "intertek.com",             # Intertek

    # ---- EPC / EPCI Companies ----
    "bechtel.com",              # Bechtel
    "fluor.com",                # Fluor
    "kbr.com",                  # KBR
    "worley.com",               # Worley
    "worleyparsons.com",        # WorleyParsons legacy domain
    "technipenergies.com",      # Technip Energies (spun off from TechnipFMC)
    "aecom.com",                # AECOM
    "jacobs.com",               # Jacobs Engineering
    "mottmac.com",              # Mott MacDonald
    "snclavalin.com",           # SNC-Lavalin (now AtkinsRealis)
    "atkinsrealis.com",         # AtkinsRealis
    "atkinsglobal.com",         # Atkins legacy domain
    "samsung-engineering.com",  # Samsung Engineering (Korea, MENA EPC)
    "hdec.co.kr",               # Hyundai Engineering (Korea, MENA EPC)
    "gsenc.com",                # GS Engineering & Construction

    # ---- Regional Contractors & Agencies ----
    # Add country-specific contractors and recruitment agencies here as needed

    # ---- PILOT: forwarding account ----
    # In the pilot, emails are forwarded from a work account to personal Outlook.
    # Phase 12 (edge_case_handler) extracts the original client sender from the Fw: header.
    # Remove this entry in production when the pipeline reads directly from client mailboxes.
    "getglobalgroup.com",
]


# ---------------------------------------------------------------------------
# FILTERING FUNCTIONS
# ---------------------------------------------------------------------------

def _extract_domain(email_address: str) -> str:
    """
    Extract the lowercase domain from an email address.
    Examples:
        "Ahmed@Aramco.COM"  → "aramco.com"
        "user@mail.adnoc.ae" → "mail.adnoc.ae"
        "not-an-email"      → ""
    """
    if "@" not in email_address:
        return ""
    return email_address.split("@")[-1].strip().lower()


def _domain_matches(domain: str, allowed_domain: str) -> bool:
    """
    Return True if `domain` is or is a subdomain of `allowed_domain`.
    Examples:
        _domain_matches("aramco.com", "aramco.com")         → True  (exact)
        _domain_matches("mail.aramco.com", "aramco.com")    → True  (subdomain)
        _domain_matches("nonaramco.com", "aramco.com")      → False
        _domain_matches("fakaramco.com", "aramco.com")      → False (no partial match)
    """
    return domain == allowed_domain or domain.endswith("." + allowed_domain)


def is_allowed_sender(sender_email: str) -> bool:
    """
    Return True if this sender's email address should be processed by the CRM.

    Decision order:
        1. If domain is in EXCLUDED_DOMAINS → False (always block, e.g. internal emails)
        2. If domain matches any entry in ALLOWED_DOMAINS → True
        3. Otherwise → False
    """
    domain = _extract_domain(sender_email)
    if not domain:
        return False

    # Step 1: Hard block — excluded domains always lose, even if on the allowed list
    for excluded in EXCLUDED_DOMAINS:
        if _domain_matches(domain, excluded.lower()):
            return False

    # Step 2: Whitelist check — domain must match at least one allowed entry
    for allowed in ALLOWED_DOMAINS:
        if _domain_matches(domain, allowed.lower()):
            return True

    # Step 3: No match found — drop silently
    return False


def filter_emails(email_list: list) -> list:
    """
    Return only the emails whose sender domain is on the whitelist.

    Filtered-out emails are silently dropped — no print, no log.
    This is intentional: internal emails, newsletters, and off-topic
    messages should not appear anywhere in the CRM output.

    Parameters:
        email_list — list of email dicts from email_reader.fetch_emails()

    Returns:
        A filtered list containing only emails from approved sender domains.
    """
    return [
        email for email in email_list
        if is_allowed_sender(email.get("sender_email", ""))
    ]


# ---------------------------------------------------------------------------
# QUICK TEST — run this file directly to verify your whitelist
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=== email_filters.py — Domain Whitelist Test ===\n")
    print(f"  Excluded domains : {len(EXCLUDED_DOMAINS)}")
    print(f"  Allowed domains  : {len(ALLOWED_DOMAINS)}")
    print()

    test_cases = [
        # (email_address, expected_result, label)
        ("ahmed@aramco.com",              True,  "Saudi Aramco (exact)"),
        ("procurement@mail.aramco.com",   True,  "Saudi Aramco (subdomain)"),
        ("khalid@adnoc.ae",               True,  "ADNOC"),
        ("user@adnocdrilling.ae",         True,  "ADNOC Drilling"),
        ("john@halliburton.com",          True,  "Halliburton OFS"),
        ("rep@bakerhughes.com",           True,  "Baker Hughes OFS"),
        ("pm@slb.com",                    True,  "SLB"),
        ("bd@petrofac.com",               True,  "Petrofac"),
        ("internal@getglobal.com",        False, "Internal domain (excluded)"),
        ("saral@getglobal.com",           False, "Internal domain (excluded)"),
        ("random@gmail.com",              False, "Gmail (excluded)"),
        ("unknown@unknowncorp.xyz",       False, "Unknown domain (not on list)"),
        ("noemail",                       False, "No @ symbol"),
        ("user@sub.fakaramco.com",        False, "Fake subdomain (not a match)"),
    ]

    all_passed = True
    for email, expected, label in test_cases:
        result = is_allowed_sender(email)
        status = "PASS" if result == expected else "FAIL"
        if status == "FAIL":
            all_passed = False
        symbol = "allow" if result else "block"
        print(f"  [{status}] {symbol:<5}  {email:<40} ({label})")

    print()
    if all_passed:
        print("  All tests passed.")
    else:
        print("  WARNING: Some tests failed — review ALLOWED_DOMAINS or EXCLUDED_DOMAINS.")
