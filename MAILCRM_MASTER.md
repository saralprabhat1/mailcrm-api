# MailCRM — MASTER PROJECT FILE
> Single source of truth. Combines all chats, all code, all decisions.
> Last compiled: June 2026 | Version: FINAL

---

## SECTION 1 — WHO I AM

**Saral Prabhat** — Business Development & Pre-Sales, GET Global Group
- Upstream oil & gas consultancy, MENA markets
- 10+ years BD/commercial background — Halliburton, MI Swaco, GET Global
- Credentials: APMP Foundation, FMVA
- Based in Gurugram, India
- Personal laptop: Lenovo IdeaPad, Windows 11, Intel Core i3, VS Code
- Python level: Beginner — learning hands-on through this project only
- Working style: Direct feedback, practical sequencing, no theory for its own sake

---

## SECTION 2 — THE PROBLEM BEING SOLVED

**Today — Fragmented & Manual:**
- Each AM tracks requirements in personal spreadsheets/email folders
- BD VP manually consolidates data from all AMs → sends to CEO
- CEO gets a partial, always-outdated picture
- Hours wasted on consolidation. Decisions made on stale data.
- No shared visibility across the BD team at any point

**With AI CRM — Centralised & Automated:**
- All 20 Outlook mailboxes read automatically via Graph API
- Azure OpenAI extracts 39 fields per email, creates CRM records instantly
- BD VP and CEO see live pipeline with zero manual consolidation
- One source of truth. Always current.

---

## SECTION 3 — PROJECT JOURNEY (CHRONOLOGICAL FROM ALL CHATS)

### How It Started (Chat: AI-assisted CRM automation for oil & gas)
- First conversation — May 2026
- Goal stated: Build AI-assisted CRM that reads emails, extracts data, updates CRM
- Original 5-phase roadmap created (20 weeks)
- Tech stack identified: Python, Groq, MS Graph API, Streamlit
- Original plan included Kylas CRM API — **later dropped**, replaced with Excel then SharePoint

### Python Learning Phase (Chat: Undefined variable in Python function call)
- Learning environment: `C:\Python_Learning`, VS Code, Python 3.14
- Files worked on: `helper_functions.py`, `client_list.py`
- Real errors debugged: NameError, missing import csv, UTF-8 encoding error, CSV formatting
- Concepts learned: return, functions, parameters, variable scope, dictionaries, modules

### Python Libraries & LLM Integration (Chat: Python libraries explained simply)
- Learned: built-in vs third-party libraries, openpyxl, groq
- Groq API connected and working with Llama model
- SaaS disruption discussion — concluded AI automation is aligned with where value is shifting

### Claude Code Setup (Chat: Using Claude code)
- Claude Code installed and configured
- CLAUDE.md created at project root
- Folder structure built:
  ```
  crm-automation/
  ├── 01_python_basics/
  ├── 02_llm_integration/
  ├── 03_outlook/
  ├── 04_email_parser/
  ├── 05_classifier/
  ├── 06_data_storage/
  ├── 07_dashboard/
  ├── 08_advanced/
  ├── utils/
  ├── tests/
  ├── sample_emails/
  ├── data/
  ├── CLAUDE.md
  └── .env
  ```
- Phases 1–6 built in one session — full pipeline working end-to-end

### Phase 7 — Streamlit Dashboard (Chat: Email-to-CRM automation learning)
- Dashboard built with: KPIs, category pie chart, pipeline stages bar, timeline area chart
- RFQ view with deadline urgency colour-coding (red/yellow/green)
- Next actions table, recent emails table, full record viewer
- Sidebar filters: category, status, client
- Reads directly from `data/crm_data.xlsx`

### CRM Concepts & Business Strategy (same chat)
- Learned: 4 CRM objects (Accounts, Contacts, Deals, Activities)
- Pipeline stages for oilfield services context
- First LinkedIn post published — thought leadership, not revealing the product yet
- Business goal: launch CRM automation service, deploy internally to pilot team first

### Production Architecture Design (Chat: Deep Learning courses for CRM project)
- Full two-track architecture designed
- Production stack: 20 mailboxes → Graph API → Azure OpenAI → SharePoint → Power Apps → Power Automate → Power BI → Teams
- SharePoint data model designed: 2 lists, 55 fields, 7 sections
- 19 requirement stages defined
- 34 PSL categories defined
- 5 Power Automate flows designed
- Power Apps 3-screen UI designed
- Power BI 6-report pages designed
- Context prompt file `GET_CRM_Context_Prompt.md` created

### This Conversation (Current)
- All code files reviewed: auth.py, email_reader.py, parser.py, extractor.py, storage.py, run_parser.py, dashboard.py
- Confirmed: Phase 7 (Streamlit) is DONE — not pending
- Folder `05_classifier/` and `08_advanced/` exist — classifier may be partially started
- `sample_emails/` folder exists — labeling may have started
- Graphify tool is running — scans codebase to build knowledge graph for Claude Code
- Two new PPT slides added: Infrastructure & Hardware Requirements + Licensing & Cost Estimate
- New PPT slide added: Before/After flow diagram (fragmented vs centralised)
- Privacy, security, edge cases, error handling, scalability all documented
- Master context file compiled

---

## SECTION 4 — TWO-TRACK ARCHITECTURE

### Track 1: PILOT (Active — Personal Laptop)
```
Location: C:\Python_Learning\crm-automation
Stack: Python 3.11+, Groq API (llama-3.3-70b-versatile), MSAL (device code flow),
       pandas, openpyxl, python-dotenv, Streamlit, Plotly
Pipeline:
  Outlook (Graph API) → email_reader.py → parser.py → extractor.py (Groq AI)
  → classifier → crm_data.xlsx → dashboard.py (Streamlit)
Auth: saral.prabhat@outlook.com, personal account, consumers authority
Token cache: data/.token_cache.bin
```

### Track 2: PRODUCTION (Designed — Not Yet Built)
```
20x Outlook mailboxes → Microsoft Graph API (Mail.Read)
→ Azure OpenAI (GPT-4o) — AI extraction
→ SharePoint Lists — storage (2 lists: Contracts + Requirements)
→ Power Apps — CRM UI (3 screens)
→ Power Automate — 5 automation flows
→ Power BI — 6 report pages
→ Teams — notifications + CRM tab
→ Azure Key Vault — credentials
→ Microsoft Purview — audit + retention
→ Azure AD / Entra ID — auth + RBAC
```

### Pilot → Production Mapping
| Pilot | Production |
|---|---|
| MSAL device code flow | Azure AD app registration — client credentials flow |
| Groq / Llama | Azure OpenAI GPT-4o |
| crm_data.xlsx | SharePoint Lists |
| run_parser.py | Power Automate Flow 1 |
| Streamlit dashboard | Power Apps |
| .env file | Azure Key Vault |
| No audit trail | Microsoft Purview |
| 1 mailbox | 20 mailboxes |

---

## SECTION 5 — CODE FILES (CURRENT STATE)

### `utils/auth.py`
MSAL authentication with persistent token cache. Uses consumers authority for personal Outlook. Device code flow on first run, silent refresh after. Token saved to `data/.token_cache.bin`.

### `03_outlook/email_reader.py`
Fetches emails from Graph API. Extracts: email_id, received_date, subject, sender_name, sender_email, body_preview, body_content, body_type, is_read, has_attachments, importance. Returns list of dicts.

### `04_email_parser/parser.py`
Strips HTML from email body. Handles style/script blocks, br/p/div tags, HTML entities. Truncates to 3000 chars before AI. Returns clean text formatted as: SUBJECT / FROM / DATE / body.

### `04_email_parser/extractor.py`
Sends cleaned email to Groq API. Currently extracts **14 fields**:
category, client, project, positions, headcount, location, mobilization_date, duration, rates, contact_person, contact_email, deadline, summary, suggested_action.
Uses `response_format: json_object` to enforce JSON. Model: llama-3.3-70b-versatile, temp 0.1.

### `04_email_parser/run_parser.py`
Master pipeline runner. Chains: auth → fetch → parse → extract → preview → save.

### `06_data_storage/storage.py`
Saves to Excel. Deduplication by email_id. Formatted header (dark blue, white text). Frozen row 1. Status column colour-coded. Wrap text on summary/action columns.

### `07_dashboard/dashboard.py`
Full Streamlit dashboard. KPIs (total, RFQs, new, overdue, due soon). Category pie, status bar, timeline area charts. RFQ table with urgency badges. Next actions table. Recent emails. Full record viewer expander. Sidebar filters. 30-second cache refresh.

---

## SECTION 6 — FULL EMAIL PIPELINE

```
1.  Graph API Auth (MSAL device code [pilot] / client credentials [production])
2.  Fetch emails (batch, filters — date range, folder, unread)
3.  Parse email content (subject, sender, body, metadata, thread detection)
4.  Apply privacy rules (redact sensitive fields BEFORE anything else)
5.  Rule-based filter (keyword, sender domain, subject tags → relevant/irrelevant/uncertain)
6.  ML classifier (scikit-learn — relevant/irrelevant/sensitive/financial/confidential)
7.  LLM-assisted classification (Groq — edge cases, confidence < threshold)
8.  LLM extraction (39 fields from relevant emails)
9.  Multi-role detection (one email → multiple records if multiple roles present)
10. Record deduplication (check existing records before creating new)
11. Validate extracted data (missing fields flag, confidence score)
12. Export to Excel / SharePoint
13. Log processing result (audit trail)
14. Refine continuously (retrain classifier, update rules)
```

---

## SECTION 7 — CLASSIFICATION SYSTEM (THREE TIERS)

### Tier 1: Rule-Based (first gate)
- Keywords: "requirement", "manpower", "mobilization", "CV", "profile", "callout", "position", "vacancy", "interview", "offer"
- Sender domains: known OFS clients (Baker Hughes, Halliburton, SLB, etc.)
- Subject tags, project codes, contract numbers
- Output: RELEVANT / IRRELEVANT / UNCERTAIN
- Config stored in file — changeable without touching core code

### Tier 2: ML Classifier (scikit-learn)
- Algorithm: Naive Bayes or Logistic Regression
- Training data: manually labeled sample emails
- Labels: relevant / irrelevant / sensitive / financial / confidential
- Features: TF-IDF on subject + body, sender domain, email length, attachment flag
- Output: label + confidence score
- Retrain periodically as new labeled samples accumulate

### Tier 3: LLM-Assisted (edge cases only)
- Trigger: ML confidence < 0.75 or conflicting Tier 1/2 signals
- Model: Groq/Llama (pilot), Azure OpenAI (production)
- Output feeds back into training data

---

## SECTION 8 — DATA MODEL

### List 1: Contracts (Manual)
Master agreements per client — filled manually by AM.

### List 2: Requirements — 55 Fields, 7 Sections

| Section | Key Fields | Filled By |
|---|---|---|
| Identity & System | Req ID, email date, source mailbox, AM, Service Order ID | System + AM |
| Client Information | Client name, country, sector, contact, PSL (multi-select) | LLM |
| Role & Requirements | Designation, positions, location, mobilization date, technical reqs, certifications | LLM |
| Stage & Status | Requirement stage (19 stages), status | LLM → manual |
| Fulfillment Tracking | CVs requested/shared, shortlisted, interview date/outcome, selected, mobilized | LLM (follow-ups) |
| Communication | Email summary, next action, AM notes | LLM + manual |
| Compliance & Audit | Processing log, LLM confidence, missing fields flag, review status | System |

**~39 fields by LLM. ~16 by system/manual.**

### 19 Requirement Stages
1. Requirement Received → 2. Under Internal Review → 3. Service Order Created → 4. CVs Being Sourced → 5. CVs Requested by Client → 6. CVs Shared with Client → 7. Client Reviewing Profiles → 8. Profiles Shortlisted by Client → 9. Interview Scheduled → 10. Interview Completed → 11. Candidate Selected by Client → 12. Offer Negotiation → 13. Mobilization in Progress → 14. Candidate Mobilized → 15. Position Filled → 16. Requirement Cancelled → 17. Requirement On Hold → 18. No Suitable Candidate → 19. Filled by Competitor

### 34 PSL Categories (Multi-select, LLM-detected)
Artificial Lift, Cementing, Coiled Tubing, Completion, Drilling, Drilling Fluids, EPF, Fishing, FPSO, Fracturing, Geology, HSE, HWO, Maintenance, MLWD, Mud Engineering, Mud Logging, Pipeline & Process, PSCM, Pumping, Reservoir, Rig, Rigless, Slickline, Sub Sea, TCP, Thru Tubing, Training, TRS, Well Completion, Well Head, Well Services, Well Testing, Wireline

---

## SECTION 9 — PRIVACY & SECURITY

### Privacy Rules (Applied Before Everything)
- Irrelevant emails dropped at Tier 1 — never stored or processed further
- Financial info, account numbers, confidential identifiers — redacted before LLM sees them
- Only CRM-relevant fields captured — data minimization
- No sensitive emails in ML training sets
- Graph API scope: Mail.Read only

### Security Stack (Production)
| Component | Role |
|---|---|
| Azure AD App Registration | App identity — reads 20 mailboxes silently, 24/7 |
| Azure Key Vault | Stores CLIENT_ID, CLIENT_SECRET, OPENAI_API_KEY |
| Azure AD Groups / RBAC | 4 roles: BD Member, AM, BD Manager (read-all), Admin |
| SharePoint + Azure | Encryption in transit (TLS) + at rest |
| Microsoft Purview | Audit logs, retention policies |
| Conditional Access | MFA enforcement |

### Data Retention
- Inactive records: delete after 2 years
- Completed records: archive after 5 years

---

## SECTION 10 — PRODUCTION COMPONENTS

### Power Automate — 5 Flows
| Flow | Trigger | Action |
|---|---|---|
| Flow 1 | New email | Extract via Azure OpenAI → create/update SharePoint record |
| Flow 2 | Missing fields on new record | Teams alert to AM |
| Flow 3 | Daily 8 AM | Deadline reminders |
| Flow 4 | Stage change | Activity log + team notification |
| Flow 5 | ERP milestone (future) | Auto-update stage from ERP |

### Power Apps — 3 Screens
1. Home — KPIs, missing field alerts, deadlines, my deals
2. Pipeline — all deals, filterable by PSL/country/AM/type
3. Deal Detail — 55-field record, AI summary, edit, missing fields banner

**4 User Roles:** BD Member, Account Manager, BD Manager, Admin

### Power BI — 6 Pages (Daily refresh)
1. Pipeline overview — stage funnel, country breakdown
2. Client activity — most active clients, NOC vs OFS
3. PSL breakdown — demand by service line, fill rate
4. Deadlines — colour-coded urgency
5. Team activity — open deals per AM, fill rate per AM
6. Fill rate — outcome breakdown, monthly trend

---

## SECTION 11 — LICENSING & COSTS (20 USERS)

| Component | Model | Est. Monthly |
|---|---|---|
| Graph API Mail.Read | Included in M365 | $0 |
| Azure OpenAI GPT-4o | Pay-per-token | ~$10–$30 |
| Power Apps | $0 if M365 E3/E5 exists; else $5/user per-app plan | $0–$100 |
| Power Automate Premium | $15/user/month | $300 |
| Power BI Pro | $10/user (managers only, ~5–10 users) | $50–$100 |
| Azure Key Vault | $0.03/10K operations | <$1 |
| **Total (incremental)** | | **~$360–$530/month** |

Note: Confirm with IT whether M365 E3/E5 already covers Power Apps.

---

## SECTION 12 — EDGE CASES & ERROR HANDLING

| Edge Case | Approach |
|---|---|
| Attachments | Extract text from PDF/Word; flag others |
| Forwarded emails | Detect forwarding headers; extract original sender |
| Long threads | Process top/latest message only; store thread depth |
| HTML emails | Strip HTML; extract clean plain text |
| Multi-role emails | One email → one record per role |
| Multi-language | Detect language; pass to LLM with language context |

| Error | Handling |
|---|---|
| Graph API failure | Retry with exponential backoff; log; alert |
| Token expiration | Auto-refresh; re-authenticate if refresh fails |
| Parsing failure | Log; flag for manual review; never drop silently |
| Classification uncertainty | Route to Tier 3 LLM; if still uncertain → human review |
| LLM extraction failure | Log confidence; flag missing fields |
| Duplicate record | Check client + role match; update existing if found |

---

## SECTION 13 — WHAT CAN BE BUILT ON PERSONAL LAPTOP

| Can Build Now | Needs Company Infra |
|---|---|
| Graph API (1 mailbox) | 20-mailbox reading |
| Groq extraction (all 39 fields) | Azure OpenAI |
| Rule-based classification | SharePoint Lists |
| scikit-learn ML classifier | Power Apps |
| LLM classification | Power Automate |
| Multi-role detection | Power BI |
| Follow-up email matching | Teams |
| Excel CRM (mirrors SharePoint schema) | Azure Key Vault |
| Streamlit dashboard | Microsoft Purview |
| All error handling logic | Org-level App Registration |

~70% of the system — the entire intelligence layer — built and validated locally.

---

## SECTION 14 — PHASE TRACKER (ACCURATE AS OF TODAY)

| Phase | Folder | Description | Status |
|---|---|---|---|
| 1 | 01_python_basics/ | Python fundamentals | ✅ Done |
| 2 | 02_llm_integration/ | Groq API connected | ✅ Done |
| 3 | 03_outlook/ | Graph API — fetch emails | ✅ Done |
| 4 | 04_email_parser/ | Groq AI extraction (14 fields) | ✅ Done |
| 5 | 05_classifier/ | Rule-based classification | ✅ Done |
| 6 | 06_data_storage/ | Excel save, dedup, format | ✅ Done |
| 7 | 07_dashboard/ | Streamlit dashboard | ✅ Done |
| 8 | 08_advanced/ | Full 55-field LLM extraction | 🔲 NEXT |
| 9 | 05_classifier/ | Multi-role detection | 🔲 Pending |
| 10 | 05_classifier/ | Follow-up email matching | 🔲 Pending |
| 11 | 05_classifier/ | scikit-learn ML classifier | 🔲 Pending |
| 12 | 08_advanced/ | Edge case handling | 🔲 Pending |
| 13 | 08_advanced/ | Full error handling | 🔲 Pending |
| 14 | — | Pilot → Production transition | 🔲 Pending |

---

## SECTION 15 — CODING STANDARDS (FOR CLAUDE CODE)

- Comment every block in plain English — beginner-friendly
- All secrets in .env via python-dotenv — never hardcode
- try/except on all API calls with clear error messages
- snake_case for all variables and functions
- Small, single-purpose functions
- Print progress messages throughout
- pathlib for all file paths (Windows-safe)
- pandas for all Excel/CSV operations
- Explain WHY each step is needed, not just what it does
- Prefer readable code over clever one-liners
- When fixing bugs — explain the root cause
- Add phase number prefix to all new folders (e.g. 08_advanced/)

---

## SECTION 16 — HOW TO RESUME IN ANY NEW CHAT

**Paste this file at the start of any new conversation.**

Current state as of this file:
- Phases 1–7 complete and working
- Phase 8 is next: expand extractor.py to full 55-field extraction
- `05_classifier/` folder exists — check contents before building classifier
- `08_advanced/` folder exists — check contents before building
- `sample_emails/` folder exists — may have labeled samples already

**To resume coding:**
```
Open VS Code
Ctrl+` → terminal
cd C:\Python_Learning\crm-automation
claude
Paste this file as first message
```

**Three things queued up in order:**
1. Full 55-field LLM extraction prompt (Phase 8) — highest priority
2. Multi-role detection — one email → multiple records
3. Follow-up email matching — update existing records from CV/interview emails

---

## SECTION 17 — BUSINESS GOAL

Internal pilot deployment first → prove value → then offer as a service to mid and small-tier oil & gas companies that have the same BD chaos problem. Building credibility on LinkedIn quietly before any public announcement. First LinkedIn post published. No product reveal yet.

## UPDATE: 2026-06-05
- Phase 9 (follow-up email matching) — COMPLETE
  - Match scoring: 85/100 on genuine follow-up, 0/100 on unrelated
  - update_record() tested: 7 fields updated, audit log appending correctly
  - followup_extractor.py created in 05_classifier/
  - 14 follow-up types mapped to status values
  - update_record() added to storage.py — patches fields, appends to audit log
  - Routing logic added to run_parser.py — follow-up vs new record path
- Phase 10 next: scikit-learn ML classifier in 05_classifier/
## CURRENT PHASE: 10

- Note: _parse_json_response() duplicated in extractor.py and 
    followup_extractor.py — move to utils/ (cleanup task)

    ## CHAT DECISIONS: 2026-06-05
- Session management process confirmed:
  - End: Graphify (optional going forward) → update master file → exit
  - Start: launch Claude Code → read master file + memory → pick up
- Graphify decision: skip by default from next session, 
  use memory + master file instead. Only use if Claude Code 
  gets confused about codebase structure.
- Master file update process: one living file, updated at 
  end of each session with dated block. No new file each day.
- Duplicate code flagged: _parse_json_response() in extractor.py 
  and followup_extractor.py — move to utils/ during Phase 10
- Phase 10 next: scikit-learn ML classifier in 05_classifier/

## UPDATE: 2026-06-05 (Session 2)
- Cleanup done: _parse_json_response() moved to utils/json_utils.py
- Renamed to parse_json_response() (public, no underscore)
- extractor.py and followup_extractor.py updated with new import

## UPDATE: 2026-06-05 (Session 3)
- Phase 10 COMPLETE: scikit-learn ML classifier in 05_classifier/
  - email_classifier.py built in 05_classifier/
  - 64 labeled training examples in data/training_emails.csv (5 classes)
  - Classes: relevant, irrelevant, sensitive, financial, confidential
  - Algorithm: Logistic Regression + TF-IDF (unigrams+bigrams) + 3 numeric features
  - Features: combined subject+body TF-IDF | is_known_domain | email_length | has_attachments
  - CV accuracy: 75% on 64 samples (will improve as labeled data grows)
  - Trained model saved to data/email_classifier.joblib
  - run_parser.py updated: classifier runs as Step 0/gate before AI extraction
  - irrelevant emails dropped silently; sensitive/financial/confidential flagged to review queue
  - Low-confidence predictions (< 0.75) pass through to Tier 3 (LLM review, future)
  - Auto-trains on first run if no model file found
  - scikit-learn 1.9.0 installed
- CURRENT PHASE: 11 (Edge case handling — 08_advanced/)

## UPDATE: 2026-06-05 (Session 4)
- Classifier retrained with 96 samples (v2)
- CV accuracy: 64.6% ±12.6% (up from 54.7%)
- Target: 200 samples / 30+ per class for 75%+ accuracy
- Accuracy improves automatically as real emails are labeled over time
- CURRENT PHASE: 11 (multi-role detection)

## UPDATE: 2026-06-05 (Session 4)
- Classifier retrained with 96 samples (v2)
- CV accuracy: 64.6% ±12.6% (up from 54.7%)
- Target: 200 samples / 30+ per class for 75%+ accuracy
- Phase 11 complete: PSL-based record splitting in 05_classifier/psl_splitter.py
  - detect_psls(), split_by_psl(), enrich_record() built
  - One email → one record per detected PSL category
- Phase 12 complete: Edge case handling in 08_advanced/edge_case_handler.py
  - Forwarding chain stripped — AI sees original email not Saral's wrapper
  - Original sender recovered correctly
  - Language detection added
  - Attachment note appended
  - Critical fix: all 33 forwarded emails were previously attributing sender as Saral
- CURRENT PHASE: 13 (full error handling)

## UPDATE: 2026-06-05 (Session 5)
- Phase 13 complete: Full error handling
  - tier3_classifier.py: LLM fallback when ML confidence <0.75
    - Tested: RFQ=99% relevant, newsletter=90% irrelevant, invoice=99% financial
  - duplicate_detector.py: difflib similarity on client+designation+date
    - ≥80% similarity → blocked, logged to failed_emails.log
    - 60-79% → saved, flagged to review_queue.xlsx
  - auth.py: token refresh returns None instead of sys.exit()
  - email_reader.py: catches HTTP 401, auto-retries with refreshed token
  - run_parser.py: Tier 3 routing, duplicate check, new summary counters
- CURRENT PHASE: 14 (Pilot → Production transition)
- Pilot intelligence layer ~100% complete

## UPDATE: 2026-06-05 (Session 5)
- Phase 13 complete: Full error handling (see previous block)
- End-to-end test run complete
  - 14 records in crm_data.xlsx
  - 3 follow-ups updated, 1 new record saved
  - 1 sensitive email correctly flagged (salary data)
  - Bug fixed: None vs missing key in extractor.py + role_taxonomy.py
  - extractor.py _clean() wrapper added on role.get() calls
  - role_taxonomy.py: guard added at top of get_psl_for_role()
- Pilot complete. Phases 1-13 done and tested.
- CURRENT PHASE: 14 (Pilot → Production transition — needs company infra)

## UPDATE: 2026-06-06 — Phase 14a bug fix (storage.py return values)

### Root cause
Three missing `return` statements in `06_data_storage/storage.py` caused
`TypeError: 'NoneType' object is not subscriptable` in run_parser.py, making
all 4 emails fail silently at the save step.

### Fixes applied
1. `save_to_excel()` — added `return {"saved": saved_count, "skipped_duplicates": 0, "total_rows": len(combined_df)}`
   - run_parser.py reads `result['saved']`, `result['skipped_duplicates']`, `result['total_rows']`
2. `update_record()` — added `return {"updated": True}`
   - run_parser.py reads `result["updated"]` in the follow-up branch
3. `save_records()` — now captures `result = save_to_excel(...)` and returns it
   - Previously called save_to_excel() and discarded its return value

### Bonus fix: Supabase column mismatch in update_record()
- `_build_update_dict()` uses internal field names (`email_summary`, `next_action`)
  that differ from Supabase column names (`summary`, `suggested_action`)
- Added `_SUPABASE_COLS`, `_SUPABASE_RENAME`, and `_sanitize_for_supabase()` helper
  to storage.py — remaps names and drops unknown columns before each Supabase update

### Verified results (run 2026-06-06)
- 5 emails fetched from Outlook
- 1 correctly flagged as sensitive (salary negotiation) → review queue
- 4 processed as follow-ups:
  - REQ-20260605-E3A8B8-01 → stage: Client Reviewing Profiles
  - REQ-20260605-EAB862-01 → stage: CVs Being Sourced
  - REQ-20260605-7BCC0F-01 → stage: CVs Being Sourced
  - REQ-20260605-37943C-01 → stage: Mobilization in Progress (mobilization type)
- All 4 Supabase updates confirmed: `Supabase updated: REQ-...`
- crm_data.xlsx updated (14 existing records, follow-up fields patched)
- No errors, no TypeError

### CURRENT PHASE: 14a complete — Supabase dual-write fully working

## UPDATE: 2026-06-06 (Session 2) — Phase 14a fully confirmed

### Root cause of empty Supabase table
- Previous session: `.update().eq()` silently matched 0 rows on an empty table — not an RLS
  violation, just a no-op. Appeared to succeed in logs but inserted nothing.
- After switching to `.upsert()`: INSERT path triggered → RLS blocked it (anon key has no
  INSERT permission). Error: `42501 new row violates row-level security policy`.

### Fix applied
- Added `SUPABASE_SERVICE_KEY` to `.env` (service role JWT — bypasses RLS entirely).
- `storage.py` already had the fallback logic from previous session:
  `SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY")`
- No further code changes needed — the key change alone unblocked writes.

### Key distinction: anon key vs service role key
| Key | Role | INSERT | UPDATE | RLS |
|---|---|---|---|---|
| `SUPABASE_KEY` (anon) | Browser/public | Blocked by RLS | No-op if row missing | Enforced |
| `SUPABASE_SERVICE_KEY` | Server/admin | Yes | Yes (upsert) | Bypassed |

### Verified run (2026-06-06)
- 5 emails fetched, 1 flagged sensitive (salary data → review queue)
- 4 processed as follow-ups — all 4 confirmed `Supabase upserted: REQ-...`:
  - REQ-20260605-E3A8B8-01 → general_update, stage: Client Reviewing Profiles
  - REQ-20260605-EAB862-01 → general_update, stage: CVs Being Sourced
  - REQ-20260605-7BCC0F-01 → cv_submitted, stage: CVs Shared with Client
  - REQ-20260605-37943C-01 → mobilization, stage: Mobilization in Progress
- crm_requirements table in Supabase now has 4 rows — check Table Editor to confirm
- Excel crm_data.xlsx also updated (14 existing rows + follow-up patches)
- No errors

### Storage architecture (final for pilot)
```
Email pipeline → Excel (crm_data.xlsx)   — primary, local backup
             → Supabase crm_requirements — cloud, real-time, dashboard-ready
```
- New records: save_records() → save_to_excel() + save_to_supabase() [upsert]
- Follow-ups:  update_record() → patch Excel row + Supabase upsert (insert if new, update if exists)

### CURRENT PHASE: 15 — next step TBD (production transition or dashboard v2)

## UPDATE: 2026-06-06 (Session 3) — Supabase field mapping fix

### Problem
Supabase `crm_requirements` table had 4 rows but all columns except `email_id` were NULL.
`save_to_supabase()` in `storage.py` was using stale Phase-4 field names that no longer
match the Phase-8 extractor output from `build_multi_role_rows()`.

### Root cause: field name mismatches
| Supabase column | Was reading | Now reads |
|---|---|---|
| `client` | `record.get("client")` | `record.get("client_name")` |
| `project` | `record.get("project")` | `record.get("project_name")` |
| `positions` | `record.get("positions")` | `record.get("designation")` |
| `summary` | `record.get("summary")` | `record.get("email_summary")` |
| `suggested_action` | `record.get("suggested_action")` | `record.get("next_action")` |
| `classification` | `record.get("classification")` | `record.get("category")` |
| `confidence_score` | `record.get("confidence_score")` | `record.get("llm_confidence")` |

Also fixed: `float()` cast on `confidence_score` now guards against empty string / None
with `try/except` block.

### Second bug found: save_to_supabase() was dead code for new records
`run_parser.py` was calling `save_to_excel(crm_rows)` directly — never calling
`save_to_supabase()` for new requirements. Fixed by:
- Adding `save_records` to the import in `run_parser.py`
- Changing `result = save_to_excel(crm_rows)` → `result = save_records(crm_rows)`
- `save_records()` calls both `save_to_excel()` AND `save_to_supabase()` per record

### Cleanup
- Deleted 4 NULL rows (keyed by REQ IDs, from previous follow-up upserts)
- Seeded Supabase with all 14 existing Excel records using corrected mapping
- Confirmed 14 rows in `crm_requirements` with real data:
  - `received_date` populated on all 14
  - `confidence_score` = 0.7 on Phase-8 records
  - `positions` = "Fishing Supervisor", "AMO Technician" where extracted
  - `client` = "Baker Hughes" where extracted
  - Earlier 10 rows have empty client/positions — expected (extracted pre-Phase 8
    with 14-field prompt, `client_name` / `designation` not available)

### Architecture note
```
New requirements:  run_parser.py → save_records() → save_to_excel() + save_to_supabase()
Follow-up emails:  run_parser.py → update_record() → Excel patch + Supabase upsert
                   (uses _sanitize_for_supabase() — maps email_summary→summary, etc.)
```

### CURRENT PHASE: 15 — Supabase dual-write fully working end-to-end

## UPDATE: 2026-06-06 (Session 4) — Rebrand to MailCRM

### What changed
The product is now called **MailCRM**. All GET Global-specific references removed from
source code so the codebase is product-generic and can be deployed for any client.

### File changes
| File | Change |
|---|---|
| `GET_CRM_MASTER_FINAL.md` | Renamed → `MAILCRM_MASTER.md` |
| `MAILCRM_MASTER.md` | H1 heading updated to "MailCRM — MASTER PROJECT FILE" |
| `04_email_parser/extractor.py` | System prompt: removed "GET Global Group" → "an oil & gas manpower consultancy"; test email salutation "Dear GET Global" → "Dear Team" |
| `05_classifier/followup_extractor.py` | System prompt: removed "GET Global Group"; field guidance: "CVs did GET Global send" → "CVs were sent"; test email signature: "GET Global Group" → "MailCRM" |
| `05_classifier/tier3_classifier.py` | Test invoice subject: "GET Global" → "Manpower Services" |
| `05_classifier/email_classifier.py` | Test email bodies: "Dear GET Global" → "Dear Team"; "acquisition of GET Global Group" → "acquisition of the company" |
| `05_classifier/psl_splitter.py` | Comment: "used by GET Global" → removed |
| `config/email_filters.py` | Comments: "GET Global's own domain" → "your company domain"; "GET Global internal domains" → "Your company's internal domains"; pilot forwarding comment generalised; test case labels updated |
| `CLAUDE.md.bak` | About section and developer background generalised |
| Memory file `project_state.md` | `GET_CRM_MASTER_FINAL.md` → `MAILCRM_MASTER.md` reference updated |

### What was NOT changed (intentional)
- Supabase project name `get-crm` — internal ID, cannot be changed via API
- `data/` files (training CSVs, logs) — raw data, not product branding
- `graphify-out/` — generated output, will regenerate if graphify is re-run
- `getglobalgroup.com` domain in `email_filters.py` ALLOWED_DOMAINS — real functional config, not branding
- Developer identity in Section 1 of this master file — personal record, not product code

### Verified
- `python 04_email_parser/run_parser.py` — clean run, no errors
- 4 follow-ups processed, 4 Supabase upserts confirmed
- Pipeline behaviour unchanged

### CURRENT PHASE: 15 — codebase is now product-generic (MailCRM)

## UPDATE: 2026-06-06 (Session 5) — Full GET Global reference sweep

### Scope
Complete grep of all `.py` and `.md` files for: "GET Global", "getglobalgroup", "GET CRM", "get-crm".

### Findings
All `.py` files were already clean (done in Session 4). Two residual business-goal references
remained in `MAILCRM_MASTER.md` — fixed in this session.

### File changed
| File | Change |
|---|---|
| `MAILCRM_MASTER.md` | Line 91 (Section 3): "starting internally at GET Global first" → "deploy internally to pilot team first" |
| `MAILCRM_MASTER.md` | Section 17: "Internal launch at GET Global first → prove value" → "Internal pilot deployment first → prove value" |

### Intentionally NOT changed
| Item | Reason |
|---|---|
| Section 1 of this file (personal bio) | Biographical data about the developer — not product code |
| Session 4 change log entries (lines 659–674) | Historical record of what was changed — accurate documentation |
| `get-crm` Supabase project name | Internal ID — cannot be changed via API |
| `getglobalgroup.com` in `config/email_filters.py` ALLOWED_DOMAINS | Functional config — real sender domain whitelist |
| `sample_emails/raw_emails.csv` | Raw fetched email data (actual emails) — not test data or hardcoded references |

### Verified
- `python 04_email_parser/run_parser.py` — clean run, no errors
- 5 emails fetched, 4 follow-ups processed, 1 sensitive flagged to review queue
- All 4 Supabase upserts confirmed

### CURRENT PHASE: 15 — codebase fully product-generic

## UPDATE: 2026-06-06 (Session 6) — Phase 14c: GitHub + Render prep

### What was done
- **Git installed**: Git 2.54.0 installed via `winget` (was missing from system)
- **requirements.txt created** (project root) — all API dependencies
- **render.yaml created** (project root) — Render web service config
- **.gitignore expanded** — added exclusions for logs, raw email CSV, local Claude settings, training data with real email content
- **Git repo initialized** — `C:\Python_Learning\crm-automation`
- **Commit made**: `bb2d5bc` — "Phase 14c: MailCRM API ready for Render deploy" — 31 files

### Files committed (31)
All source code + config. Explicitly excluded from commit:
- `.env` — secrets
- `data/` — all Excel, CSV, binary, log files
- `sample_emails/raw_emails.csv` — real email data
- `05_classifier/training_data_v2.csv` — training data with real content
- `api/uvicorn.log`, `api/uvicorn_err.log` — runtime logs
- `.claude/settings.local.json` — local Claude config
- `graphify-out/` — generated output

### requirements.txt contents
```
fastapi
uvicorn[standard]
supabase
python-dotenv
pandas
openpyxl
requests
scikit-learn
joblib
msal
scipy
numpy
```

### render.yaml config
```yaml
services:
  - type: web
    name: mailcrm-api
    runtime: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn api.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: SUPABASE_URL
        value: https://xvosrjwtcsspoqqaiawm.supabase.co
      - key: SUPABASE_SERVICE_KEY
        sync: false
      - key: GROQ_API_KEY
        sync: false
```

### GitHub push — manual step required
`gh` CLI not available for automated auth. To push to GitHub:

1. Go to https://github.com/new → create repo named **mailcrm-api** (private, no README)
2. Run these 3 commands in terminal from `C:\Python_Learning\crm-automation`:
```
"C:\Program Files\Git\bin\git.exe" remote add origin https://github.com/<YOUR_USERNAME>/mailcrm-api.git
"C:\Program Files\Git\bin\git.exe" branch -M main
"C:\Program Files\Git\bin\git.exe" push -u origin main
```
3. Once pushed → connect Render to GitHub repo (manual step in Render dashboard)

### Environment variables to set in Render dashboard
| Key | Value |
|---|---|
| SUPABASE_URL | https://xvosrjwtcsspoqqaiawm.supabase.co |
| SUPABASE_SERVICE_KEY | (paste from .env) |
| GROQ_API_KEY | (paste from .env) |

### GitHub push — COMPLETE
- Pushed via Windows Credential Manager (stored credentials used automatically)
- Repo: https://github.com/saralprabhat1/mailcrm-api
- Branch: `main` tracking `origin/main`
- Commit: `5587849` — 31 files, 8,184 insertions

### CURRENT PHASE: 14c — code on GitHub, Render connection next

## END-OF-DAY SUMMARY: 2026-06-06 — Full day recap

### Phase 14a — Supabase live
- Org: MailCRM | Project: `get-crm` | Region: Mumbai (ap-south-1)
- Table: `crm_requirements` — 25 columns, RLS enabled
- Auth: service role key (bypasses RLS for server-side writes)
- Both write paths confirmed working:
  - New records: `save_records()` → `save_to_supabase()` upsert
  - Follow-up updates: `update_record()` → Supabase upsert (insert if new, patch if exists)
- Field mapping fixed: `client_name`, `designation`, `email_summary`, `next_action`, `category`, `llm_confidence` all correctly written

### Phase 14b — FastAPI backend
- File: `api/main.py`
- 5 endpoints:
  | Endpoint | Method | Description |
  |---|---|---|
  | `/` | GET | Health check |
  | `/records` | GET | All CRM records, newest first |
  | `/records/{email_id}` | GET | Single record by REQ ID |
  | `/stats` | GET | Totals, status breakdown, top PSLs, last-7-days count |
  | `/run-pipeline` | POST | Trigger email pipeline (max 5 emails) |
- CORS enabled (allow_origins=["*"])
- Supabase client initialised at startup using `SUPABASE_SERVICE_KEY`

### Phase 14c — Render deployment
- Live API: https://mailcrm-api.onrender.com
- GitHub repo: https://github.com/saralprabhat1/mailcrm-api
- Runtime: Python 3, Render free tier
- Config: `render.yaml` at project root (auto-detected by Render)
- Env vars set in Render dashboard: `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`, `GROQ_API_KEY`
- Git installed (v2.54.0 via winget) — was missing from system
- 31 source files committed; secrets, data files, raw emails excluded

### Rebrand — complete
- Product name: **MailCRM** (was internally GET Global CRM)
- All `GET Global` references removed from all `.py` files and prompts
- System prompts now generic: "an oil & gas manpower consultancy"
- Master file renamed: `GET_CRM_MASTER_FINAL.md` → `MAILCRM_MASTER.md`

### Known issue — fix next session
**Problem:** Supabase `crm_requirements` table showing NULL fields on recent records.
**Root cause:** `is_followup_email()` in `05_classifier/followup_matcher.py` is incorrectly classifying new requirement emails as follow-ups. They get routed to `update_record()` (which patches existing rows) instead of `save_records()` (which creates new rows with all fields).
**Fix:** Tighten the follow-up detection logic in `followup_matcher.py` — likely the subject-line matching or match-score threshold is too loose, causing false positives.
**File to fix:** `05_classifier/followup_matcher.py` → `is_followup_email()` and/or match score threshold

### Next: Phase 14d — React dashboard frontend
- Goal: replace Streamlit dashboard with a React web app reading from the Render API
- Stack: React + TailwindCSS, reading from `https://mailcrm-api.onrender.com`
- Endpoints it will consume: `/records`, `/stats`, `/records/{id}`
- To discuss: hosting (Vercel/Netlify), authentication for dashboard access

---

## UPDATE: 2026-06-06 (Session 7) — Bug fix + Phase 14d React dashboard

### Decisions & agreements

- **End-of-session rule established:** last Claude Code prompt every session must update MAILCRM_MASTER.md and then exit
- Master file must capture everything — not just code changes, but all decisions, directions, agreements, blockers, and business discussions — so any future session can start from full context just by reading the file
- When Saral types `exit` in Claude.ai chat, Claude will always generate the final Claude Code prompt automatically

### Bug fix — followup_matcher.py (Phase 14b)

- **Root cause 1:** `Fw:` prefix was being treated as a follow-up signal — but Saral forwards all emails, so every email was matching. Fixed: removed `Fw:`/`Fwd:` from prefix check; only `Re:` is now a follow-up signal
- **Root cause 2:** `is_followup_email()` was receiving the raw Outlook blob (with forwarding headers) instead of the cleaned body from `preprocess_email()` — fixed in `run_parser.py`
- Body keyword threshold raised from 3 → 5; match score threshold raised from 40 → 60
- NULL rows 31–34 and 45 deleted from Supabase; Row 46 confirmed fully populated — fix verified

### Phase 14d — React dashboard

- `frontend/` folder created at project root using Vite + TailwindCSS
- Dark terminal aesthetic: bg `#0d0f12`, accent `#00d4aa`, IBM Plex Mono + DM Sans fonts
- Components built: `StatsBar`, `PipelineBar`, `RecordsTable`, `DetailPanel`, `useApi` hook
- Connects to `https://mailcrm-api.onrender.com` — endpoints: `/records`, `/stats`, `/records/{id}`, `/run-pipeline`
- Clean build confirmed locally (`npm run build` — 2.15s, 0 errors)
- Committed and pushed to GitHub (`saralprabhat1/mailcrm-api`, commits `d3ecf89` + `270ce01`)

### Vercel deploy — attempted, incomplete

- Vercel account created (Hobby plan, Google OAuth, username `saralprabhat1`)
- Internet instability + laptop restart prevented completion
- **Resume next session:** go to vercel.com → Add New → Project → import `saralprabhat1/mailcrm-api` → Edit Root Directory → select `frontend` → Framework: Vite → Deploy

### Next session start point

1. Restart laptop, open VS Code, run `claude` in terminal
2. Read `MAILCRM_MASTER.md`
3. Open vercel.com and complete the deploy
4. Once live URL confirmed — set up UptimeRobot to ping Render API every 5 mins (Phase 14e)
5. Then Phase 14f: add basic auth to the React dashboard (simple password gate before sharing with anyone)

---

## UPDATE: 2026-06-06 (Session 8) — Phase 14d COMPLETE

### Phase 14d — Vercel deploy successful
- Live dashboard URL: https://mailcrm-api.vercel.app
- Vercel account: saralprabhat1 (Hobby plan, Google OAuth)
- Repo: saralprabhat1/mailcrm-api, branch: main, commit: d3ecf89
- Root directory: frontend | Framework: Vite (auto-detected)
- Dashboard confirmed loading with live data from Supabase via Render API
- Total Records = 1 (correct — only 1 clean verified record in Supabase post bug-fix)
- Some fields showing — (NULL issue on older records, not a new problem)

### Network issue resolved
- vercel.com and netlify.com were unreachable (ISP block, Meerut)
- Fixed by changing DNS to Cloudflare (1.1.1.1 / 1.0.0.1) via netsh in admin CMD
- Interface name: "Wi-Fi 2"

### Full stack now live end-to-end
Outlook → Groq → Supabase → Render API → Vercel → Browser

### CURRENT PHASE: 14e — UptimeRobot setup (keep Render API alive)

### Next session start point
1. Read MAILCRM_MASTER.md
2. Go to uptimerobot.com → create free monitor → ping https://mailcrm-api.onrender.com every 5 mins (Phase 14e)
3. Phase 14f: add basic password gate to React dashboard before sharing with anyone
4. Then run pipeline from VS Code to populate more records

### CURRENT PHASE: 14d — React dashboard (next session)

---

## UPDATE: 2026-06-06 (Session 9) — Phases 14e + 14f complete, pipeline run, field mapping fixed

### Phase 14e — UptimeRobot COMPLETE
- Monitor live at uptimerobot.com: pings https://mailcrm-api.onrender.com every 5 minutes
- Prevents Render free tier from spinning down (15-min idle timeout)
- Alert contact: saral.prabhat@gmail.com (notified if API goes down)
- Health check endpoint: GET / → `{"status": "ok", "product": "MailCRM"}`

### Phase 14f — Password gate COMPLETE
- New file: `frontend/src/components/LoginScreen.jsx`
- `App.jsx`: added `authed` state — if false, render LoginScreen; if true, render dashboard
- Password: `MailCRM@2026` (hardcoded, change when onboarding real users)
- Auth state in React memory only — no localStorage, no cookies; refresh = back to login
- UI: full-screen dark terminal aesthetic, IBM Plex Mono, accent #00d4aa
- Subtle grid texture background; input auto-focuses on mount; Enter key submits
- Wrong password: "Incorrect password." error + brief shake animation + field clears
- Unlock button disabled when field is empty
- Deployed to Vercel automatically via GitHub push

### Pipeline run — full inbox
- Ran `run_pipeline(max_emails=50)` on full inbox: 38 emails fetched, 31 passed domain filter
- 7 filtered by ML/Tier3: 2 sensitive, 2 confidential, 2 irrelevant, 1 financial
- 30 new CRM records created; all 30 pushed to Supabase
- Supabase now has 30 rows; Excel crm_data.xlsx has 35 rows total
- Note: Groq Tier3 rate-limited on second run (same-day quota exhausted after processing 31 emails twice)

### Field mapping fix — api/main.py
- **Root cause**: React dashboard reads Phase-8 internal field names (`req_id`, `client_name`,
  `designation`, `email_summary`, `next_action`, `llm_confidence`) but Supabase stores legacy
  column names (`email_id`, `client`, `positions`, `summary`, `suggested_action`, `confidence_score`).
  FastAPI was passing raw Supabase rows with no renaming → all six fields showed NULL in dashboard.
- **Fix**: added `_to_frontend()` transform in `api/main.py` — runs at the API boundary before
  any response is returned. Applied to `/records` and `/records/{id}` endpoints.
- Supabase schema unchanged; React components unchanged; storage.py unchanged.
- A bad intermediate fix (writing to non-existent Supabase columns) was correctly reverted
  after PGRST204 errors confirmed the table uses the old column names.

### extractor.py — Internal company exclusion list
- Added `INTERNAL_COMPANY_NAMES` set in `extractor.py` (module-level constant)
- Added `_filter_client_name()` helper: case-insensitive match + prefix match
- Applied in `build_multi_role_rows()` at the `client_name` assignment
- Initial entries: "aldhahi get consultants company ltd", "aldhahi get consultants", "aldhahi"
- To add new entries: append to `INTERNAL_COMPANY_NAMES` set — no other changes needed
- Existing Supabase record REQ-20260606-58CA99-01 patched: `client` → NULL via direct Supabase update
- No other records matched the exclusion list (checked all 30 rows)

### Attachment issue — documented, deferred to Phase 15
- Many emails show NULL for `client_name`, `designation` (positions), `rates`, `duration`, `deadline`
- Root cause: requirements are in PDF/Word attachments — the email body only says "please find attached"
- AI correctly returns null (information is not in the body text it receives)
- Fix: Phase 15 — extract text from PDF/Word attachments before passing to AI
- NOT a field mapping bug — the mapping is correct; the data simply isn't in the email body

### NULL field summary (30 Supabase rows)
| Column | Nulls | % | Cause |
|---|---|---|---|
| `duration` | 29 | 97% | In attachments |
| `rates` | 29 | 97% | In attachments |
| `mobilization_date` | 27 | 90% | In attachments / not stated |
| `deadline` | 25 | 83% | In attachments / not stated |
| `headcount` | 22 | 73% | General enquiry emails |
| `positions` / designation | 21 | 70% | In attachments |
| `client` | 18 | 60% | In attachments / internal intermediary |
| `project` | 16 | 53% | Not stated |
| `contact_email` | 8 | 27% | Often missing |
| `location` | 5 | 17% | Usually extractable |

### Google Drive MCP — noted
- MCP auto-connected at session start (claude.ai Google Drive integration)
- Not intentionally configured for this project
- Action: when onboarding real customers, replace with client-appropriate MCP (e.g. SharePoint, OneDrive)
- No data was written to Google Drive in this session

### DNS fix — re-applied
- Cloudflare DNS (1.1.1.1 / 1.0.0.1) re-applied via netsh in admin CMD
- Interface: "Wi-Fi 2"
- Required due to ISP blocking vercel.com / netlify.com (Meerut)
- Must re-apply after each network reset or laptop restart

### Git — commits pushed this session
| Commit | Description |
|---|---|
| `6f4cd58` | Fix field-name mismatch (Supabase → React via _to_frontend) |
| `6f21ade` | Phase 14f: password gate on React dashboard |
| `991ca04` | extractor: internal company exclusion list |
| `21ef0af` | MAILCRM_MASTER.md update + MAILCRM_COMMERCIAL_STRATEGY.md |

### CURRENT PHASE: 15 — PDF attachment text extraction

### Next session start point
1. Read MAILCRM_MASTER.md
2. Phase 15: add PDF/Word attachment text extraction to the pipeline
   - Graph API already fetches `hasAttachments` flag — extend to download attachment content
   - Extract text from PDF (PyMuPDF or pdfplumber) and Word (python-docx)
   - Append extracted text to email body before passing to AI extractor
   - Target: populate NULL client/role/rates fields that are currently in attachments
3. Re-run pipeline (max_emails=50) after Phase 15 to repopulate Supabase with richer data

---

## UPDATE: 2026-06-07 (Session 10) — Phase 15: Attachment extraction wired in

### Phase 15 — Attachment text extraction (verification stage)

- New file: `utils/attachment_extractor.py`
  - `extract_text_from_attachment(name, bytes)` → str
  - PDF: pdfplumber first, PyMuPDF fallback
  - DOCX: python-docx paragraph extraction
  - Other types: empty string + log warning
  - Never crashes pipeline — all exceptions return empty string

- Modified: `03_outlook/email_reader.py`
  - New function: `get_email_attachments(access_token, message_id)` → list of dicts
  - Graph API endpoint: GET /me/messages/{id}/attachments
  - Skips attachments >5MB and inline images (content_type: image/*)

- Modified: `run_parser.py`
  - When hasAttachments True: downloads attachments, extracts text, appends with `\n\n--- ATTACHMENT TEXT ---\n` separator
  - Prints one-time enriched body sample for verification
  - Tracks `att_emails_found` counter in run summary
  - `__main__` set to max_emails=10 with save_records() commented out for verification run

### Current status
- Extraction is wired in and running — NOT yet verified
- save_records() is commented out — no Supabase writes yet

### Next session start point
1. Read MAILCRM_MASTER.md
2. Run run_parser.py (max_emails=10, save_records commented out)
3. Paste enriched body sample into Claude.ai — verify extraction quality
4. If good: uncomment save_records(), re-run with max_emails=50 to push enriched records to Supabase
5. Check dashboard at https://mailcrm-api.vercel.app — confirm NULL fields are now populating

### CURRENT PHASE: 15 — pending verification + Supabase push

---

## UPDATE: 2026-06-07 (Session 11) — Phase 15 verification complete

### Phase 15 — verification run (max_emails=10)

- Ran `run_parser.py` and inspected the enriched body sample for the Baker
  Hughes "Fw: Oman DS Hiring" email (the one with `BH_Oman_Proposal_DS_V2.docx`
  + `Baker_Oman_DS_V2.xlsx` attachments).
- Found the gap: `_extract_docx()` only read paragraph text — the actual
  role/rate table lived in a Word table (cut off right at "Responsibility
  Matrix:"), and `.xlsx` attachments were skipped entirely (not handled).

### Fix — `utils/attachment_extractor.py`

- `_extract_docx()`: now also walks `doc.tables`, joining each row's cell
  text with `" | "` and appending after the paragraph text.
- New `_extract_xlsx()`: reads `.xlsx` attachments with `openpyxl`
  (read-only mode), iterating every worksheet/row, labelling each sheet
  with `[Sheet: <name>]`, joining non-empty cell values with `" | "`.
- `extract_text_from_attachment()` dispatch updated to route `.xlsx` to the
  new function.

### Re-run confirms the fix

- Enriched body for the Baker Hughes email grew from 1235 chars (DOCX
  paragraphs only, AI returned 0 roles) to 8968 chars (2649 DOCX + 6386 XLSX),
  now showing the full rate-card and training-matrix tables.
- AI extraction went from "no roles array" → **8 real roles with day rates**
  (Directional Driller, DD Engineer L1–L3, Drilling Engineering Coordinator,
  MWD Engineer L1–L3, $235–$528/day) plus 2 PSL-augmented rows (HSE, Training).
- Pulled the full record dicts for all 10 Baker Hughes/Oman rows — confirmed
  `client_name`, `client_country`, `rates`, `rates_currency`, `psl_categories`,
  `project_name`, `contact_person` all populated correctly from attachment text.

### `run_parser.py` — `save_records()` uncommented

- The Phase 15 verification gate is now passed — `save_records()` is live in
  `__main__` (Excel + Supabase write enabled). Currently still set to
  `max_emails=10`; bump to 50 for the full-inbox push next session.

### Known issue — Groq rate limit hit at session end

- Running the pipeline 3x back-to-back (verification → fix → re-verify →
  full-dict inspection) exhausted the Groq quota: Tier 3 classifier calls
  started returning `429 Too Many Requests`, falling back to
  "relevant (50%, Tier 3 unavailable)" and flagging emails for review instead
  of extracting them. The actual Supabase push with `save_records()` has NOT
  run yet — pending a clean run once the quota resets.

### Next session start point
1. Read MAILCRM_MASTER.md
2. Confirm Groq rate limit has reset (no 429s on a small test run)
3. Run `run_parser.py` with `max_emails=50` — `save_records()` is already
   live, this will push enriched records (with attachment-derived rates,
   client names, role tables) to Excel + Supabase
4. Check dashboard at https://mailcrm-api.vercel.app — confirm previously-NULL
   fields (client_name, rates, headcount, etc.) are now populating from
   attachment-enriched extractions

### CURRENT PHASE: 15 COMPLETE — Supabase push pending (Groq quota reset)

---

## UPDATE: 2026-06-09 (Session 12) — Phase 15 Closed + Zavenir Daubert Pipeline Live

### Phase 15 — CLOSED
- Full 50-email push completed. 120 records now in Supabase `crm_requirements`.
- ZIP extraction working: MEDCO RFQ ZIP — 5 files, 3 extracted (6,007 chars), 2 scanned image PDFs correctly fell through.
- Nested ZIPs (ZIPs inside ZIPs) currently skipped — flagged for future fix.
- Excel stays at 35 rows (deduplication by email_id working correctly).
- Phase 15 fully closed.

### GET CRM — Data Quality Issue (Flagged, Deferred to Phase 16)
- Dashboard showing very few fields populating per record, low confidence scores.
- Root cause unknown — suspected: prompt quality, 3000-char truncation, attachment text positioning.
- Phase 16 to investigate: debug mode (single email end-to-end print), prompt rewrite, truncation increase.
- Target: confidence score >0.75 on 80%+ of relevant emails.

### GET Dashboard — Duplicate Records (Flagged, Deferred)
- Same emails processed in two runs appear with both 20260606 and 20260609 prefixes.
- June 6 batch: sparse data (pre-attachment extraction). June 9 batch: enriched.
- Fix needed: clear old records from Supabase or deduplicate by email_id across date prefixes.

### Zavenir Daubert Pipeline — NEW (Full Build This Session)

#### New Files Created:
- `configs/zavenir_daubert.py` — 13 product categories, 8 industry segments, 16 fields, sender filter, Excel output path, Supabase table name
- `utils/zavenir_extractor.py` — Groq extractor adapted for Zavenir; one record per email (no multi-role splitting); validates against config lists at runtime
- `run_zavenir_parser.py` — standalone runner; filters by tarora@zavenir.com; attachment extraction wired in; saves to Excel + Supabase
- `scripts/create_zavenir_table.sql` — SQL for zavenir_requirements table
- `dashboards/zavenir/` — full React dashboard (Vite + TailwindCSS); password gated (MailCRM@2026)

#### Supabase:
- New table: `zavenir_requirements` (18 columns, GENERATED ALWAYS AS IDENTITY PK)
- 3 real records pushed from first run

#### API (api/main.py):
- New endpoints added (existing endpoints untouched):
  - GET /zavenir/records — optional filters: status, product_category, industry_segment
  - GET /zavenir/stats — total_records, last_7_days, active, top_product_category, status_breakdown
- Commit: 738a5a0

#### Dashboard:
- Local: http://localhost:5173
- Production: https://zavenir-dashboard.vercel.app
- Password: MailCRM@2026
- Columns: Req ID, Customer, Segment, Product Category, Brand, Qty, Location, Delivery, Status, Received
- KPIs: Total Records, Last 7 Days, Active, Top Category

#### Product Categories (13):
Specialty Greases, Rust Preventive Coatings, Metalworking Fluids, Corrosion Inhibitor Additives (SACI), Food Grade Lubricants, Oil and Gas Lubricants, MIL-SPEC Defense Lubricants, Adhesives and Sealants, Sound Deadening NVH, Process Oils, Vapor Corrosion Inhibitors (VCI), Defoamers and Cleaners, Other

#### Industry Segments (8):
Steel, Automotive, Oil and Gas, Defense, Marine, Aerospace, General Engineering, Other

#### First Run Results:
- 3 emails from tarora@zavenir.com found and processed
- ELEMATIC INDIA PVT LTD — VCI Roll → Other (VCI category added post-run, will fix on next run)
- Auto International Binola — X-Cool → Metalworking Fluids ✅
- Kapl Rohtak — ADDITIVE D Defoamer → Other (Defoamers category added post-run, will fix on next run)

### Zavenir — Thread Intelligence Gap Identified
- Auto International Binola email is a multi-email thread (May 20 – June 5, 2026)
- Three products discussed across thread: Nox Rust 307 (₹282.36/L), Nox Rust R-823 (₹260.00/L), X-Cool 1000 (₹290.00/L)
- Pipeline captured only the most recent email snapshot — missed full thread context
- Phase 17 planned: Thread Intelligence — stitch emails by conversation ID, extract one opportunity per product, track negotiation stage per product

### CURRENT PHASE: 16 — GET CRM Intelligence Layer Improvement

### Next Session Start Point:
1. Read MAILCRM_MASTER.md
2. Phase 16: improve GET CRM intelligence layer
3. Zavenir: re-run run_zavenir_parser.py
4. GET dashboard: clean up duplicate records
5. Phase 17 (Zavenir): Thread Intelligence — spec and build

---

## UPDATE: 2026-06-09 (Session 13) — Phase 16 CLOSED + Zavenir Re-run + Pre-Phase 17 Cleanup

### Phase 16 — CLOSED (GET CRM Intelligence Layer)

Five fixes applied in sequence, tracked via `debug_extractor.py` (read-only single-email diagnostic tool):

#### Fix 1 — Zavenir domain isolation
- `config/email_filters.py`: removed `zavenir.com` from `EXCLUDED_DOMAINS`.
- Root cause: `email_reader.py` applies `filter_emails()` before returning, so adding zavenir.com to EXCLUDED_DOMAINS blocked both pipelines. The GET pipeline already ignores Zavenir emails because `zavenir.com` is not in `ALLOWED_DOMAINS` — the EXCLUDED entry was redundant and self-defeating.

#### Fix 2 — Confidential false-positive (legal footer stripper)
- `05_classifier/email_classifier.py`: added `_FOOTER_PATTERNS` list (18 patterns), `strip_legal_footer()` function, `_is_confidential_subject()` helper.
- Post-prediction override: "confidential" label only sticks if email subject itself contains the word.
- `08_advanced/edge_case_handler.py`: `strip_legal_footer()` called in Step 5 of `preprocess_email()` so every downstream consumer (ML, Tier 3, Groq) sees clean text.
- `CONFIDENCE_THRESHOLD` lowered 0.75 -> 0.50 temporarily (retrain classifier before raising back).

#### Fix 3 — Attachment byte key mismatch
- `get_email_attachments()` returns dicts with key `"bytes"`, not `"content_bytes"`.
- Fixed in `debug_extractor.py`. After fix: `1. RFQ BF29858.zip` -> 49,537 chars extracted from 5 internal files.

#### Fix 4 — ZIP file priority sort
- `utils/attachment_extractor.py`: added `_zip_file_priority()` sort key.
  - Priority 0 (first): files with "boq", "rfq", "scope of work", "rate schedule" in name.
  - Priority 1 (middle): generic files.
  - Priority 2 (last): boilerplate — "gcoc", "omanization", "terms and condition", "appendix".
- Per-file cap: `_ZIP_PER_FILE_MAX_CHARS = 8000` (raised from 3000 in Phase 16).
- Effect: for MEDCO RFQ ZIP (8 files), BOQ and Scope of Work reach Groq first instead of the 40K-char GCOC legal document.

#### Fix 5 — Truncation limit raised
- `04_email_parser/parser.py`: `max_chars` raised 3000 -> 12000.
- `debug_extractor.py`: `MAX_CHARS` synced to 12000.

### Fill Rate Progression (MEDCO RFQ BF29858 — Production Surveillance Service)

| Run | Config | Sent to Groq | Confidence | Fill rate | Key new fields |
|---|---|---|---|---|---|
| Baseline | 3K total | 3,000 chars | 0.7 | 19% (56/302) | — |
| Fix 4+5 v1 | 15K total, 3K/file | 11,922 chars | 0.8 | 68% (26/38) | project_name (specific), location (Nimr), duration, work_schedule, nationality |
| Fix 5 final | 12K total, 8K/file | 12,000 chars | **0.9** | **71% (27/38)** | + experience_years: "8-10+ years" |

Remaining empty fields at 71%: genuine document gaps (rates = blank vendor template, certifications = not listed, mobilization_date = "Bidder to provide").

### ML Classifier — Deferred

- Root cause confirmed: all 36 "relevant" training samples in `training_data_v2.csv` are internal GET forwarding emails (sprabhat@getglobalgroup.com). Zero inbound client RFQ examples.
- Classifier scores real forwarded client RFQs at 26-36% irrelevant — has never seen that pattern.
- Deferred to Phase 17 backlog. Threshold stays 0.50. Training data needs inbound RFQ examples added.

### Zavenir Re-run — 4 Records, Categories Fixed

- Re-run found 0 emails via inbox fetch (emails archived out of inbox).
- Fix: `run_zavenir_parser.py` now uses `_search_zavenir_emails()` — Graph API `$search="tarora@zavenir.com"` across ALL folders (not inbox-only). Import `requests` added.
- 4 emails found and processed:

| Customer | Product | Qty |
|---|---|---|
| Unominda | Defoamers and Cleaners (was Other) | 20 Ltr |
| ELEMATIC INDIA PVT LTD | Vapor Corrosion Inhibitors (VCI) (was Other) | 10 NOS |
| Auto International Binola | Rust Preventive Coatings | ? |
| Kapl Rohtak | Defoamers and Cleaners (was Other) | 20 ltr |

- All 4 upserted to Supabase `zavenir_requirements`. Confidence: 80% all.

### GET Supabase Cleanup — DONE

- `crm_requirements` had 150 rows: 30 from June 6 run (sparse, pre-attachment extraction) + 120 from June 9 run (attachment-enriched).
- Deleted all 30 `REQ-20260606-*` records.
- **120 rows remain** (all June 9 enriched records).

### Strategic Pivot

- **GET CRM: FROZEN.** 120 clean records in Supabase, dashboard live at https://mailcrm-api.vercel.app. No new GET feature work planned.
- **All new development: Zavenir Daubert pipeline.** Phase 17 = Zavenir Thread Intelligence.
- **ICP confirmed:** MailCRM targets B2B product-selling companies (specialty chemicals, lubricants, industrial goods) that receive enquiries by email and need to track them as opportunities. Not oil & gas manpower.

### Files Changed This Session

| File | Change |
|---|---|
| `config/email_filters.py` | Removed `zavenir.com` from EXCLUDED_DOMAINS |
| `05_classifier/email_classifier.py` | Footer stripper + confidential override + threshold 0.75->0.50 |
| `08_advanced/edge_case_handler.py` | Step 5: strip_legal_footer() in preprocess_email() |
| `utils/attachment_extractor.py` | ZIP priority sort + per-file 8K cap + XLSX support |
| `04_email_parser/parser.py` | Truncation 3000->12000 |
| `run_zavenir_parser.py` | _search_zavenir_emails() all-folder Graph $search |
| `debug_extractor.py` | New — read-only single-email diagnostic (MAX_CHARS=12000) |
| `configs/zavenir_daubert.py` | New — 13 product categories, 8 segments, sender filter |
| `utils/zavenir_extractor.py` | New — Groq extractor for Zavenir (single record per email) |
| `scripts/create_zavenir_table.sql` | New — Supabase DDL for zavenir_requirements |
| `dashboards/zavenir/` | New — React dashboard (Vite + TailwindCSS, mobile-responsive, password gated) |
| `api/main.py` | GET /zavenir/records + GET /zavenir/stats endpoints (commit 738a5a0) |

---

### Phase 17 — COMPLETE: Zavenir Thread Intelligence

#### What was built:
- `fetch_conversation(access_token, conv_id)` in `utils/zavenir_extractor.py` — fetches all emails in a thread via Graph API `$filter=conversationId eq '...'`, sorted oldest-first
- `stitch_thread(email_list, max_chars=15000)` — chronological stitching with `[DATE | SENDER]` prefix per email, 15K char cap with truncation marker
- `extract_zavenir_thread(thread_text)` — Groq call with `{"enquiries": [...]}` wrapper; returns one record per distinct product model
- `THREAD_SYSTEM_PROMPT` — key rule: "different model numbers or grades of the same brand are DIFFERENT products — create one record per model number"; prevents Nox-Rust 307 + R-823 merging into one record
- `_clean_body()` updated — `html.unescape()` added after HTML tag-strip; decodes `&lt;`, `&amp;`, `&nbsp;`, `&#8764;` before Groq sees the text
- `configs/zavenir_daubert.py` renamed → `configs/clients/zavenir.py`; `configs/clients/__init__.py` and `configs/clients/client_template.py` added
- `utils/retry.py` updated — respects `Retry-After` / `x-ratelimit-reset-*` headers on 429; 60s fallback if header absent
- 15s inter-email sleep in `run_pipeline()` to stay within Groq TPM limits
- `_make_req_id(email_id, idx)` — multi-product threads get suffixes `-01`, `-02`, `-03` per product
- `DRY_RUN` flag in `run_zavenir_parser.py` for safe testing without saving

#### Phase 17 Production Results (2026-06-09):

| Email | Records | Products |
|---|---|---|
| FW: Alloy Wheel Cleaner (Unominda) | 1 | X-Clean 2070 BF |
| FW: RFQ - VCI Roll (ELEMATIC) | 1 | Vapor Corrosion Inhibitors (VCI) |
| FW: Offer-Auto International Binola | **3** | Nox-Rust 307 + Nox-Rust R-823 + X-Cool 1000 |
| FW: Defoamer quotation (Kapl Rohtak) | 1 | ADDITIVE D |
| **Total** | **6** | — |

Auto International: 1 record (pre-Phase 17, generic Nox-Rust) → **3 records** (one per model number). Thread intelligence working as designed.

#### Hardening Backlog:
- **MSAL token refresh mid-run**: 80+ min of cumulative Retry-After waits expired the access token on email 4; `fetch_conversation` returned 401, fell back to single-email body gracefully. Fix: re-call `get_access_token()` at the start of each email iteration before `fetch_conversation()`.
- **Zavenir dedup**: multiple dry runs + the production run created duplicate records in `zavenir_requirements`; clean before next production run.

#### Commit: `8dd103d`

---

---

## UPDATE: 2026-06-10 (Session 14) — Deploy Blockers Resolved + Phase 18

### Deploy Blockers from Session 13 — RESOLVED

**1. Git author email mismatch (blocked Vercel auto-deploy from GitHub)**
- Root cause: the `591999b` commit author email didn't match a verified email on the GitHub account linked to Vercel, so Vercel silently skipped auto-deploy on push.
- Fix: `git config --global user.email "saral.prabhat1@gmail.com"` -> `git commit --amend --reset-author --no-edit` -> `git push --force-with-lease`.
- Result: HEAD re-authored as `df409b5`, force-pushed to `saralprabhat1/mailcrm-api` main.

**2. Mobile layout fix — deployed and confirmed live**
- Deployed manually from `dashboards/zavenir/` with a fresh `VERCEL_TOKEN` (`npx vercel --prod --yes`).
- Confirms commits `591999b` + `765e30d` (mobile layout fix) are live at https://zavenir-dashboard.vercel.app.

**3. Desktop layout bug — detail pane cut off — FIXED**
- Root cause: flex children had no `min-w-0`, so `whitespace-nowrap` table cells forced the records table past its flex-basis and pushed the detail pane off the right edge of the viewport.
- Fix:
  - `dashboards/zavenir/src/App.jsx` — added `min-w-0` to the records-table flex wrapper.
  - `dashboards/zavenir/src/components/RecordsTable.jsx` — added `min-w-0` to the root div; `overflow-y-auto` -> `overflow-auto` on the table scroll container.
- Built and deployed via `npx vercel --prod --yes` from `dashboards/zavenir/`.

---

### Phase 18 — COMPLETE: Forwarded Sender + Auto-Assign + Conversation Timeline

Scope confined to the Zavenir-specific layer: `utils/zavenir_extractor.py`, `run_zavenir_parser.py`, `configs/clients/zavenir.py`, `scripts/*.sql`, `dashboards/zavenir/src/components/DetailPanel.jsx`. GET Global pipeline untouched.

#### Feature 1 — Forwarded sender extraction
- New regexes in `utils/zavenir_extractor.py`: `_FROM_LINE_RE`, `_FORWARD_CTX_RE`, `_NAME_EMAIL_ANGLE_RE`, `_NAME_EMAIL_MAILTO_RE`, `_BARE_EMAIL_RE`.
- New functions: `_parse_from_value()`, `_find_forward_header_index()`, `extract_forwarded_sender(text)` — scans cleaned body text (line-by-line) for a `From:` line followed within 4 lines by `Sent:`/`Date:`/`To:`/`Subject:`, skipping any block whose email is `SENDER_FILTER` (tarora@zavenir.com).
- `run_zavenir_parser.py`: per email, runs `email_parser.strip_html()` on the anchor email body (preserves line breaks), then `extract_forwarded_sender()`. If found, `sender_name`/`sender_email` = the forwarded customer. If not found, falls back to the Graph API `from` field — but if that's `tarora@zavenir.com`, both are set to `None` instead.
- **Constraint verified**: `tarora@zavenir.com` does not appear as `sender_email` on any of the 6 test records (2 fell back to `None` rather than the forwarder's address — see Test Results below).

#### Feature 2 — Auto-assign deal (`assigned_to`)
- `_search_zavenir_emails()` now selects `toRecipients` and returns `to_recipients: [{name, address}, ...]` per email.
- New regex `_ASSIGNMENT_PHRASES_RE` (please handle / assign(ed) to / over to you / your lead / take this / follow up / kindly handle / please action / please take / for your action / requesting you to).
- New function `detect_assigned_to(forwarder_note, to_recipients)` (and `get_forwarder_note(text)` to isolate the text above the forward header): finds the first `to_recipients` address ending in `@zavenir.com` that isn't `tarora@zavenir.com` -> `assigned_to = "Name <email>"`. Confidence = `"high"` if assignment language is also present in the forwarder's note, `"low"` if only the recipient signal is present, `null` if no internal recipient (i.e. forwarded only to `saral.prabhat@outlook.com`).
- `configs/clients/zavenir.py` `FIELDS`: added `assigned_to`, `assigned_to_confidence`.

#### Feature 3 — Conversation timeline
- `fetch_conversation()` now also returns `sender_name` per message; `stitch_thread()` prefixes each message with `[YYYY-MM-DD | Sender Name <email>]` (was `[YYYY-MM-DD | email]`).
- `THREAD_SYSTEM_PROMPT` updated: instructs the model to also return a top-level `conversation_timeline` string — one line per thread message in the format `[Mon D | Sender Name | Company] -> summary`, lines joined with `\n`.
- `_build_record()` / `_empty_record()` / `extract_zavenir_thread()`: `conversation_timeline` extracted once from the outer Groq response and copied onto every product record from that thread.
- `configs/clients/zavenir.py` `FIELDS`: added `conversation_timeline`.

#### Dashboard — `dashboards/zavenir/src/components/DetailPanel.jsx`
- New "Assigned To" field (in the Enquiry section) with a confidence badge (green = high, amber = low).
- New "Conversation Timeline" section — monospace, `whitespace-pre-wrap`, rendered only when non-empty.
- New "Sender Name" field next to "Sender Email" in the footer block.
- Built and deployed to https://zavenir-dashboard.vercel.app via `npx vercel --prod --yes` from `dashboards/zavenir/`.

#### Schema changes
- `scripts/create_zavenir_table.sql` updated (fresh-install schema): added `sender_name`, `assigned_to`, `assigned_to_confidence`, `conversation_timeline` (all `TEXT`).
- **New file `scripts/alter_zavenir_table_phase18.sql`** — `ALTER TABLE ... ADD COLUMN IF NOT EXISTS` migration for the *live* Supabase table. **Status: RUN — live `zavenir_requirements` table now has `sender_name`, `assigned_to`, `assigned_to_confidence`, `conversation_timeline` (all `TEXT`).** Ready for a non-DRY_RUN pipeline run.

#### Test Results — DRY_RUN parse of 4 emails / 6 product records (2026-06-10)

req_id hashes match the existing `data/zavenir_crm.xlsx` rows (same conversationId -> same MD5 hash, only the date prefix changed from `20260609` to `20260610`).

| req_id (hash) | Customer / Product | Before: sender_email | After: sender_name | After: sender_email | assigned_to | conversation_timeline |
|---|---|---|---|---|---|---|
| 5617F9 | Unominda / X-Clean 2070 BF | `tarora@zavenir.com` | — | `null` | `null` | 3-line summary (Mar 24 - May 7, all Tarul Arora — no embedded customer email in this thread) |
| 8EAD0D | ELEMATIC INDIA PVT LTD / VCI Roll | `tarora@zavenir.com` | Tanwar Dhiraj | `Dhiraj.Tanwar@elematic.com` | `null` | 2-line summary (Jun 4 RFQ -> Jun 9 forwarded) |
| 2ACFF3-01 | Auto International / Nox-Rust 307 | `tarora@zavenir.com` | Amitrajit Sinha | `amitrajitsinha@autointernational.co.in` | `null` | 10-line summary (May 20 - Jun 9 full negotiation) |
| 2ACFF3-02 | Auto International / Nox-Rust R-823 | `tarora@zavenir.com` | Amitrajit Sinha | `amitrajitsinha@autointernational.co.in` | `null` | same 10-line thread summary |
| 2ACFF3-03 | Auto International / X-Cool 1000 | `tarora@zavenir.com` | Amitrajit Sinha | `amitrajitsinha@autointernational.co.in` | `null` | same 10-line thread summary |
| 9CB26E | Kapl Rohtak / Defoamer | `tarora@zavenir.com` | — | `null` | `null` | 1-line summary (Jun 9, Tarul Arora forwarded quotation) |

**Observations:**
- `tarora@zavenir.com` is gone from `sender_email` on all 6 records (constraint met). 4/6 resolved to the real customer contact (ELEMATIC, Auto International x3); 2/6 (Unominda, Kapl Rohtak) had no parseable `From:`/`Sent:` header block in the body — these look like Tarul forwarding her own prior quotations rather than a customer's email, so `sender_name`/`sender_email` correctly fall back to `null` rather than a wrong value.
- `assigned_to` is `null` on all 6 because every email's `toRecipients` is only `saral.prabhat@outlook.com` (external monitoring) — exactly the "no internal recipient" case in the spec. The feature is wired correctly; it will populate once Tania starts cc'ing other `@zavenir.com` staff on forwards.
- `conversation_timeline` populated on all 6 records with real `\n`-separated multi-line summaries, correctly attributing each thread message to a person + company (e.g. distinguishing Multitech Marketing as the channel partner vs. Auto International as the customer).

#### Files Changed This Session

| File | Change |
|---|---|
| `utils/zavenir_extractor.py` | Forwarded-sender regexes + `extract_forwarded_sender`, `get_forwarder_note`, `detect_assigned_to`; `fetch_conversation`/`stitch_thread` now carry `sender_name`; `THREAD_SYSTEM_PROMPT` + `_build_record`/`_empty_record`/`extract_zavenir_thread` add `conversation_timeline` |
| `run_zavenir_parser.py` | `_search_zavenir_emails()` selects `toRecipients`; per-email Phase 18 block computes `sender_name`/`sender_email`/`assigned_to`/`assigned_to_confidence`; `_save_to_supabase()` writes the 4 new columns |
| `configs/clients/zavenir.py` | `FIELDS` += `sender_name`, `assigned_to`, `assigned_to_confidence`, `conversation_timeline` |
| `scripts/create_zavenir_table.sql` | Fresh-install schema += 4 new `TEXT` columns |
| `scripts/alter_zavenir_table_phase18.sql` | New — live-table migration (manual, Supabase SQL Editor) |
| `dashboards/zavenir/src/components/DetailPanel.jsx` | "Assigned To" field + confidence badge, "Conversation Timeline" section, "Sender Name" field |
| `dashboards/zavenir/src/App.jsx`, `RecordsTable.jsx` | Desktop overflow fix (`min-w-0`, `overflow-auto`) |

#### Commit: `1b8bde8` — pushed to `saralprabhat1/mailcrm-api` main

---

### Customer Master List — `zavenir_customers_base.xlsx` (external artifact, 633 customers)

- Built in a separate claude.ai chat session (not this repo/session) — a master list of **633 Zavenir customers**.
- **Current location:** `C:\Users\Saral\Downloads\zavenir_customers_base.xlsx` on Saral's machine — **not yet copied into this repo**.
- **Plan:** copy to `data/zavenir_customers_base.xlsx`, create a new `zavenir_customers` Supabase table, and upload this list as the seed/reference customer master (used for matching incoming enquiries to known customers, and as the base for domain enrichment below).

### Backlog — Customer Domain Enrichment (new)

- Enrich the 633-customer master list with each customer's company domain/website.
- Purpose: once domains are known, incoming enquiry sender domains (Feature 1's `sender_email`) can be matched against the customer master for de-dup/linking, and `assigned_to`/customer-matching logic can be made domain-aware instead of name-based.
- Implementation: a domain enrichment script (TBD — likely a lookup/scrape step run once over the 633-row list, output added as a column before/at Supabase upload).

---

### CURRENT PHASE: 18 COMPLETE (commit `1b8bde8`, pushed)

### Next Session Start Point
1. Read MAILCRM_MASTER.md
2. Copy `C:\Users\Saral\Downloads\zavenir_customers_base.xlsx` -> `data/zavenir_customers_base.xlsx` (do this **before** the Supabase upload task below)
3. Create `zavenir_customers` table in Supabase (new DDL script, modeled on `scripts/create_zavenir_table.sql`) and upload the 633-row customer master
4. Build the Customer Domain Enrichment script (see Backlog above) — enrich the 633 customers with company domains
5. Re-run `run_zavenir_parser.py` (DRY_RUN=False) for a full production pass with Phase 18 fields — Supabase schema is live and ready
6. Clean duplicate records in `zavenir_requirements` Supabase table (multiple test runs created duplicates — deduplicate by `req_id`)
7. MSAL token refresh mid-run hardening (`run_zavenir_parser.py` — re-acquire token before each `fetch_conversation()` call)
8. ML classifier retrain — `training_data_v2.csv` has 36 "relevant" samples but all are outbound GET emails; need inbound RFQ examples added before retraining

---

## UPDATE: 2026-06-10 (Session 15) — Backlog Clearance: Customer Master Scripts + Production Run + Dedup + Token Hardening

### MSAL token hardening — DONE
- `run_zavenir_parser.py`: imports `get_access_token_or_none` from `utils/auth.py`
  and calls it at the **start of each email iteration**, before `fetch_conversation()`.
- `acquire_token_silent()` is cheap — returns the cached token if still valid,
  refreshes only near expiry. If refresh fails, the loop keeps the existing
  token and warns instead of crashing.
- Verified live in the production run: "Cache loaded / Token saved" printed
  before each of the 4 emails.

### Production run — DONE (DRY_RUN=False, Phase 18 fields live)
- 4 Zavenir emails found, **6 product records** extracted and saved to
  Excel + Supabase (Unominda X-Clean 2070 BF, ELEMATIC VCI Roll,
  Auto International Nox-Rust 307 / Nox-Rust R-823 / X-Cool 1000,
  KAPL Rohtak ADDITIVE D). req_ids: `REQ-20260610-*`.
- Phase 18 columns (`sender_name`, `assigned_to`, `assigned_to_confidence`,
  `conversation_timeline`) written to Supabase for the first time.
- **Observation:** `fetch_conversation()` returned only 1 email per thread this
  run (Auto International thread previously had 10). Extraction still recovered
  all 3 products from the quoted text inside the forward, but thread context is
  thinner than the Phase 18 DRY_RUN test. Watch on next run — possibly archived
  messages no longer matching the conversationId `$filter`.

### Dedup — DONE (`scripts/dedup_zavenir_requirements.py`, new)
- Key insight: req_id = `REQ-YYYYMMDD-HASH-NN` where the **date prefix is the
  run date** — re-running the same conversation on a new day creates a new
  req_id. So dedup keys on the stable `HASH-NN` part, keeps the row with the
  newest date prefix (ties: `created_at`, then `id`), deletes the rest.
- Run result: 16 rows -> 10 (six June-9 date-prefix dupes deleted).
- 4 remaining pre-Phase-17 rows (hashed on `email_id`, not `conversationId` —
  e.g. generic "Nox-Rust" single record) were the same 4 enquiries; deleted
  manually by id. **`zavenir_requirements` is now exactly 6 clean rows**, all
  from today's Phase-18-enriched run.
- `data/zavenir_crm.xlsx` deduped the same way (16 -> 6 rows), header
  formatting re-applied. Excel and Supabase now mirror each other exactly.
- Script is safe to re-run any time (no dupes -> zero deletions).

### Customer master scripts — WRITTEN (blocked on 2 manual steps)
- **`scripts/create_zavenir_customers_table.sql`** (new) — DDL for
  `zavenir_customers`: `customer_name` (UNIQUE NOT NULL, upsert key), `domain`,
  `domain_source` ('xlsx'|'email'|'clearbit'), city/state/country/address,
  `industry_segment`, contact fields, `notes`, `source`, timestamps; index on
  `domain` (the enquiry-matching lookup path).
- **`scripts/upload_zavenir_customers.py`** (new) — reads
  `data/zavenir_customers_base.xlsx`, normalizes whatever headers the file has
  (maps variants: "Company Name"/"Customer"/"Account" -> `customer_name`,
  "Website"/"URL" -> `domain`, etc.), prints mapped + skipped columns,
  cleans/dedupes by customer_name, batch-upserts to Supabase
  (on_conflict=customer_name, 100/batch). Safe to re-run.
- **`scripts/enrich_customer_domains.py`** (new) — for each row missing a
  domain: (1) derive from contact email if business domain (free, exact);
  (2) else Clearbit Autocomplete API (free, keyless — endpoint verified
  working this session) with a name-similarity guard (difflib >= 0.55 after
  stripping legal suffixes) so wrong-company domains are never written;
  (3) else leave blank + list for manual lookup. Writes back to the xlsx
  (checkpoint every 25 lookups) and updates Supabase as it goes.
- **BLOCKED — two manual steps before these can run:**
  1. `data/zavenir_customers_base.xlsx` was **not found anywhere on this
     machine** (searched data/, Downloads, user profile) — copy it in first.
  2. Run `scripts/create_zavenir_customers_table.sql` in the Supabase SQL
     Editor (no Postgres connection string in .env, so DDL is manual —
     confirmed table does not exist yet via REST probe).
  Then run: `python scripts/upload_zavenir_customers.py` followed by
  `python scripts/enrich_customer_domains.py`.

### Files changed this session
| File | Change |
|---|---|
| `run_zavenir_parser.py` | Per-email silent token re-acquire before `fetch_conversation()` |
| `scripts/dedup_zavenir_requirements.py` | New — HASH-NN dedup, keep latest |
| `scripts/create_zavenir_customers_table.sql` | New — `zavenir_customers` DDL |
| `scripts/upload_zavenir_customers.py` | New — column-adaptive xlsx -> Supabase upload |
| `scripts/enrich_customer_domains.py` | New — email + Clearbit domain enrichment |
| `data/zavenir_crm.xlsx` | Deduped 16 -> 6 rows (not committed — data/ is gitignored) |

### CURRENT PHASE: 18 complete + backlog cleared (except customer-master upload, blocked on manual steps)

### Next Session Start Point
1. Read MAILCRM_MASTER.md
2. Copy `zavenir_customers_base.xlsx` -> `data/zavenir_customers_base.xlsx`
3. Run `scripts/create_zavenir_customers_table.sql` in Supabase SQL Editor
4. `python scripts/upload_zavenir_customers.py` — upload the 633-row master
5. `python scripts/enrich_customer_domains.py` — fill missing domains
6. Check `fetch_conversation()` thread depth (returned 1 email/thread this run vs 10 previously — see Observation above)
7. ML classifier retrain — `training_data_v2.csv` needs inbound RFQ examples added before retraining