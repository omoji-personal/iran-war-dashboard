export const meta = {
  name: 'iwd-audit-update',
  description: 'Iran War Dashboard: real-world intelligence sweep (May 15→Jun 15 2026) + repo audit, all cited, to drive a full data refresh',
  phases: [
    { title: 'Intel sweep', detail: '7 multi-angle cited intelligence agents (diplomacy/kinetic/regime/markets/US-politics/sanctions-commodity/prediction-markets) + 1 repo audit' },
    { title: 'Verify', detail: 'adversarial verification of the highest-stakes claims (the June 14 deal, market levels, Khamenei status, resolved questions)' },
  ],
}

// ============================================================================
// Shared context handed to every intel agent
// ============================================================================
const CONTEXT = `
CONTEXT — you are gathering real-world intelligence to update the "Iran War Dashboard",
a cited probabilistic-forecasting site about the 2026 Iran-US conflict.

GROUND TRUTH RULES:
- Today is 2026-06-15. The current month is June 2026. These events are REAL and POST-DATE
  your training cutoff — you MUST use WebSearch (and WebFetch on primary sources) to find facts.
  Do NOT rely on memory for anything after Jan 2026.
- The war's Day 1 (D1) = 2026-02-28 (US+Israel strikes on Iran; Iran then closed Strait of Hormuz).
- The dashboard's data is FROZEN at 2026-05-12 to 2026-05-15 (its last update). Its worldview then:
  "ceasefire on life support", deal "unlikely", Hormuz closed since May 4, rial ~1.842M, Brent ~$105,
  US gas ~$4.52, Trump-Xi summit framed as UPCOMING (May 14-15).
- KNOWN BIG SHIFT (confirm + expand): around 2026-06-14 the US and Iran reached an agreement —
  Trump lifting the naval blockade, Hormuz reopening, an MOU to be signed ~June 19, aiming to end
  the conflict within ~60 days. Find the full, cited picture of HOW we got from May 15 to this deal.

YOUR JOB: find what ACTUALLY happened between 2026-05-15 and 2026-06-15, with REAL sources.
- Run 4-8 WebSearch queries. WebFetch 1-3 primary/authoritative sources to confirm key claims.
- EVERY finding must have a real, non-invented URL. Never fabricate a URL or a fact.
- Date-stamp findings (ISO). Prefer Tier-1 / primary sources; note when a source is partisan.
- public_safe=false for anything touching the operator's family businesses (Iranfarhang, Kipa,
  AMAG, Kemco, Behrah, Mozhgan) or the "Berman Amendment / informational-materials" personal angle.
  General public regulatory/market facts are public_safe=true.
- For each relevant question, give a "question_impact": did it move up/down, resolve YES, resolve NO,
  or stay flat — with a suggested probability (0-1) and an 80% credible interval, plus a one-line
  rationale citing a finding. Be calibrated; use ICD-203 discipline (don't overclaim certainty).
`

const INTEL_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  required: ['track', 'as_of_utc', 'summary', 'findings', 'question_impacts'],
  properties: {
    track: { type: 'string' },
    as_of_utc: { type: 'string' },
    summary: { type: 'string', description: '3-5 sentence narrative of what changed in this track May15->Jun15' },
    findings: {
      type: 'array',
      items: {
        type: 'object',
        additionalProperties: false,
        required: ['claim', 'date', 'source_name', 'url', 'public_safe'],
        properties: {
          claim: { type: 'string' },
          date: { type: 'string', description: 'ISO date of the event' },
          source_name: { type: 'string' },
          url: { type: 'string' },
          public_safe: { type: 'boolean' },
          confidence: { type: 'number' },
        },
      },
    },
    market_data: {
      type: 'array',
      description: 'Optional: current quantitative levels (rial, Brent, gas, oil exports, vessel counts, LDPE)',
      items: {
        type: 'object',
        additionalProperties: false,
        required: ['metric', 'value', 'as_of', 'source_name', 'url'],
        properties: {
          metric: { type: 'string' },
          value: { type: 'string' },
          as_of: { type: 'string' },
          source_name: { type: 'string' },
          url: { type: 'string' },
        },
      },
    },
    prediction_markets: {
      type: 'array',
      description: 'Optional: current prediction-market odds relevant to portfolio questions',
      items: {
        type: 'object',
        additionalProperties: false,
        required: ['platform', 'question', 'probability', 'url'],
        properties: {
          platform: { type: 'string' },
          question: { type: 'string' },
          probability: { type: 'number' },
          url: { type: 'string' },
        },
      },
    },
    question_impacts: {
      type: 'array',
      items: {
        type: 'object',
        additionalProperties: false,
        required: ['qid', 'direction', 'rationale'],
        properties: {
          qid: { type: 'string' },
          direction: { type: 'string', enum: ['up', 'down', 'resolved_yes', 'resolved_no', 'flat', 'unknown'] },
          suggested_probability: { type: ['number', 'null'] },
          suggested_ci_low: { type: ['number', 'null'] },
          suggested_ci_high: { type: ['number', 'null'] },
          rationale: { type: 'string' },
        },
      },
    },
  },
}

const TRACKS = [
  {
    key: 'A-diplomacy',
    label: 'intel:diplomacy-deal',
    prompt: `${CONTEXT}

TRACK A — DIPLOMACY & THE DEAL. Find the full cited story of the diplomatic endgame.
Search for: the June 2026 US-Iran agreement / memorandum of understanding; signing date; mediators
(Oman/Qatar/Pakistan/China); the Trump-Xi summit outcome (May 14-15); what the deal says about
sanctions relief, nuclear monitoring/enrichment, Hormuz reopening, naval blockade lifting, prisoner/
hostage terms, the 60-day formal-end timeline; Khamenei's public posture toward negotiating (any
"heroic flexibility"-type framing); Araghchi's diplomacy (New Delhi and after).

Map impacts to these questions (current dashboard probability in parens):
- A1: Iran-US framework agreement signed by 2026-09-30 (was 20%, "unlikely")
- A2: Hormuz commercial transit >50% pre-war (>67 vessels/day 7d MA) by 2026-12-31 (was 22%)
- A3: US announces formal naval reflagging of GCC tankers by 2026-12-31 (was 10%)
- A4: Iran 14-point counter-proposal becomes basis for substantive talks (joint working groups) by 2026-08-31 (was 25%)
- A5: Khamenei publicly endorses negotiations using 'heroic flexibility' framing by 2026-12-31 (was 10%)
For A1 especially: is it already effectively resolved YES, or imminently? Be precise about the deal's status (MOU vs signed vs framework).`,
  },
  {
    key: 'B-kinetic',
    label: 'intel:kinetic-military',
    prompt: `${CONTEXT}

TRACK B — MILITARY / KINETIC. Reconstruct the kinetic timeline 2026-05-15 → 2026-06-15.
Search for: US strikes on Iranian territory; Israeli strikes on Iran (esp. nuclear sites Natanz/
Fordow/Arak); Iranian strikes on US bases/ships/embassies; the naval blockade and tanker interdictions;
IRGC seizures of foreign-flagged commercial vessels; Hezbollah/Lebanon-Israel cross-border attacks and
the Lebanon-Israel talks; casualty figures; any ceasefire declarations or collapses before the June deal.

Map impacts to:
- B1: US conducts kinetic strike on Iranian sovereign territory by 2026-12-31 (was 22%). NOTE: if US/Israel struck Iran during this conflict, is B1 already resolved YES? Check the war's actual strike record carefully.
- B2: Iran conducts kinetic strike on US-flagged/US-base target by 2026-12-31 (was 75%, flagged near-resolution — Iran attacked 3 US destroyers May 7). Is this resolved YES?
- B3: Israel strikes Iranian nuclear infrastructure by 2026-12-31 (was 15%). Resolved?
- B4: Hezbollah-attributed attack reaches Israeli population center >25km north of border by 2026-09-30 (was 35%)
- B5: IRGC seizes a 3rd foreign-flagged commercial vessel by 2026-09-30 (was 58%)
Be explicit about which of B1/B2/B3 may ALREADY be resolved YES by events in the war, vs still open.`,
  },
  {
    key: 'C-regime',
    label: 'intel:regime-internal',
    prompt: `${CONTEXT}

TRACK C — IRAN REGIME / INTERNAL. Find cited facts on Iran's internal situation May15→Jun15.
Search for: Khamenei's health and public appearances (was reportedly recovering from severe burns,
unseen publicly since Feb 28); any death/removal/incapacity reports; Mojtaba Khamenei succession moves
and Assembly of Experts statements; protest activity (ACLED/Iran International) — scale, cities, duration;
Tehran Grand Bazaar strikes/closures; the internet blackout status (was ~74+ days); economic-grievance signals.

Map impacts to:
- C1: Khamenei dies or is publicly removed by 2026-12-31 (was 8%, humility-flagged)
- C2: Iran sustained protest wave >14d, >5 cities, ACLED-coded, by 2026-12-31 (was 46%)
- C3: Mojtaba Khamenei publicly designated heir-apparent by Assembly of Experts by 2026-12-31 (was 6%, humility-flagged)
- C4: Sustained bazaari shutdown >3d Tehran Grand Bazaar by 2026-12-31 (was 30%)
Flag clearly if Khamenei has reappeared publicly / is confirmed alive, or if there is credible succession news.`,
  },
  {
    key: 'D-markets',
    label: 'intel:markets-economy',
    prompt: `${CONTEXT}

TRACK D — MARKETS & ECONOMY (quantitative; fill market_data with real current numbers + sources).
Find the CURRENT (mid-June 2026) levels and the May15→Jun15 trajectory for:
- USD/IRR free-market rate (bonbast.com, alanchand.com, tgju.org). Was 1.842M on May 12. Where is it now? Did it cross 2,000,000?
- Brent crude front-month (and WTI). Was ~$105 on May 12; reportedly dropping ~4% on the deal news. Current?
- US AAA national gas-price average. Was ~$4.52 on May 12. Did it sustain >$4.50 for 7+ days (resolves D3 YES)? Current level + trajectory.
- Iran seaborne crude exports (Kpler-style estimates if publicly reported). Below 0.5M bpd at any point?
- Strait of Hormuz commercial vessel traffic (counts / % of pre-war ~135/day). Reopening status post-deal.
- LDPE CFR Far East Asia polymer price (ChemOrbis/Polymerupdate public snippets) vs the $1,390-1,500/MT April anchor — any war-premium compression?

Map impacts to: D1 (bonbast >2M by 12/31, was 68%), D2 (oil exports <0.5M bpd by 12/31, was 52%),
D3 (US gas >$4.50 sustained 7d by 9/30, was 78% — likely already RESOLVED YES; confirm with dated AAA data),
D4 (Brent >$130 by 12/31, was 20%), and note read-through to A2/F7 (Hormuz), F8 (ICE FX >2M), F12 (LDPE).
Put every number in market_data with an as_of date and source URL.`,
  },
  {
    key: 'E-us-politics',
    label: 'intel:us-politics',
    prompt: `${CONTEXT}

TRACK E — US DOMESTIC POLITICS. Find cited facts May15→Jun15 on:
- Any replacement/resignation of the US Secretary of Defense, National Security Advisor, or Secretary of State.
- 2026 midterm dynamics: generic-ballot polling, House/Senate control forecasts (538/Cook/Polymarket), the
  political effect of gas prices and the war/deal on Trump's standing.

Map impacts to:
- E1: Trump replaces SecDef, NSA, or SecState by 2026-09-30 (was 30%)
- E2: Republican loses control of either chamber in Nov 2026 midterms (was 60%)
Note that the June deal may cut both gas prices and war-fatigue — reason about the net effect on E2.`,
  },
  {
    key: 'F-sanctions',
    label: 'intel:sanctions-commodity',
    prompt: `${CONTEXT}

TRACK F — SANCTIONS & REGULATORY BACKDROP (PUBLIC SOURCES ONLY; do NOT research private individuals or
the operator's specific companies — only the public regulatory/market environment that those questions sit in).
Search for:
- OFAC "Recent Actions" May15→Jun15: any Iran-related designations, any UAE-based (Dubai FZCO/FZE)
  chemical/petroleum entity designations, any new Iran sanctions tranches (incl. the UK May 15 package + US follow-on).
- Any OFAC FAQ/Federal Register/AAUP/AUPresses signal touching the Berman Amendment / informational-materials
  exemption (31 CFR 560.315) — narrowing or reaffirmation.
- Iran MIMT (Ministry of Industry) import policy / bakhshname restricting raw-material imports to manufacturer-end-users.
- General "diaspora bank de-risking / French-correspondent-bank Iran compliance" climate during the conflict (public reporting only).

Map impacts to (mark these question_impacts public_safe=false):
- F2 (correspondent-bank Iran payment freeze risk, was 35%), F5 (OFAC Berman narrowing by 12/31, was 10%, humility-flagged),
- F10 (Iran MIMT import bakhshname by 12/31, was 15%), F11 (OFAC designates a Dubai chemical FZCO/FZE by 12/31, was 30%),
  plus read-through to F1/F4 (general sanctions/cargo climate) and F12 (covered in Track D).
Keep findings to PUBLIC regulatory/market facts; do not name or investigate the operator's businesses.`,
  },
  {
    key: 'G-prediction-markets',
    label: 'intel:prediction-markets',
    prompt: `${CONTEXT}

TRACK G — PREDICTION MARKETS (calibration cross-check). Find current odds (mid-June 2026) on
Polymarket, Metaculus, Manifold, Kalshi for questions analogous to our portfolio:
- Iran-US deal / nuclear agreement in 2026 (cross-check A1)
- Strait of Hormuz reopening / shipping normalization (cross-check A2/F7)
- US or Israel military strike on Iran in 2026 (cross-check B1/B3) — note many may now be backward-looking/resolved
- Khamenei out / regime change in 2026 (cross-check C1)
- 2026 US midterms: which party controls House/Senate (cross-check E2)
- Brent/oil price levels (cross-check D4)
Return each as a prediction_markets entry (platform, question, probability, url). In question_impacts, note where
the market diverges from our last dashboard probability and which way.`,
  },
]

const AUDIT_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  required: ['test_status', 'findings'],
  properties: {
    test_status: { type: 'string' },
    findings: {
      type: 'array',
      items: {
        type: 'object',
        additionalProperties: false,
        required: ['severity', 'area', 'title', 'detail', 'recommendation'],
        properties: {
          severity: { type: 'string', enum: ['P0', 'P1', 'P2', 'P3'] },
          area: { type: 'string' },
          title: { type: 'string' },
          detail: { type: 'string' },
          file: { type: 'string' },
          recommendation: { type: 'string' },
        },
      },
    },
  },
}

const AUDIT_PROMPT = `You are auditing a Python+static-HTML repo at the current working directory: the "Iran War Dashboard".
It renders a probabilistic-forecasting site from portfolio.yaml via scripts/render.py into index.html / fa.html /
public.html / public.fa.html, with a stripped public build (scripts/build-public.py -> public-dist/). Tests in tests/.

Today is 2026-06-15. The data (portfolio.yaml, agent/briefing-2026-05-15.json, committed HTML) is frozen at
2026-05-12..05-15. The daily refresh cron was just disabled. Do a thorough engineering + content-integrity audit.

Investigate and report findings (use Read/Grep/Glob/Bash; run pytest):
1. STALENESS & CORRECTNESS: Where are dates/"Day N"/"next 14 days" windows hardcoded vs computed? render.py computes
   war_day from D1=2026-02-28 and "today" from datetime.now — so re-rendering today shows ~Day 107 and the briefing
   freshness banner trips (briefing is 2026-05-15, >36h old). Confirm this. Is CLAUDE.md stale (it says "Last data: D46
   eve / Apr 14")? List every place the May-12 worldview is baked into prose (base_case, economic_war_frame) that would
   read as wrong now that a deal was reached ~June 14.
2. RESOLUTION LOGIC: Does anything auto-resolve questions at deadline or on threshold? Several questions are at/over
   resolution (B2, D3) or have near-term deadlines (F7 = 2026-06-30). Is there machinery for marking a question resolved,
   or is it purely manual via portfolio.yaml? Note the gap.
3. PUBLIC/SENSITIVE STRIPPING: Verify the public build correctly strips family-business (F-class / public_safe=false)
   content from public.html/public.fa.html/public-dist. Grep the public outputs for leak terms: Iranfarhang, Kipa, AMAG,
   Kemco, Behrah, Mozhgan, Berman. Report any leak as P0.
4. PIPELINE INTEGRITY: Do scripts/fetch_news.py, fetch_polymarket.py, fetch_manifold.py, fetch_metaculus.py,
   append_history.py, refresh_memory.py, render.py run without import/obvious runtime errors? (Try --help or a dry import.)
   Is the /legacy chart still broken (legacy/war-data.json a ~12-byte placeholder)? Any other broken/dead files,
   stale .bak files, gitignored-but-committed artifacts?
5. TEST COVERAGE: Run pytest (expect 85 passing). What's NOT covered that matters for a data refresh — e.g. resolution
   rendering, deadline-passed handling, the public-strip leak test, briefing schema validation?
6. RENDER ROBUSTNESS: If portfolio.yaml gains a "resolved"/"status" field or a question's deadline passes, does render.py
   handle it gracefully or break? Skim render_question_card / render_question_board for assumptions.

Return test_status (e.g. "85 passed") and a findings list with severity P0-P3, the file, and a concrete recommendation.
Focus on what blocks or endangers a correct full data refresh today. Do NOT edit any files — audit only.`

// ============================================================================
// PHASE 1 — Intel sweep (7 cited intel agents) + repo audit, all concurrent
// ============================================================================
phase('Intel sweep')
log(`Launching ${TRACKS.length} cited intel agents + 1 repo audit`)

const phase1 = await parallel([
  ...TRACKS.map((t) => () =>
    agent(t.prompt, { label: t.label, phase: 'Intel sweep', schema: INTEL_SCHEMA }).then((r) => ({ kind: 'intel', track: t.key, data: r })),
  ),
  () => agent(AUDIT_PROMPT, { label: 'repo-audit', phase: 'Intel sweep', schema: AUDIT_SCHEMA }).then((r) => ({ kind: 'audit', data: r })),
])

const intel = phase1.filter((x) => x && x.kind === 'intel' && x.data).map((x) => x.data)
const audit = phase1.filter((x) => x && x.kind === 'audit' && x.data).map((x) => x.data)

// ============================================================================
// PHASE 2 — Adversarial verification of the highest-stakes claims
// ============================================================================
phase('Verify')

const VERIFY_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  required: ['claim', 'verdict', 'evidence', 'confidence'],
  properties: {
    claim: { type: 'string' },
    verdict: { type: 'string', enum: ['confirmed', 'refuted', 'mixed', 'uncertain'] },
    corrected_value: { type: 'string', description: 'If the claim is wrong or imprecise, the corrected fact' },
    evidence: {
      type: 'array',
      items: {
        type: 'object',
        additionalProperties: false,
        required: ['source_name', 'url', 'note'],
        properties: {
          source_name: { type: 'string' },
          url: { type: 'string' },
          note: { type: 'string' },
        },
      },
    },
    confidence: { type: 'number' },
  },
}

const VERIFY_BASE = `Today is 2026-06-15; the current month is June 2026; these are REAL post-cutoff events — use WebSearch
and WebFetch primary sources, never memory. Be adversarial: actively try to find a source that REFUTES or corrects the
claim before confirming it. Cite real URLs only. Return verdict + corrected_value (if needed) + evidence.`

const CLAIMS = [
  `The June 14, 2026 US-Iran agreement: confirm the precise status and terms — is it a signed deal, an MOU, or a
   framework? Confirm the reported signing date (~June 19), the ~60-day formal-end timeline, the lifting of the US naval
   blockade, the reopening of the Strait of Hormuz, and any sanctions-relief / nuclear-monitoring components. Correct any
   imprecision. This determines whether dashboard question A1 (framework agreement by 2026-09-30) resolves YES.`,
  `Current market levels as of mid-June 2026: (a) USD/IRR free-market rate (bonbast/alanchand/tgju) — exact figure and
   whether it crossed 2,000,000; (b) Brent crude front-month price; (c) US AAA national average gas price and whether it
   sustained above $4.50 for 7+ consecutive days at any point since May. Give exact dated numbers with sources.`,
  `Iran internal: Is Ayatollah Khamenei confirmed alive and has he made any public appearance in June 2026? Any credible
   death/incapacity/removal or Mojtaba-succession designation? This bears on dashboard questions C1 and C3.`,
  `Resolution check: During the 2026 Iran war did (a) the US conduct a kinetic strike on Iranian sovereign territory, and
   (b) Iran conduct a kinetic strike on a US-flagged vessel or US base, and (c) Israel strike Iranian nuclear sites
   (Natanz/Fordow/Arak)? For each, state whether it is firmly established by ≥2 sources — these would resolve dashboard
   questions B1, B2, B3 YES respectively.`,
]

const verify = await parallel(
  CLAIMS.map((c, i) => () =>
    agent(`${VERIFY_BASE}\n\nCLAIM TO VERIFY:\n${c}`, { label: `verify:${i + 1}`, phase: 'Verify', schema: VERIFY_SCHEMA }),
  ),
)

return {
  generated_for: '2026-06-15 full audit+update',
  intel,
  audit,
  verify: verify.filter(Boolean),
}
