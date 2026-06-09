# MailCRM — Commercial Strategy Master File
> Separate from MAILCRM_MASTER.md (technical build log)
> This file = business strategy, market positioning, commercialization discussion only
> Last updated: 2026-06-09 | Session 5

---

## CURRENT STRATEGIC DIRECTION

MailCRM is an AI system that sits on top of any team's email, reads inbound business emails, extracts structured data automatically, and gives leadership a live pipeline — without anyone manually entering anything.

The pilot was built for an upstream oil & gas manpower consultancy (GET Global). That specific use case (manpower supply BD tracking) is NOT the target market. The engine is domain-agnostic and will be deployed for other business flows and processes.

**Target industry: Oil & Gas — OFS and Operators**
**Target customer: Mid-tier OFS companies operating in MENA**
**Current phase: Pre-discovery — outreach not yet started, zero conversations done**

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
| 8 | Set up Peerlist profile | India builder community visibility, no product needed | This week |
| 9 | Set up Indie Hackers profile — post "building in public" entry | Solo founder credibility, early signal | This week |
| 10 | List on Show Me Best AI | AI product directory, free discoverability | When product is demo-ready |
| 11 | List on Beta List | Early sign-up capture | When landing page is live |
| 12 | Launch on Product Hunt | Full product launch | When product is polished and demo-ready |
| 13 | Post on Hacker News "What are you building" thread | Technical community visibility | When ready |
| 14 | List on Launching Next | Press and visibility | When ready |
| 15 | List on DevHunt | Dev tool audience — lower priority for MailCRM | Optional |
| 16 | List on Product Hunt Canyon | Curated directory | When ready |
| 17 | List on Startup Base | Startup database visibility | When ready |
| 18 | Rename chat to "CRM Commercial Strategy" in sidebar after starting each session | Navigation hygiene | Each session |

---

## KEY DECISIONS MADE

| Decision | Rationale |
|---|---|
| NOT targeting manpower companies in upstream O&G | Too narrow, better niches exist within the same industry |
| Staying within Oil & Gas — OFS and Operators | Saral has 10 years domain context — this is the real moat, not the tech |
| Starting with mid-tier OFS, not Tier-1 giants | Tier-1 has systems, long procurement cycles; mid-tier has the gap and can decide fast |
| No investors yet | Stack costs near-zero; bootstrap until 2-3 paying clients, then revisit |
| No company registration yet | Do it when second party is ready to pay; Pvt Ltd is the right structure when ready |
| Not giving MailCRM away free | Free signals no value; founding customer discount yes, free no |
| Discovery before more building | Knowledge gap is bigger than product gap right now |
| LinkedIn outreach before LinkedIn post | Need conversations first, not inbound before product is ready to demo |
| MAILCRM_COMMERCIAL_STRATEGY.md kept separate from MAILCRM_MASTER.md | Technical log vs business strategy — two files, two concerns |
| No software patent | Too expensive, too slow, wrong stage — move fast instead; code is auto-copyrighted |
| Path 1 vs Path 2 (direct client vs CRM vendor licensing) | Unresolved — foundational decision to make next session |

---

## OPEN QUESTIONS (PARKED, NOT FORGOTTEN)

- What specific business flow inside mid-tier OFS is the right entry point? (needs discovery)
- Pricing model: setup fee + retainer vs per-seat SaaS? (decide after first client conversation — next agenda item)
- When to register a company? (trigger = second party willing to pay)
- When to raise funding? (trigger = 2-3 paying clients with MRR proof)
- Path 3 (license/OEM to CRM companies like Salesforce/HubSpot) — revisit in 2-3 years with traction
- ADIPEC November — worth attending independently for networking? (if attending via GET Global anyway, use it)
- What does the deployment story look like for a mid-tier OFS pilot? (30-day trial? sandbox?) — unresolved
- Does MailCRM handle Arabic/English bilingual emails? If not, is this a gap or a Phase 2 feature?
- Discovery conversations: still 0. No outreach sent. Single most important unblocked action.
- Path 1 (sell direct to end clients) vs Path 2 (license to CRM vendors as bolt-on feature) — unresolved, needs a session to work through properly
- Pricing — not yet worked out; next agenda item for Session 6

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

**MENA-specific market dynamics (Session 2 research):**
- Microsoft stack (Outlook, Teams, SharePoint) is near-universal in MENA OFS — strong deployment fit
- Arabic/English bilingual emails common — parser's handling of this is a potential differentiator or gap to address
- Saudi Aramco heavily Ariba-driven (portal, not email) — reduces MailCRM fit for Saudi operator procurement
- ADNOC, KOC, TotalEnergies remain email-heavy — better fit for operator flows in UAE/Kuwait/Iraq

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

## COST MODEL

### Stage 0 — Today (pre-client)
| Item | Cost |
|---|---|
| Groq (LLM) | Free tier |
| Supabase (DB) | Free tier |
| Render (backend) | Free tier |
| Vercel (dashboard) | Free tier |
| GitHub | Free |
| Microsoft Graph API | Free (M365 included) |
| **Monthly total** | **~₹0** |

### Stage 1 — First client
| Item | Cost |
|---|---|
| Groq paid tier or OpenAI API | $20–$100/mo |
| Supabase Pro | $25/mo |
| Render paid (no cold starts) | $7–$25/mo |
| Domain + hosting | ~$5/mo |
| **Monthly recurring** | **~$57–$155/mo** |
| Company registration (Pvt Ltd) — one-time | ₹10,000–15,000 |

> First client's setup fee should cover one-time registration cost. Monthly recurring is easily covered by first paying client.

### Stage 2 — 3–5 clients
| Item | Cost |
|---|---|
| LLM API (scaled usage) | $100–$400/mo |
| Supabase Pro (per project or shared) | $25–$75/mo |
| Render / cloud infra | $50–$100/mo |
| UptimeRobot / monitoring | Free tier |
| Azure OpenAI (in-tenant deployments) | **Client pays — not you** |
| SharePoint / M365 hosting | **Client's tenant — not you** |
| **Monthly recurring** | **~$175–$575/mo** |

> **Key principle:** Push clients toward in-tenant deployment as early as possible. Client bears Azure/M365 costs, your infrastructure bill stays low, and switching cost goes up significantly once it's inside their Azure tenant.

---

## OBJECTIONS & RISKS

### "We'll build it internally"
Most common enterprise deflection. IT will always say yes when asked if they can build it. The real question is whether they'll prioritise it — they won't. Use the argument explicitly: *"Your IT team can absolutely build this. The question is when, and at what opportunity cost."*

### "We already have a CRM"
Mid-tier OFS companies often have Salesforce or Dynamics that nobody uses properly. Data is stale, adoption is broken. MailCRM doesn't compete with the CRM — it feeds it. Position as a layer that makes their existing CRM investment actually work.

### "Who else are you deployed with?" (Reference client problem)
First client will ask this and you'll have nobody to name. Fix: offer a heavily discounted or free pilot explicitly in exchange for a written case study and reference call rights. That reference is worth more than the first fee.

### Single-founder dependency risk
Procurement or legal teams may ask: what happens if you disappear? Options to address: escrow of code, documented handover plan, or framing GET Global as anchor client proving continuity.

### Data privacy objection (especially MENA)
Saudi, UAE, Kuwait companies increasingly sensitive about commercial data location. One-sentence answer: *"Your emails never leave your own Microsoft environment — we deploy inside your Azure tenant, not ours."* In-tenant model is the answer — be ready to say it clearly to a non-technical BD manager.

### You are the product right now
Clients are buying you — your domain knowledge, responsiveness, understanding of their world. Strength (trust, credibility) and risk (not scalable). In BD manager conversations: lean into practitioner angle. In CTO/IT conversations: lean into architecture.

### Pricing hesitation
The moment you hesitate on price, they'll push. Decide your number before the first call and don't apologise for it.

### IP / competitive copying risk
Tech stack is standard — a competent dev team could build a rough version in weeks if shown too much. Mitigations:
- Show outcomes only in early conversations, not code or architecture
- Demo on anonymised data only
- Move fast — get a signed MOU before deep technical disclosure
- Frame as managed service, not a product they own
- Don't publish full technical approach in slides or LinkedIn before first paying client
- Real moat is iteration history, domain logic, and ongoing improvement — not the stack itself

### "Can you integrate with our existing system?"
They will ask this. Honest answer: *"Current version works standalone or feeds into Excel/SharePoint. Custom integrations are scoped separately."* Don't promise integrations you haven't built.

### Talking publicly at events
Once presenting at ADIPEC/GITEX etc., competitors will find you. Fine and inevitable — but don't reveal architecture before first paying client. Talk about problem and outcome only.

---

## LAUNCH PLATFORMS (ALL OPTIONS)

| Platform | Relevance | When |
|---|---|---|
| Peerlist | High — explicitly for India builders, no product needed | This week — set up profile now |
| Indie Hackers | High — solo founder / bootstrapper, "building in public" post | This week — no product needed |
| Show Me Best AI | Medium — AI product directory, free discoverability | When demo-ready |
| Beta List | Medium — pre-launch sign-up capture | When landing page is live |
| Product Hunt | High — main SaaS launch platform | When product is polished, can mobilise upvotes |
| Hacker News | Medium — technical audience, "what are you building" thread | When ready, wrong crowd for O&G validation |
| Launching Next | Low-medium — press and visibility | When ready |
| DevHunt | Low — dev tool audience, not ideal for MailCRM | Optional |
| Product Hunt Canyon | Low-medium — curated directory listing | When ready |
| Startup Base | Low — startup database visibility | When ready |

> Note: A simple landing page (problem statement + "coming soon" + email capture) is the entry ticket for Beta List and makes Indie Hackers / Peerlist posts look credible. Build this before the product is fully demo-ready.

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

### Session 2 — 2026-06-06

**Started with:** Continued from Session 1. Focus shifted to MENA market dynamics and discovery conversation framework.

**Key content covered:**

1. **MENA OFS market research:** Microsoft stack (Outlook/Teams/SharePoint) is near-universal — strong deployment advantage. Arabic/English bilingual emails are common in RFQs — worth knowing if parser handles this. Saudi Aramco is Ariba-dominant (portal-based, not email) which reduces MailCRM fit for Saudi operator procurement. ADNOC, KOC, TotalEnergies are email-heavy — better fit.

2. **Discovery question framework developed.** Questions should be hypothesis validation, not open-ended fishing. Peer-level tone — practitioner checking assumptions, not startup founder pitching. Key questions:
   - "My understanding is most BD tracking at your level is still Excel and email — is that accurate?"
   - "When leadership asks for a pipeline update, how long does it take to produce one?"
   - "Have you tried CRM before? What happened to it?"
   - "When a BD manager leaves, how do you recover their client context?"

3. **One-pager: too soon.** Decided not to write the one-page problem statement yet. Reasoning: write it after 3-5 discovery conversations using the prospect's own language, not ours. Pre-discovery one-pager sounds like a product brochure. Post-discovery one-pager has specifics that resonate.

4. **Demo/pilot problem raised but unresolved.** When someone says "show me" — what do you show? Can't use live client email. Sandbox? Anonymised GET Global data? Not yet answered.

5. **Networking events noted:** ADIPEC, OSEA, GITEX Energy, Gastech — don't need to exhibit, just be in the room. If attending via GET Global already, second reason to be there.

6. **LinkedIn: listen before you post.** Follow BD managers and commercial directors at mid-tier OFS first. Learn their language from what they share and comment on. Post comes after you have a story.

**Status at end of session:** LinkedIn outreach message not drafted yet. No discovery conversations started. All actions still pending.

### Session 3 — 2026-06-07

**Started with:** Saral uploaded the strategy file and confirmed it was only Session 1. Requested to continue discussion. Session was very brief — Saral confirmed zero discovery conversations have happened to date, then typed `exit`.

**Key facts established:**
- Discovery conversations: 0 done. No outreach sent yet.
- File was not updated after Session 2 — Sessions 2 and 3 captured together in this update.

**Status:** All Session 1 and 2 actions remain pending. The single most important unblocked next step is drafting and sending the LinkedIn outreach message to start discovery conversations.

### Session 4 — 2026-06-07

**Started with:** File was behind by one full session (Session 4 content was missing) — not captured because Groq update script wasn't run at end of that session.

**Key content covered:**
- Clarified the bat/py script purpose: automates end-of-session .md file updates using Groq free tier (Llama 3.3) — Groq used instead of Claude API because it's free and the task is mechanical document editing
- Full workflow confirmed: Claude chat → type exit → copy session notes → run update_strategy.bat → paste notes → type END → Groq updates .md with backup saved
- Clarified that pasting the .md file at the start of each new commercial strategy session is how Claude gets context — works as primary method, and Claude can also search past conversations as fallback
- Exit notes going forward must include session date and time (IST) as the last line
- No new strategic decisions made this session — housekeeping and workflow alignment only
- Discovery conversations: still 0. No outreach sent. This remains the single most important unblocked action.
- Session date/time: 2026-06-07, approximately 19:15 IST

### Session 5 — 2026-06-09

**Started with:** Saral uploaded strategy file. Quick housekeeping note: chat should be renamed to "CRM Commercial Strategy" in sidebar at start of each session (Claude cannot do this automatically).

**Voice session (June 8) notes incorporated:**
- Path 1 vs Path 2 question raised: license to CRM vendors (B2B2B) vs sell directly to end clients (B2B). Foundational decision, not yet made — added to open questions.
- For CRM vendor route, a credible proof point suffices over a full paid pilot — demo using GET Global anonymised data or realistic sample emails (Baker Hughes extraction flagged as good showcase).
- GITEX October not confirmed as hard dependency for discovery conversations — correction noted.

**Key content covered this session:**

1. **Launch platforms:** Analysed 10 platforms from a YouTube short (Builders Central). All 10 documented in Launch Platforms section with relevance ratings and timing. Immediate actions: Peerlist and Indie Hackers (no product needed). Show Me Best AI, Beta List, Product Hunt when demo-ready. Landing page identified as entry ticket for multiple platforms.

2. **IP / patents:** Software patents not recommended at this stage — expensive ($10-20k+), slow (2-4 years), hard to enforce without deep pockets. Real protection comes from: trade secrets (keep architecture private), auto-copyright on code, first-mover advantage, domain expertise, and customer stickiness via in-tenant deployment. Decision: no patent, move fast instead.

3. **Cost model built out:** Three stages (pre-client / first client / 3-5 clients) with line-item costs. Key insight: in-tenant deployment model is a significant cost shield — Azure/M365 costs sit with the client, not Saral. Full model documented in Cost Model section.

4. **Objections & risks framework:** Comprehensive list of likely objections and how to handle them — "we'll build it internally", "we already have CRM", reference client problem, single-founder dependency, data privacy (MENA), pricing hesitation, IP copying risk, integration questions, and event/public disclosure risk. All documented in Objections & Risks section.

**Status at end of session:**
- Discovery conversations: still 0. No outreach sent. Remains single most important unblocked action.
- Pricing model: not yet worked out — first item for Session 6.
- Path 1 vs Path 2: not yet resolved — second item for Session 6.
- Session date/time: 2026-06-09 IST

---

## HOW TO USE THIS FILE

1. Save as `MAILCRM_COMMERCIAL_STRATEGY.md`
2. When starting a new commercial strategy chat with Claude, paste this file and say: **"Continue commercial strategy session for MailCRM"**
3. Claude will read, orient, and continue from exactly here
4. Type `exit` at end of any session to get an updated version of this file
5. Replace the previous version with the new one — this is always the single source of truth
6. After starting the chat, rename it to **"CRM Commercial Strategy"** in the sidebar (hover over chat name → rename)

---

Today's date: 2026-06-09
Session date/time: 2026-06-09 IST