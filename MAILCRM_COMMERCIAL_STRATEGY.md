# MailCRM — Commercial Strategy Master File
> Separate from MAILCRM_MASTER.md (technical build log)
> This file = business strategy, market positioning, commercialization discussion only
> Last updated: 2026-06-06 | Session 1

---

## CURRENT STRATEGIC DIRECTION

MailCRM is an AI system that sits on top of any team's email, reads inbound business emails, extracts structured data automatically, and gives leadership a live pipeline — without anyone manually entering anything.

The pilot was built for an upstream oil & gas manpower consultancy (GET Global). That specific use case (manpower supply BD tracking) is NOT the target market. The engine is domain-agnostic and will be deployed for other business flows and processes.

**Target industry: Oil & Gas — OFS and Operators**
**Target customer: Mid-tier OFS companies operating in MENA**
**Current phase: Discovery — we don't know enough yet to build for this customer**

---

## TARGET CUSTOMER (CURRENT BEST HYPOTHESIS)

**Who:** Mid-tier oilfield services companies operating in Gulf/MENA
**Examples:** Petrofac, Kentech, Sapura, NES Fircroft, Enpro, Hunting Energy, Frank's International, regional EPC contractors
**Size:** ~$50M–$2B revenue, BD teams of 10–50 people
**Why them:**
- Bidding on operator contracts, tracking RFQs, managing accounts — all via email and Excel
- Too complex for generic CRM out of the box
- Too small/decentralized to have properly implemented enterprise CRM
- Can make a buying decision in weeks, not years
- Tier-1 giants (SLB, Halliburton, BH) already have systems — long procurement cycles, wrong fit for now

**Secondary targets (longer term):**
- Operators: ADNOC, Aramco, KOC, TotalEnergies, Shell — vendor/procurement correspondence flows
- Tier-1 OFS regional offices where global CRM exists but adoption is broken

---

## WHAT WE DO NOT KNOW YET (KNOWLEDGE GAPS)

These must be answered through discovery conversations — cannot be assumed:

1. How do mid-tier OFS BD teams actually track bids and client requirements day to day?
2. What is the specific broken moment in their workflow — the thing that costs them most?
3. Do they already have a CRM? If yes, is it actually used and working?
4. Who makes the buying decision at a mid-tier OFS company for a tool like this?
5. What would a low-friction pilot entry point look like for them?
6. What business flows beyond manpower tracking exist inside OFS/operators that MailCRM could serve?

---

## IMMEDIATE ACTIONS (PRIORITIZED)

| # | Action | Purpose | Timeframe |
|---|---|---|---|
| 1 | Draft LinkedIn outreach message (Claude to help) | Start 10 discovery conversations | This week |
| 2 | Mine existing network for warm intros | 5 messages to ex-Halliburton/MI Swaco/GET contacts asking for introductions | This week |
| 3 | Follow BD managers / commercial directors at mid-tier OFS on LinkedIn | Free market research, learn their language | Ongoing |
| 4 | Build one-page problem statement | Leave-behind for every conversation, outreach attachment | Before first call |
| 5 | Start LinkedIn content — 1 post/week on OFS commercial ops / AI workflow | Build credibility before product pitch | Ongoing |
| 6 | Build list of 20 target companies explicitly | Systematic outreach hit list | Week 2 |
| 7 | Define pilot/demo entry point | What does "show me" look like for a prospect? | Before first call |

---

## KEY DECISIONS MADE

| Decision | Rationale |
|---|---|
| NOT targeting manpower companies in upstream O&G | Too narrow, better niches exist within the same industry |
| Staying within Oil & Gas — OFS + Operators | Saral has 10 years domain context — this is the real moat, not the tech |
| Starting with mid-tier OFS, not Tier-1 giants | Tier-1 has systems, long procurement cycles; mid-tier has the gap and can decide fast |
| No investors yet | Stack costs near-zero; bootstrap until 2-3 paying clients, then revisit |
| No company registration yet | Do it when second party is ready to pay; Pvt Ltd is the right structure when ready |
| Not giving MailCRM away free | Free signals no value; founding customer discount yes, free no |
| Discovery before more building | Knowledge gap is bigger than product gap right now |
| LinkedIn outreach before LinkedIn post | Need conversations first, not inbound before product is ready to demo |
| MAILCRM_COMMERCIAL_STRATEGY.md kept separate from MAILCRM_MASTER.md | Technical log vs business strategy — two files, two concerns |

---

## OPEN QUESTIONS (PARKED, NOT FORGOTTEN)

- What specific business flow inside mid-tier OFS is the right entry point? (needs discovery)
- Pricing model: setup fee + retainer vs per-seat SaaS? (decide after first client conversation)
- When to register a company? (trigger = second party willing to pay)
- When to raise funding? (trigger = 2-3 paying clients with MRR proof)
- Path 3 (license/OEM to CRM companies like Salesforce/HubSpot) — revisit in 2-3 years with traction
- ADIPEC November — worth attending independently for networking?
- What does the deployment story look like for a mid-tier OFS pilot? (30-day trial? sandbox?)

---

## COMPETITIVE LANDSCAPE (CURRENT KNOWLEDGE)

| Player | What they do | Why not a direct threat |
|---|---|---|
| Recruiterflow, Bullhorn, Atlas | Staffing/recruitment CRMs with AI | Horizontal, no O&G domain knowledge, require active data entry |
| Salesforce for Energy | Enterprise CRM configured for upstream O&G | Too expensive, too complex, wrong fit for mid-tier |
| Riger CRM | Built specifically for oilfield BD/VP Sales | Closest competitor — focused on OFS sales side, not email-to-CRM automation |
| AIEmailParser.com | General AI email data extraction | No domain knowledge, no CRM logic, no pipeline tracking |
| People.ai, Gong | Email capture + CRM sync | Enterprise-only, no O&G specialization |

**MailCRM's actual moat:**
- Domain specificity (O&G commercial workflows, MENA context)
- Founder is a practitioner — understands the pain from the inside
- Zero-entry-effort model — reads email, no AM data input required
- Microsoft stack deployment (Outlook/Graph API) — what every O&G company already runs

---

## PATHS TO MARKET (ALL OPTIONS)

| Path | Description | Status |
|---|---|---|
| Path 1 — Bootstrap SaaS | Pilot internally → charge companies directly | Right destination eventually, not now |
| Path 2 — Consultancy | Deploy for clients as paid setup service | **Best immediate move** |
| Path 3 — License/OEM | Sell tech to CRM company as module | 2-3 years away, needs traction first |
| Path 4 — Raise funding | Angel/pre-seed for faster build | After 2-3 paying clients |
| Path 5 — Acquisition | Build to sell to Salesforce/HubSpot | Long game, keep in mind |
| Path 0 — Open source | Free/community-led | Do not do this |

**Recommended sequence:**
1. Prove value through discovery + consultancy deployments
2. Find 2nd paying client
3. Register company, charge properly
4. Decide exit/scale path

---

## FULL DISCUSSION LOG

### Session 1 — 2026-06-06

**Started with:** Saral uploaded MAILCRM_MASTER.md and asked to discuss commercialization — money, investors, pitching to CRM companies, company registration, competition, free vs paid, and more.

**Key reframes in this session:**

1. **Manpower companies in upstream O&G = wrong target.** Saral clarified this explicitly. MailCRM should be positioned for other business flows and processes within Oil & Gas — OFS companies and operators are the target, not manpower consultancies.

2. **Mid-tier OFS is the entry point.** Tier-1 giants (SLB, BH, Halliburton) likely have systems already and have 18-month procurement cycles. Mid-tier (Petrofac, Kentech, Sapura, Enpro etc.) have the pain, no proper system, and can decide fast.

3. **Knowledge gap is the real problem right now.** Saral confirmed:
   - No firsthand knowledge of mid-tier OFS BD workflows (was a field guy at Halliburton/MI Swaco)
   - Zero contacts at mid-tier OFS currently
   - Doesn't know the specific broken moment in their workflow yet
   - Therefore: discovery conversations are the entire next phase, not more building

4. **MailCRM build continues in parallel** via Claude Code sessions (MAILCRM_MASTER.md tracks that separately).

5. **LinkedIn strategy:** Outreach before posting. 10 cold/warm DMs to BD managers at mid-tier OFS to start discovery conversations. Post comes later when there's a story to tell.

**Competitive landscape discussed:**
- Generic staffing CRMs: no O&G domain knowledge
- Salesforce: enterprise-only, wrong fit for mid-tier
- Riger CRM: closest but focused on OFS sales, not email automation
- AIEmailParser.com: general purpose, no domain logic
- **Conclusion: the specific gap (email-to-CRM automation for OFS commercial teams, MENA-focused, zero manual entry) is real and unserved**

**Commercial decisions made this session:**
- No investors yet
- No company registration yet (wait for second paying party)
- Don't give it away free
- Consultancy/service model is the right first move
- Discovery before everything else

**Next deliverables agreed:**
- LinkedIn outreach message (Claude to draft, multiple versions)
- One-page problem statement
- List of 20 target companies
- 1 post/week content rhythm on LinkedIn

---

## HOW TO USE THIS FILE

1. Save as `MAILCRM_COMMERCIAL_STRATEGY.md`
2. When starting a new commercial strategy chat with Claude, paste this file and say: **"Continue commercial strategy session for MailCRM"**
3. Claude will read, orient, and continue from exactly here
4. Type `exit` at end of any session to get an updated version of this file
5. Replace the previous version with the new one — this is always the single source of truth
