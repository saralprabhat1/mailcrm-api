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

### CURRENT PHASE: 14d — React dashboard (next session)