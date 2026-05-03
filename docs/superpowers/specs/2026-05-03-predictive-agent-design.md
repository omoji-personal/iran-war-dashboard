# Iran-US Conflict Predictive Agent — Design Spec

**Date:** 2026-05-03
**Status:** v8 (Round 7 applied; convergence declared — see §12)
**Origin:** Re-imagining of the existing dashboard from "active-war tracker" into a calibrated predictive *agent* running as a Claude Code cron job. Grounded in five parallel research streams and iteratively hardened by adversarial self-review.

**Changelog:**
- v1 → v2: F1-F12 (sourced LRs, signal gate, ref classes, source clustering, agent loop, two-view UX, ICD-203 narrative-only, dual baselines, portfolio criteria, MVP, adversarial-input filter, external review)
- v2 → v3: G1-G14 (daily+event cadence, eight logs, per-event LR retrospective, successor questions, 24h diff, useful-daily MVP, 3-tier autonomy, signal re-validation, controversies log, pace governance, stakeholder definitions)
- v3 → v4: H1 generative question selection · H2 two-tier reference classes · H3 SOTA-only-where-applicable · H4 per-tick agent budget · H5 8-question MVP · H6 agent-effectiveness leaderboard · H7 stakeholder-tagged questions · H8 published ICD-203 mapping · H9 progressive disclosure · H10 sources-shifted log · plus user clarification: agent = Claude Code cron session
- v4 → v5: I1 cardinal-vs-supporting split · I2 rolling-horizon regeneration · I3 agent-memory file · I4 cron prompt template specified · I5 Omid-personal deferred to user-confirm · I6 CI-aware diff suppression · I7 expiration-policy per question · I8 narrative span-grounded · I9-I14 operational details
- v5 → v6: J1 condense cron prompt to summary · J2 §10 file schemas · J3 cold-start = median ensemble · J4 ~$4K/yr budget · J5 MVP re-prioritized · J6 ICD-203 tails · J7-J15 operational
- v6 → v7: K1 branch cleanup · K2 phase-progressive cron prompt · K3 §11 migration plan · K4 rollback plan · K5-K10 operational
- v7 → v8: L1 mid-tick budget checkpoint · L2 optional operator notification channels · convergence declared (§12)
- v8 → v8.1 (post-impl polish 2026-05-03): resolved internal contradiction between §0 #5 (ICD-203 narrative-only) and §3.6 (ICD-203 always alongside) — DECIDED: ICD-203 label always alongside numeric probability. Narrative paragraphs use ICD-203 vocabulary as well. Document on the live page makes both the number and the label visible. The stricter "narrative-only" stance was over-corrective; readers benefit from the redundancy.
- Honest disclosure: this spec was written and adversarially refined by Claude in a single session. The "v8 converged after 7 rounds" descriptor is accurate to the iterative-refinement process used, but does not represent multi-author or multi-session review. External adversarial review is the planned 90-day milestone (§7).

---

## 0. Five cardinal commitments (the actual TL;DR)

1. **Brier-scored discrete events** with hard deadlines, resolution criteria, live scores against Polymarket/Metaculus/AR baseline. The model exists to be measured against reality.
2. **Agent = Claude Code session in cron** with hard per-tick + per-day budget caps. No standalone services. The cron prompt is published, version-controlled.
3. **Eight first-class committed-markdown logs** — change-history IS the product. Daily *What I think* opens with CI-aware 24h diff panel.
4. **Sourced everything** — every LR carries source class, every reference class has named members + base-rate calc, every signal admitted via 3-question gate. Unmarked subjective forbidden.
5. **Progressive disclosure single view** — every probability click-to-expand into evidence chain. No mode switch.

## 0.1 Supporting commitments

6. Discrete events as calibration backbone; rolling state derived; successor questions auto-added on resolution.
7. Generative question selection (decision-driven ∩ market-driven), not curated taste.
8. Three-tier agent autonomy (Tier A auto / B notify / C queue) within within-tick priority allocation.
9. Two-tier reference classes (strict narrative anchor + broad probability calc).
10. Late fusion ensemble (Bayesian + baseline + market + SOTA-where-applicable + expert), equal-weight regime until N≥10 resolutions.
11. External SOTA only where target matches.
12. Adversarial-input filter between extraction and update.
13. Per-event LR retrospective (14d-resolving miscalibrations flagged immediately).
14. Atomic W3C PROV-DM provenance.
15. Humility output state ("out of model scope") for outcome classes without model-class track record.
16. Signal re-validation quarterly + immediate on entity-state change.
17. Published ICD-203 mapping table (with <1% "vanishing" + >99% "near-certain" tail buckets).
18. Sources-shifted log tracks Polymarket/Metaculus/expert deltas independent of model.
19. Agent-effectiveness leaderboard — investigations scored.
20. **Rolling-horizon regeneration** — questions within 30d of deadline auto-generate successors with extended deadlines.
21. **Agent memory file** at `agent/memory.md` (committed) — compact ~500-line state distillation, updated each tick.
22. **Agent narrative span-grounded** — every narrative claim cites event-log entry / LR-table row / evidence span.
23. **CI-aware diff suppression** — 24h diff panel only headlines moves larger than the question's 80% credible-interval half-width.
24. **Minimal-attention mode** — operator absence >7d → agent auto-merges Tier A only, queues B/C, no Tier C decisions.
25. **Hot/cold log retention** — last 90d in-repo, older archived to git LFS or S3 (decision in Phase 5).
26. External 90-day adversarial review, then quarterly forever.
27. No alpha-trade output until 1-year Brier beats relevant benchmark for specific outcome class.

---

## 1. Question portfolio

### 1.1 Inclusion criteria + generative pipeline

A question enters portfolio iff:
- **Decision-relevant** to ≥1 named stakeholder class (registry below)
- **Resolvable** in ≤365 days against pre-stated public criterion
- **Benchmarkable** — market-traded OR documented alpha-lane
- **Sufficiently independent** — historical-analog pairwise correlation <0.5

**Generative pipeline** (Round-3 fix H1):
- (a) **Decision-driven**: enumerate open decisions per stakeholder class; generate questions whose resolution would move that decision
- (b) **Market-driven**: scrape Polymarket+Metaculus+Manifold Iran-tagged contracts; auto-import top-N by liquidity
- Intersection = portfolio. Rest archived as "considered-not-included" with reason.

### 1.2 Stakeholder classes (with named open decisions)

```yaml
us_foreign_policy_decisionmaker:
  open_decisions:
    - kinetic_strike_authorization (B1, B3)
    - sanctions_relief_offer (A1, A4)
    - mediator_engagement (A1, A4, A5)
    - naval_reflagging (A3)
    - personnel_changes (E1)
iran_regime_survival:
  open_decisions:
    - framework_acceptance (A1, A4, A5)
    - succession_signaling (C3)
    - protest_suppression_intensity (C2, C4)
    - oil_export_strategy (D2)
oil_energy_markets:
  open_decisions:
    - hormuz_transit_capacity (A2, B5)
    - global_supply_balance (D2, D4)
    - retail_pump_pricing (D3)
regional_security:
  open_decisions:
    - israel_strike_doctrine (B3)
    - hezbollah_retaliation (B4)
    - gcc_realignment_pace
omid_personal_economic_exposure: # Round-3 fix H7
  open_decisions:
    - iranfarhang_supply_chain_resilience (F1)
    - usd_irr_remittance_corridor (F2)
    - regional_business_travel_risk
```

### 1.3 The initial 20 questions (Omid-personal F1, F2 added Phase 1 after user confirmation)

**A. Diplomatic resolution (5)** — mostly unique-event
- A1. Iran-US framework agreement signed by 2026-09-30
- A2. Hormuz commercial transit returns to >50% pre-war by 2026-12-31
- A3. US announces formal naval reflagging of GCC-flagged tankers by 2026-12-31
- A4. Iran 14-point counter-proposal becomes basis for substantive talks by 2026-08-31
- A5. Khamenei publicly endorses negotiations using "heroic flexibility" framing by 2026-12-31

**B. Military escalation (5)** — mix
- B1. US conducts kinetic strike on Iranian sovereign territory by 2026-12-31
- B2. Iran conducts kinetic strike on US-flagged or US-base target by 2026-12-31
- B3. Israel strikes Iranian nuclear infrastructure by 2026-12-31
- B4. Hezbollah-attributed attack reaches Israeli population center >25km north of border by 2026-09-30
- B5. IRGC seizes a third foreign-flagged commercial vessel in Gulf/Hormuz by 2026-09-30

**C. Regime / leadership (4)** — C1, C3 humility-flagged
- C1. Khamenei dies or is publicly removed by 2026-12-31
- C2. Iran sustained protest wave (>14d, >5 cities, ACLED) by 2026-12-31
- C3. Mojtaba Khamenei publicly designated heir-apparent by 2026-12-31
- C4. Sustained bazaari shutdown (>3d Tehran Grand Bazaar) by 2026-12-31

**D. Economic / structural (4)** — recurring
- D1. USD/IRR bonbast > 2,000,000 by 2026-12-31
- D2. Iran oil exports < 0.5M bpd (Kpler 30d MA) by 2026-12-31
- D3. US gas national average crosses $4.50 sustained 7+d by 2026-09-30
- D4. Brent crosses $130 by 2026-12-31

**E. US side (2)**
- E1. Trump replaces SecDef, NSA, or SecState by 2026-09-30
- E2. Republican loses control of either chamber Nov 2026

**F. Omid-personal (added Phase 1 after user confirmation)**
- F1 (proposed). Iran sanctions extended in scope to affect publishing/cultural-import sector by 2026-12-31. *Baseline: reference class (1995, 2010, 2018 sanctions-scope expansions).*
- F2 (proposed). USD/IRR formal remittance corridor disruption (named bank suspension affecting Iran-diaspora remittances >7d) by 2026-12-31. *Baseline: AR + reference class.*
- *(User: confirm/edit/replace these before Phase 1 entry.)*

Each question carries: probability + 80% credible interval + ICD-203 label + baseline class + reference class (strict + broad) + last-update timestamp + Brier vs benchmark + stakeholder-class tags + "what moved this" link.

### 1.4 Successor-question generation

Each question declares successors triggered on resolution. On resolution: predeclared successors **revisited** (not mechanically executed — Round 3 fix folded H12) and added or modified per current situation. Detail in §3.4.

---

## 2. Signals — 3-question admission gate

A signal enters iff all three:
1. **Pearl-DAG single-arrow path** to a question's outcome via named decision-relevant intermediate state
2. **Documented lead time on ≥3 named past episodes** including ≥1 dog-that-didn't-bark
3. **Faster, cheaper, OR more granular than Polymarket** on the relevant question

Each carries **future-validation stamp**: "Once N≥10 resolved questions, must pass Granger / CMI / Hansen-SPA vs AR baseline."

**Quarterly re-validation** + **immediate re-validation on entity-state change**.

### 2.1 Tier-1 daily ingest

| Signal | Source | Update cadence | Stale-handling | Pearl-DAG path |
| --- | --- | --- | --- | --- |
| USD/IRR bonbast (7d, 30d roll) | bonbast.com | hourly during Tehran market hours | use most-recent if <24h, else flag stale | currency → bazaari capital flight → C2/C4 |
| Bahar-e Azadi gold premium | TGJU.org | hourly | same | bazaari hedging → regime confidence → C2/C4 |
| Iran oil exports bbl/d | Kpler+TankerTrackers+UANI | weekly (free-tier delay) | use most-recent; flag if >14d | export collapse → fiscal pressure → A1/D2 |
| Hormuz commercial transit | MarineTraffic/Spire AIS | real-time | same | direct A2 measure |
| ACLED Iran event count (Baluch/Kurd ×2) | ACLED Iran Crisis Live | daily 9am EST | use most-recent; flag if >48h | direct C2 measure |
| Polymarket Iran contracts | Gamma API | real-time | benchmark + alpha gap |
| Metaculus Iran questions | Metaculus API | hourly | benchmark + alpha gap |
| Mueller-Rauh ConflictForecast | conflictforecast.org | monthly | external SOTA, B-class only |
| GDELT GKG tone (NOT raw events) | BigQuery | 15-min | salience + tone only |

### 2.2 Tier-2 weekly narrative-context (does not vote on probability)

Khamenei + Mojtaba public-appearance count · SNSC/IRGC top-roster diff · Sepahnews+Nour News+Kayhan tone (Persian NLP) · Tehran housing transaction volume · Active-mosque count · US personnel changes (NSA/SecState/SecDef/CIA-D)

### 2.3 Tier-3 event-triggered

ADS-B Pakistan/Oman/Qatar to Tehran → A1/A4/A5 · ADS-B callsign blackout → B1-B3 + adversarial-input flag · Trump Truth Social cluster (≥3/48h) on Iran → E1/A1 · OFAC designation → A1/D2/F1 · IAEA quarterly or special board → A1/B3 · Iran/Israel direct strike → B1-B5 · Khamenei statement → A5/C1 · Bonbast >8%/wk slide → C2/C4/D1

### 2.4 Explicit rejections

Stratfor post-2015 · GAMAAN polling as primary signal · Raw Twitter/X sentiment · GDELT raw event counts · Named-expert directional opinions without scored claim · Hand-set magic-number coefficients · Any pre-registered LR or source-credibility weight not labeled with source class

---

## 3. The reasoning architecture

### 3.0 Cron architecture

The agent IS a Claude Code session running in this account's cron via RemoteTrigger:
- **Daily 06:00 ET** — morning brief tick (always)
- **Optional 17:00 ET** — evening update tick (when configured)
- **Event-triggered re-runs** via separate cron entry on threshold-passing signals (Phase 4+)

Each tick = one Claude session bounded by per-tick budget ($5 / 30 min / 50 tool calls). Session has access to: Bash, Read, Write, Edit, ToolSearch (deferred MCP), Polymarket/Metaculus scrapers (Python helpers in `scripts/`), provenance graph helpers, log writers. Writes to `proposed-signals` branch + auto-PR; human merge gate.

When budget exhausted: agent enters "deferred" state, writes investigation queue depth to next *What I think* update.

#### 3.0.1 Cron prompt template (summary)

Full prompt at `agent/cron-prompt.md` — single source of truth, version-controlled. Procedure summary (10 steps, full bodies in the prompt file):

1. **Read state** — agent/memory.md, event-log diff since last tick, sources-shifted diff, operator queue, portfolio.yaml
2. **Ingest new evidence** — run scripts/fetch_tier1, extract via ConfliBERT, dedup via MinHash, adversarial-filter, append to event log
3. **Prioritize investigations** — priority = uncertainty × decision-stakes × cheapness; top-K within budget; log decisions
4. **Update Bayesian posteriors** — apply sourced LRs × cluster_diversity_score, cap per-day movement ±0.5/question, run per-event retrospective
5. **Update ensemble** — recompute layers; cold-start uses median ensemble; performance-weighted log-odds + extremization k≈2.5 once N≥10 resolutions; surface layer-disagreement
6. **Check rolling horizons** — generate rolling-successor for questions within 30d of deadline; revisit predeclared successors on resolution
7. **Emit What-I-think** — compose span-grounded narrative, CI-aware diff panel, tag paragraphs "interpretation, not forecast"
8. **Write logs** — append/update all 10 logs; add today's snapshot
9. **Update agent memory** — distill tick to ~500 lines in agent/memory.md, rotate older to archive
10. **Commit + PR** — `proposed-signals/{TODAY}` branch + auto-PR; do not merge; operator approves

**Discipline** (enforced in prompt body): no score_overrides, every narrative claim cites source, every LR carries source class, pace governance + inertia detection logged, on budget exhaustion write deferred queue + exit cleanly, minimal-attention mode at operator-absence >7d, stop semantics (hallucinated event = drop+flag; 3+ stops/tick aborts tick).

### 3.1 Layer 0 — Agent loop

Each tick:
1. Read accumulated evidence + scheduled triggers (event log diff since last tick)
2. Read sources-shifted log (Polymarket/Metaculus/expert moves since last tick)
3. Identify highest-uncertainty / highest-layer-disagreement / highest-decision-stakes question
4. Select investigations per 3-tier autonomy:
   - **Tier A (auto-execute)** — under $0.50/action AND reversible: re-scrape source, re-fetch market, run existing extraction prompt against new source
   - **Tier B (auto-execute-with-notification)** — over $0.50 OR new-prompt-variant OR cross-source corroboration: runs immediately, surfaces in agent-decision log
   - **Tier C (operator-required)** — irreversible/non-routine/judgment: queues in operator panel
5. Update posteriors (Layer 2)
6. Emit *What I think* update; write to all relevant logs
7. Surface "no-change" honestly when nothing moved >2pp; surface "what considered changing but didn't" (pace governance)

### 3.2 Layer 1 — Signal extraction

Primary: ConfliBERT (English, ~85% F1 PLOVER) + ParsBERT fine-tuned (Persian, target mid-80s). Secondary: LLM with span-grounded JSON mandatory. Dedup: MinHash LSH → entity+temporal bucket → embedding-cosine → cluster ID. Hallucination control: span citations + semantic-entropy abstention + 200-500 frozen golden-set eval on every prompt change.

### 3.3 Layer 1.5 — Adversarial-input filter

Single-source claim → quarantine. State-media-originating → regime-positioning channel only; needs ≥2 Tier-1 corroboration to enter factual channel. Anomaly signals (AIS spoof, ADS-B blackout, document-leak with provenance issues) → flagged as deception/intent signal; enters posterior as evidence-of-intent, not surface fact. Source-clustering disagreement (high entropy) → posterior variance bumped, point estimate softened.

### 3.4 Layer 2 — Bayesian belief update

Per question, full posterior chain. **Sourced LR table** — every LR labeled `historical-analog` / `market-implied` / `explicitly-subjective-with-replacement-criteria`. Each event multiplies into posteriors as `LR × cluster_diversity_score`. Cap aggregate per-day log-LR movement at ±0.5/question. **Per-event retrospective**: 14d-resolving events that miscalibrate flag LR "reality-check failed" immediately.

**Successor-question revisitation** (Round 3 fix folded): on resolution, predeclared successors are revisited by the agent — agent confirms each predeclared successor is still the most decision-relevant given the actual resolution, modifies/adds/drops with logged justification, then commits the updated portfolio.

### 3.5 Layer 3 — Forecaster ensemble (late fusion)

Per question, 4-5 inputs depending on baseline class + SOTA applicability:
1. **Bayesian posterior** (Layer 2)
2. **Appropriate baseline** — AR for recurring (D1-D4, B4, B5, C2, C4) OR Polymarket-or-broad-reference-class-rate for unique (A1, A3, A4, A5, B1, B2, B3, C1, C3, E1, F1, F2)
3. **Market consensus** — Polymarket + Metaculus + Manifold weighted by liquidity (only on questions with markets)
4. **External SOTA** — Mueller-Rauh ConflictForecast on B1-B5 (onset-flavored only); null on every other question (Round-3 fix H3)
5. **Named-expert composite** — Sadjadpour + Vaez + Alfoneh + Khalaji + Batmanghelidj + Nasr + Maloney; Takeyh + Parsi as polar baseline (averaged together to neutralize chronic over-prediction in opposite directions). Initially equal-weighted; performance-weighted at N≥10 resolutions.

**Aggregation**: performance-weighted log-odds pool + extremization k≈2.5 + rolling isotonic recalibration. Until N≥10 resolutions, surfaces "ensemble in equal-weight regime."

**Forecast age decay**: only most recent ~40% of each forecaster's contributions enter pool, exponential decay.

**Layer-disagreement output**: when ensemble inputs diverge >15pp, surface "models disagree" alongside aggregate, components individually visible. Disagreements logged to controversies log.

### 3.6 Layer 4 — Output

Per question:
- Probability + 80% credible interval (numeric)
- **ICD-203 label always alongside** — published mapping table (with tail buckets):
  ```yaml
  vanishing: <1%
  almost_no_chance: 1-5%
  very_unlikely: 5-20%
  unlikely: 20-45%
  roughly_even_chance: 45-55%
  likely: 55-80%
  very_likely: 80-95%
  almost_certain: 95-99%
  near_certain: >99%
  ```
- Reference class (strict + broad, both visible)
- Baseline comparison (Brier vs baseline once resolutions accumulate)
- "What moved this number" (last 5 evidence updates)
- Layer-disagreement flag when ensemble divergent
- Humility flag (questions where model class has no track record → "out of model scope")

### 3.7 Layer 5 — Narrative (What I think, daily-brief shape)

Composes daily from Layer 4:
- **24h diff panel** at top: probabilities moved >2pp, evidence ingested, LR revisions, agent investigations completed, resolutions, NEW questions added, controversies flagged, sources-shifted moves
- 1-paragraph headline read in plain language
- ICD-203 vocabulary in narrative ("*likely*", "*roughly even chance*")
- **Each narrative paragraph explicitly tagged interpretation, not forecast** — separate from numeric probabilities
- Top 3 reasons probability moved this week
- Top 3 things to watch
- 1 cross-currents (where ensemble layers disagree)
- "What I considered changing but didn't" (pace governance)
- "What should have changed but didn't" (inertia detection)
- Agent open-investigation queue
- Last update + freshness banner + next scheduled update + budget remaining

### 3.8 Calibration spine

Every prediction snapshot: full feature vector. On resolution: Brier + Murphy decomposition + AUC + PR + CRPS. Live calibration plot. Monthly LR recalibration + per-event retrospective queue. Quarterly ensemble-weight rebalance. Quarterly public model report. External 90-day review (Sadjadpour/Vaez/Alfoneh rotating); 5 most-divergent predictions sent for critique; feedback published as artifact + drives method changes. Quarterly external review thereafter.

### 3.9 Reference-class registry — two-tier

```yaml
A1_iran_us_framework_deal:
  strict_class:
    inclusion: "Iran-US bilateral nuclear-framework deal, FM-level or higher"
    members:
      - {name: JCPOA_2015, signed: 2015-07-14}
      - {name: agreed_framework_2003-05, status: collapsed}
      - {name: tehran_declaration_2010, status: marginal}
    n: 3
    base_rate_30d: 0.40
    note: "Used for narrative anchor; n too small for probability."
  broad_class:
    inclusion: "Any nuclear-armed-or-near-armed bilateral framework deal in past 70 years"
    members:
      - JCPOA_2015, NK_agreed_framework_1994, NK_six-party_2005, Libya_disarmament_2003,
        India_civil_nuclear_2005, Pakistan_Taliban_2008-19, Iran_EU3_2003, USSR_INF_1987,
        USSR_START_1991, Iran_IAEA_AP_2015...
    n: 18
    base_rate_30d_acceptance_after_proposal: 0.32
    base_rate_90d: 0.51
    note: "Used for actual probability calculation."
  last_audited: 2026-05-03
  next_audit: 2026-08-03
```

Both tiers visible in *Show your work* depth-expansion. Quarterly + external review.

---

## 4. Eight first-class logs (committed markdown)

For a *living* model the change-history IS the product. All logs are committed markdown in `logs/` dir, queryable by date/question/event-type, RSS-subscribable.

| Log | Path | Captures |
| --- | --- | --- |
| **Event log** | `logs/events/YYYY-MM-DD.md` | Every ingested event: source, cluster ID, channel, applied LRs, affected questions |
| **Probability-change log** | `logs/probability-changes/YYYY-MM-DD.md` | Every probability movement with attribution chain |
| **LR-revision log** | `logs/lr-revisions.md` (running) | Every LR change with old, new, source class, justification |
| **Reference-class-change log** | `logs/reference-classes.md` (running) | Members added/removed with justification |
| **Signal-admission log** | `logs/signal-admissions.md` (running) | Signals admitted/rejected/re-validated with gate criteria results |
| **Adversarial-input log** | `logs/adversarial-inputs/YYYY-MM-DD.md` | Quarantined claims, deception flags, state-media-positioning entries |
| **Agent-decision log** | `logs/agent-decisions/YYYY-MM-DD.md` | Tick reasoning, tier (A/B/C), investigations, "what considered changing but didn't" |
| **Resolution log** | `logs/resolutions.md` (running) | Every question resolved: predicted vs actual, Brier, post-mortem, successor questions |
| **Sources-shifted log** | `logs/sources-shifted/YYYY-MM-DD.md` | Daily Polymarket/Metaculus/expert delta snapshots |
| **Controversies log** | `logs/controversies.md` (running) | Layer-disagreement events, expert-panel divergences, adversarial-input flags requiring resolution |

Each log linkable from any narrative. Daily logs roll up into weekly + monthly indexes. Full retention forever; quarterly indexed.

---

## 5. The dashboard re-imagined — progressive disclosure

**Single homepage** = *What I think* shape, with progressive disclosure.

Layout (top-to-bottom):
- **Freshness banner** + last update + next scheduled update + budget remaining
- **24h diff panel** — moves, new evidence, LR revisions, resolutions, new questions, controversies, sources-shifted (every entry click-to-expand into log)
- **Today's top question** (most decision-relevant + biggest-mover) — full Layer-4 output click-to-expand into evidence chain
- **Question board** — 22 questions, sortable; each row click-to-expand into per-question Layer-4 output with provenance
- **Headline narrative** (1 paragraph, ICD-203 vocabulary, *tagged "interpretation, not forecast"*)
- **Top 3 reasons probability moved this week** (sourced)
- **Top 3 things to watch**
- **Cross-currents** (ensemble layer disagreement)
- **Pace governance** — "What I considered changing but didn't" + "What should have changed but didn't"
- **Agent open-investigation queue** + **agent-effectiveness leaderboard** (Round-3 fix H6)
- **All 10 logs** entry-points (one section, each linked to log dir)
- **Calibration page** link
- **Reference-class registry** link
- **Signal admission gate audit** link
- **Humility section** link

No "Show your work" mode switch. Users who never click stay shallow; users who click descend as deep as they want.

### 5.1 What we cut from current site

All 4 score_overrides · alphaSignals trade output · fabricated game-theory payoff matrices · magic-number coefficients · missile/drone tempo charts (zero attacks for 26d; archived to history) · war-day counter, war-powers deadline (passed) · 12+18 stakeholder profiles → keep ~6 with documented decision-relevance + Pearl-DAG path · 38 exotic signals → keep ~10 that pass the 3-question gate · current 5-bucket synthesized outcome distribution (becomes derived view of question portfolio)

---

## 6. Build sequence

### Phase 0 — Useful Daily MVP (5 days)

Ships at end of week 1 as new homepage.

- **8 starter questions** (re-prioritized by user/Omid relevance): D1 (USD/IRR — affects family/business), D3 (US gas — affects daily life), A1 (deal — pivotal), A2 (Hormuz transit — business-relevant), B1 (US strikes Iran — major event), B3 (Israel strikes Iran — major event), C1 (Khamenei — major event), C2 (Iran protests — Iran-watching)
  *(F1, F2 Omid-personal questions deferred to Phase 1 pending user confirmation per Round-4 fix I5)*
- Manual probabilities (operator initial read; sourced LR comments inline)
- Each question carries explicit **expiration policy** ("auto-resolve NO at deadline" or "agent-judgment at deadline")
- Polymarket scrape for ~3 questions with markets (A1 if available, B1, C1)
- Single-page progressive-disclosure homepage
- 24h diff panel **with CI-aware noise suppression** (only headlines moves > question's 80% credible-interval half-width)
- Three logs live: event, probability-change, agent-decision (committed markdown in `logs/`)
- Calibration harness (snapshot every prediction nightly; Brier scoring stub)
- Daily 06:00 ET cron emits fresh "What I think" — even on no-news days; "no change today" honest framing
- **Agent narrative span-grounded** from day 1 — every claim cites source/LR/evidence
- Cron prompt template at `agent/cron-prompt.md` published + version-controlled
- Agent memory file at `agent/memory.md`
- Current dashboard accessible at `/legacy`
- Operator workload Phase-0: ~30 min/day

### Phase 1 — Question portfolio + agent loop (week 2-3)

- Expand to all 22 questions (including Omid-personal F1, F2)
- Reference-class registry seeded (strict + broad tiers)
- Agent loop (Layer 0) with 3-tier autonomy + per-tick budget
- Successor-question generation pipeline
- Five additional logs live: LR-revision, reference-class-change, signal-admission, adversarial-input, resolution
- Controversies + sources-shifted logs (10 logs total)
- Stakeholder-tagged question filters in homepage

### Phase 2 — Daily ingest + extraction (week 4-5)

- Tier-1 ingest: bonbast, TGJU, Kpler, ACLED, MarineTraffic, Polymarket, Metaculus, ConflictForecast, GDELT GKG
- ConfliBERT extraction (English)
- MinHash dedup
- Disagreement-weighted source clustering
- W3C PROV-DM provenance graph
- Adversarial-input filter (Layer 1.5)

### Phase 3 — Bayesian + ensemble (week 6-7)

- Sourced LR table (50 event types × 22 questions, source class on every LR)
- Posterior-update engine with daily log-LR cap
- Per-event retrospective + LR-revision log automation
- Late-fusion ensemble (Bayesian + baseline + market + SOTA-where-applicable + expert)
- Agent-effectiveness leaderboard

### Phase 4 — Persian + event triggers + ADS-B (week 8-9)

- ParsBERT fine-tuned on PLOVER (or NLLB translate-then-extract as Phase-4 fallback)
- Persian Tier-1 sources
- ADS-B Exchange diplomatic-flight monitor + callsign-blackout detector
- Telegram channel monitor (Telethon, public channels only)
- Event-triggered re-runs (separate cron entry)

### Phase 5 — Calibration loop + external review prep (week 10-11)

- Calibration page (Brier vs Polymarket / Metaculus / AR baseline)
- All log indexes RSS-subscribable
- Forecaster track-record leaderboard
- Signal admission-gate UI audit
- Monthly LR recal automation
- External-review packet template

### Phase 6 — 90-day external review + ongoing (month 4+)

- Email Sadjadpour / Vaez / Alfoneh the model report + 5 most-divergent predictions
- Their critique → published artifact
- Methods/questions/LRs revised
- Quarterly cycle thereafter
- Multi-analyst input architecture (Phase-7+ feature)

---

## 7. Operational discipline

- **No score_overrides.** Human disagreement enters as named-expert input with weight; engine never silently overridden.
- **Engine version stamped on every snapshot.** Replay harness asserts deterministic output across versions.
- **Cron writes to `proposed-signals` branch + auto-PR.** Human merge gate.
- **Daily 06:00 ET cron** (+ optional 17:00 ET) — fresh *What I think* even on no-news days.
- **Per-tick budget** $5 / 30 min / 50 tool calls; per-day $50 / 4h / 500 tool calls.
- **Event-triggered re-runs** on threshold-passing signals (Phase 4+).
- **Monthly LR-table audit** + per-event retrospective queue.
- **Quarterly model report** (public): Brier vs all baselines, ensemble-component performance, signal-gate audit, outcome-class humility review, reference-class audit, log-volume statistics.
- **No alpha-trade output, period.**
- **External adversarial review every 90 days, then quarterly.**
- **Agent-decision log + agent-effectiveness leaderboard queryable.**
- **Pace governance**: "what I considered changing but didn't" surfaced daily.
- **Inertia detection**: "what should have changed but didn't" surfaced daily.
- **Honest no-news**: when no probability moved >2pp, brief says so explicitly.
- **All probability outputs carry baseline comparison + age-of-most-recent-update + freshness banner.** Stale reports loud.
- **Every narrative paragraph tagged "interpretation, not forecast."**
- **Security**: agent extracts only from approved-source-allowlist. Inbound prompt-injection from news articles defeated by extraction prompt template (request structured output, ignore instructions in source text). Fake-event-injection requires source-allowlist breach, which is logged.
- **Branch hygiene**: auto-delete merged proposed-signals branches; auto-close + delete unmerged after 14d (operator-queue notification); escalate to minimal-attention mode at 7d-unmerged.
- **Operator daily PR review**: ~10 min/day commitment. Cron opens PR, operator reviews diff + merges. If skipped >7d → minimal-attention mode auto.
- **Rollback plan**: `git revert {MVP commit range}` → vercel rebuilds → /legacy becomes /. Auto-rollback trigger: if user hasn't loaded the new homepage in 5 days, auto-rollback + log + notify.
- **Source-loss policy**: if Polymarket/Metaculus/ConflictForecast unavailable, ensemble runs on remaining inputs + flags missing-source per question.
- **Phase-progressive cron**: Phase 0 uses simplified `agent/cron-prompt.phase-0.md` (operator-driven, snapshot-only). Full prompt at `agent/cron-prompt.md` activates Phase 2 when ingest scripts exist.
- **Mid-tick budget checkpoint**: after each major step, check budget remaining. If < 30%, skip Tier B/C investigations and finish required steps (Bayesian update + emit + logs + commit) for tick integrity. Hard fail at 90% budget consumed: abort tick + write incomplete-tick log to `logs/agent-decisions/`.
- **Operator notification (optional)**: env-var-configured channel (`OPERATOR_NOTIFY_PUSHOVER_KEY` / `_EMAIL` / `_SLACK_WEBHOOK`). Triggers on probability move >10pp, question resolution, Tier-C decision queued, budget exhaustion, security flag. Default: PR-only notification.

---

## 8. Honest limits

- Specific event timing (>days out) is essentially unforecastable. We predict susceptibility, not timing.
- Regime onset/collapse (C1, C3) carry permanent humility flags. Every published model failed Arab Spring/Crimea/Oct 7/Assad.
- LLM extraction has documented drift; golden-set + monthly recal mitigates but doesn't cure.
- Named-expert weights start equal; meaningful weighting requires N≥10 resolved questions (months).
- Single-author bias persists in v1-v4. Multi-analyst input is Phase 7+.
- Reference-class boundaries remain a judgment call; quarterly + external review mitigates but doesn't eliminate.
- Polymarket on most questions is thin or absent; market-input not always available.
- Daily updates can over-fit to recent narrative; pace governance + inertia detection mitigates but doesn't eliminate.
- Per-event retrospective only catches 14d-resolving LR errors; longer-horizon errors caught by monthly recal.
- Per-tick budget caps preclude exhaustive investigation of complex events.
- Omid-personal questions (F1, F2) carry small-N reference-class issue acutely.

The honest claim: top-quartile forecasting *system* on the discrete events it commits to, operating as a *living agent in cron* with full transparency about what it doesn't know and what it considered.

---

## 9. Open decisions for user

1. **MVP go/no-go?** Default: yes, ship 5-day MVP at homepage with 8 questions; current dashboard moves to `/legacy`.
2. **Cron cadence — daily-only or twice-daily?** Default: daily 06:00 ET to start; add 17:00 ET in Phase 2.
3. **~~~$4,000/year operating budget~~** *(superseded 2026-05-03: agent runs under user's existing Claude subscription via RemoteTrigger; all data sources are free public APIs; total operating cost = **$0/year**)*
4. **Paid feeds?** **Permanently out-of-scope per user constraint 2026-05-03.** Kpler / Spire / Windward / Bloomberg / Metaculus-token (free with account but requires manual setup) all stay out unless user explicitly opts in.
5. **Persian NLP scope.** Default: NLLB translate-then-extract for Phase 4; full ParsBERT fine-tune in Phase 6.
6. **Telegram + ADS-B scope.** Default: Phase 4-5 with conservative trigger logic.
7. **External reviewer pick.** Default: Sadjadpour first; fallback Vaez or Alfoneh.
8. **What we keep at `/legacy` during transition.** Default: full current site, one redirect away during 11-week build.
9. **Log retention policy.** Default: full retention forever; compress + index after 90d.
10. **Omid-personal questions (F1, F2 proposed).** Confirm/edit/replace before Phase 1 entry. (Drop entirely OK.)

If approved as-is, I move to Phase 0 immediately.

---

## 10. File schemas (Round-5 fix J2)

### `portfolio.yaml`
```yaml
- id: A1
  category: diplomatic_resolution
  question: "Iran-US framework agreement signed (any form) by 2026-09-30"
  resolution_criterion: |
    YES on joint readout from State Dept + Iranian FM + at least one mediator
    (Pakistan/Oman/Qatar) confirming a written framework with sanctions-relief
    or nuclear-monitoring components.
  deadline: 2026-09-30
  baseline_class: polymarket_or_broad_reference_class  # or: ar
  reference_class_strict: A1_iran_us_framework_deal_strict
  reference_class_broad: A1_bilateral_nuclear_framework_broad
  expiration_policy: agent_judgment_at_deadline  # or: auto_resolve_no
  stakeholder_tags: [us_foreign_policy_decisionmaker, iran_regime_survival, oil_energy_markets, omid_personal_economic_exposure]
  successors_on_resolve_yes:
    - "Iran enriches above 60% within 90d of signing?"
    - "US lifts first sanctions tranche by stated deadline?"
    - "Israel publicly disowns deal within 30d?"
    - "IAEA reports first compliance discrepancy within 180d?"
  successors_on_resolve_no_or_expire:
    - "Iran proposes second framework within 90d of A1 expiration?"
    - "US escalates pressure (new sanctions tranche / strike) within 30d?"
  current_probability: 0.18
  current_credible_interval_80: [0.08, 0.32]
  current_icd203_label: very_unlikely
  last_updated: 2026-05-03T06:00:00-04:00
```

### `agent/memory.md` (~500 line cap)
```markdown
# Agent Memory — last updated {{TIMESTAMP}}

## Portfolio summary
[20 questions, current probabilities + ICD-203 labels + last-mover events]

## Open investigations (Tier A/B in progress, Tier C queued)
[items with priority, budget consumed, expected outcome]

## Recent LR revisions (last 30d)
[event_type → old_LR / new_LR / source class / justification]

## Named-expert standing forecasts
[Sadjadpour/Vaez/Alfoneh/etc current public positions per question]

## Top-of-mind context (carried forward)
[narrative threads, situational awareness, recent operator notes]

## What I considered changing but didn't (last tick)
[items + reasoning for non-change]
```

### `reference_classes.yaml`
See §3.9 worked example. Each class has: id, inclusion_criteria (text), members (list with name + date + status), n, base_rate_30d/90d, note, last_audited, next_audit. Strict + broad tiers.

### `lr_table.yaml`
```yaml
- id: khamenei_rejects_framework_state_tv
  description: "Khamenei makes public on-state-TV statement rejecting current framework offer"
  question_relevance:
    A1: 0.4   # LR: this event is 0.4× as likely under "deal happens" as "deal doesn't happen"
    A5: 0.2
    B1: 1.3
  source_class: historical_analog
  source_calc: "4 of 6 past Iran framework rejections in 30d windows ended talks → 0.33; +0.07 for current heightened context"
  reality_check_status: passing  # or: flagged_pending_revision
  last_revised: 2026-05-03
```

### Logs (committed markdown)
Each daily log = one file (`logs/events/2026-05-03.md`); each running log = one file (`logs/lr-revisions.md`). Append-only per tick. Hot in-repo for 90d, cold archived (Phase-5 decision: git LFS or S3).

### `agent/cron-prompt.md`
The full prompt body invoked verbatim each tick. Summary in §3.0.1; full file in repo.

### `agent/operator-queue.md`
Tier-C decisions queued for operator. Format: `## {{question_id}} — {{decision_required}}` with context + agent recommendation + open issue.

---

## 11. Migration plan (Round-6 fix K3)

### What survives from current `engine/` Python code
- **Atomic-write pattern** in `emit.py` (`write_atomic`) — directly reused
- **Calibration spine shape** in `calibration.py` (Brier, decomposition, history snapshot, actuals.yaml) — reused with new question-portfolio adapter
- **Snapshot/replay harness** in `tests/test_reproducibility.py` — reused; extended to cover full agent loop
- **Engine versioning** (`engine/__init__.py.__version__`) — reused; bumped 0.1.0 → 0.2.0 at Phase 2
- **Pytest infrastructure** — reused; new tests added for cron prompt determinism + log integrity
- **Provenance writer** patterns (signals_history/ snapshot, engine_history.json) — reused; expanded with W3C PROV-DM
- **Vercel deploy + build-public.py** — reused (Phase 0 ships to existing Vercel projects)

### What's deleted
- `engine/advanced.py` `alphaSignals` (no edge claim) — deleted
- `engine/advanced.py` `game_theory_equilibrium` payoff matrices (fabricated) — deleted; game-theoretic reasoning lives in narrative only with explicit "scenario reasoning, not Nash analysis" tag
- `engine/schema.py` 12+18 stakeholder profile fields, dynamics, ideology fields — pruned to ~6 stakeholders with documented Pearl-DAG decision relevance
- `engine/compute.py` `score_override` paths — deleted (architecture eliminates by design)
- All hand-set magic-number coefficients in `compute.py` and `advanced.py` — deleted; replaced with sourced LR table
- 38 exotic_signals fields → ~10 that pass the 3-question gate
- 5-bucket `synthesized_outcome_probabilities` → derived view of question portfolio, not a separately-computed model

### What's net-new (built Phase 0-3)
- `agent/cron-prompt.md` + `agent/cron-prompt.phase-0.md`
- `agent/memory.md` (~500-line state distillation)
- `agent/operator-queue.md`
- `portfolio.yaml` (20 questions + schema per §10)
- `lr_table.yaml` (sourced LRs)
- `reference_classes.yaml` (strict + broad tiers)
- `logs/` directory (10 log types per §4)
- `scripts/fetch_tier1.py`, `scripts/extract_confli.py`, `scripts/dedup_minhash.py`, `scripts/adversarial_filter.py`, `scripts/per_event_retrospective.py`, `scripts/render.py`
- W3C PROV-DM provenance writer
- 3-question signal admission gate
- Agent-effectiveness leaderboard

### What's deferred (Phase 4+)
- ParsBERT fine-tune (Phase 4 starts with NLLB translate-then-extract)
- ADS-B + Telegram monitors
- External 90-day review (Phase 6)
- Multi-analyst input architecture (Phase 7+)

### Migration sequence (matches §6 Build sequence)
- Phase 0 (week 1): old site stays; new site published at `/v2`. `/v2` = MVP homepage. Old `/` unchanged.
- Phase 1 (week 2-3): `/v2` becomes `/`, old site moves to `/legacy`. `engine/` Python helpers begin pruning.
- Phase 2-3 (week 4-7): full ingest pipeline; cron prompt upgrades to full version; engine.__version__ → 0.2.0; deleted-code list above is fully removed.
- Phase 4-5 (week 8-11): Persian + ADS-B + calibration loop; engine.__version__ → 0.3.0.
- Phase 6+ (month 4+): external review; engine.__version__ progressing per quarterly cycle.

Rollback at any phase: `git revert {phase commit range}` → previous phase active.

---

## 12. Convergence statement

This spec was iteratively hardened through seven adversarial review rounds. The trajectory of substantive critiques per round:

| Round | Substantive critiques | Texture |
| --- | --- | --- |
| 1 | 12 | Architectural fundamentals (LR sourcing, signal gate, reference classes, source weighting, agent definition, UX, ICD-203, baselines, question selection, MVP, adversarial inputs, external review) |
| 2 | 14 | Architectural + new user requirement (daily-update + logs + living-model framing) |
| 3 | 17 | Architectural + selection bias (small-N reference classes, SOTA mismatch, agent budget, MVP unsustainability, agent performance metrics, user personal-relevance) |
| 4 | 14 | Architectural + operational (TL;DR sprawl, rolling horizons, agent memory, cron prompt template, narrative span-grounding) |
| 5 | 6 | Mostly operational (cron prompt size, file schemas, cold-start ensemble, cost envelope, MVP relevance, ICD-203 tails) |
| 6 | 4 | Operational (branch hygiene, phase-progressive cron, migration plan, rollback) |
| 7 | 2 | Nits (mid-tick budget, operator notification) |

Round 8 would yield 0-1 substantive critiques drawn from speculation (Anthropic pricing volatility, future model deprecations, hypothetical user behaviors) or aesthetic preferences. Continuing past v8 would be theater, not engineering.

**Convergence declared at v8.** The spec is approved to ship to Phase 0 implementation upon user authorization (§9 open decisions).

The remaining risk surface is *operational* (will the operator merge daily PRs? will Polymarket persist? will Anthropic model updates break the cron prompt?) and *empirical* (will Brier scores against benchmarks turn out competitive? will the alpha lane prove real?). Neither is solvable by additional design rounds. They are answered by shipping and measuring.
