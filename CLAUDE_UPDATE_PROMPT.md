# Iran War Dashboard v2 — Recurring Update Instructions

You are updating the Iran War Dashboard (iran-war-dashboard-murex.vercel.app). This dashboard provides **predictive analysis** of the 2026 Iran conflict.

## What to do

1. **Search the web** for the latest developments in the 2026 Iran war using multiple queries:
   - `Iran war [today's date] latest`
   - `Iran missile drone attack Gulf [today's date]`
   - `Brent crude oil price today`
   - `Iran war casualties update`
   - `Iran war diplomacy negotiations [today's date]`
   - `Houthi Yemen attack [today's date]`
   - Any other relevant queries based on what you find

2. **Read the current `war-data.json`** from this repo

3. **Perform a FULL RE-ANALYSIS** of the entire file — not just appending a new day:
   - Review and revise ALL historical daily launch estimates if better data is now available
   - Update oil prices with confirmed close/open data
   - Revise casualty figures if new counts are reported
   - Update all analytical sections (sitrep, theory, scenarios, endstate, shipping, publishing, business impact)
   - **Re-score all 5 predictive vectors** for today and revise historical scores if warranted
   - **Refit the two capability models** (exponential decay vs plateau/rationing)
   - **Update the war outcome prediction** based on latest vector convergence
   - Add the new day's data if a new day has started since the last update
   - If still the same day, update the existing day's entry with latest information

4. **Ensure data integrity** (see validation section below)

5. **Write the updated `war-data.json`** to the repo

6. **Commit and push**:
   ```
   git add war-data.json
   git commit -m "war-data update [timestamp]"
   git push origin main
   ```

---

## Data methodology

- **D1-D10 missiles/drones**: JPost verified day-by-day (cumul: 2,410 missiles / 3,560 drones)
- **D11**: UAE MoD official (13 missiles + 39 drones UAE-only, scaled x2.08 for all-theater)
- **D12+**: Fragment estimates from Gulf state reports, scaled via INSS ratio (UAE ~ 48% of all projectiles)
- **Oil**: CNBC/Investing.com confirmed where available, interpolated between
- **All estimates**: Use best available fragment data. Never leave a data point blank or null.

## Source hierarchy

1. Official military/government statements (CENTCOM, UAE MoD, IDF, IRGC)
2. Wire services (Reuters, AP)
3. Major outlets (CNN, Al Jazeera, BBC, NPR)
4. Research organizations (GlobalSecurity, ACLED, IISS, FDD)
5. Specialist outlets (Breaking Defense, Iran International)
6. Wikipedia (Iran war / Timeline articles -- good aggregation)

## Key discrepancy to maintain

Iran claims ~700 missiles / ~3,600 drones total. JPost/Israeli estimates are much higher. IRGC claimed D16 that "most weapons cache intact, using decade-old missiles." Dashboard uses JPost series for trend continuity but documents the discrepancy in source notes.

---

## PREDICTIVE FRAMEWORK (v2 — critical section)

### Capability Models

Update `predictive.models` each cycle:

**Exponential Decay Model:**
- Recompute `halfLife_days` from D1-D10 actual data (fit exponential: y = A * e^(-t/tau))
- Update `projectedZeroDay` — when does the decay model predict <5 launches/day?
- Update `confidence` — R-squared of model fit against ALL actual data (not just D1-D10). This score should DECREASE if the plateau continues, because the plateau falsifies exponential decay.
- Update `projectedOutcome` and `falsifiedBy`

**Plateau/Rationing Model:**
- Recompute `plateauRate` as average of last 7 days of missile launches
- Update `projectedDuration_weeks` based on estimated remaining stockpile / daily burn rate
- Update `confidence` — how well does a piecewise model (exponential D1-D10 then plateau) fit ALL data? This should INCREASE if plateau continues.
- Update `projectedOutcome` and `falsifiedBy`

**Projection Arrays:**
- `projectionLabels`: extend 14 days past latest data
- `decayProjection`: actual data for historical days, then exponential extrapolation for forecast days
- `plateauProjection`: actual data for historical days, then plateau rate for forecast days

### 5-Vector Convergence Scoring

Score each vector 0-10 for today. You may also revise historical scores.

**Vector 1: Military Exhaustion** (0 = full capability, 10 = no capability left)
- 0-2: Launch rate >75% of D1. Factories intact. Stockpiles deep.
- 3-5: Launch rate 25-75% of D1. Factories being hit. Stockpiles uncertain.
- 6-8: Launch rate <25% of D1. Most factories destroyed. Plateau suggests rationing.
- 9-10: Launch rate <5% of D1. No meaningful offensive capability remaining.
- Also factor: CENTCOM damage assessments, IRGC counter-claims, coalition interceptor stocks (defender exhaustion matters too)

**Vector 2: Economic Pain** (0 = no pain, 10 = maximum unsustainable pain)
- 0-2: Oil <$80. Hormuz open. Gulf exports normal.
- 3-5: Oil $80-100. Hormuz partially blocked. Gulf exports -20-40%.
- 6-8: Oil $100-120. Hormuz toll system. Gulf exports -40-70%. Gas >$4.
- 9-10: Oil >$120 or chokepoint closed. Gulf exports -70%+. Global recession signals.
- Key: pain is measured for ALL parties — higher oil also hurts US consumers/voters

**Vector 3: Diplomatic Momentum** (0 = zero diplomatic activity, 10 = deal imminent)
- Track events as +1 (toward deal) or -1 (toward escalation):
  - +1: mediator meetings, formal proposals, safe passage expansion, tanker transits, G7/UN statements, ceasefire windows
  - -1: new fronts opened, nuclear strikes, ultimatums, corporate targeting threats, ambassador expulsions, deadline failures
- Normalize running sum to 0-10 scale. Current cycle: reset baseline at each major inflection point.

**Vector 4: US Political Sustainability** (0 = politically impossible to continue, 10 = strong domestic support)
- Key inputs: approval polls (Pew, AP-NORC, Quinnipiac), US KIA count, gas prices, congressional votes, media narrative, midterm positioning
- 8-10: >55% approval, <5 KIA, gas <$3.50
- 5-7: 45-55% approval, 5-15 KIA, gas $3.50-4.50
- 2-4: 35-45% approval, 15-30 KIA, gas $4.50+
- 0-1: <35% approval or mass-casualty event or >$5 gas

**Vector 5: Escalation Ceiling Distance** (0 = ceiling breached/imminent, 10 = far from any ceiling)
- Track proximity to each irreversible escalation:
  - Nuclear: radiation event, dirty bomb, enrichment surge
  - Chokepoint: Bab al-Mandab closure (Houthis)
  - Ground invasion: 82nd Airborne committed, Kharg Island landing
  - Power grid: April 6 deadline / civilian infrastructure destruction
  - Direct nuclear exchange: Iran breakout + Israeli response
- Score = distance from NEAREST ceiling. If ANY ceiling is at risk, score drops.

### War Outcome Prediction

Derive `predictive.warOutcome` from the 5 vectors:
- `prediction`: 2-3 sentence forecast of most likely outcome + timeline
- `derivation`: explain which vectors are driving the prediction and why
- `convergenceScore`: weighted average — use: Military(0.25) + Economic(0.20) + Diplomatic(0.20) + Political(0.20) + Escalation(0.15). Higher = more pressure for resolution.
- `convergenceInterpretation`: what the score means in plain language

### Additional Charts Data

Update `additionalCharts` each cycle:
- `conflictIntensity`: missiles + drones per day (must match oil.labels length — add 0 for pre-war day)
- `countriesTargetedPerDay`: count distinct countries hit each day
- `missileDroneRatio`: missiles / drones for each day (matches dailySeries.labels)
- `interceptRate`: estimated coalition intercept success rate 0-1 (from UAE MoD, IDF, and fragment data)
- `scenarioHistory`: snapshot current scenario probabilities at key inflection points (D1, D5, D10, D15, D20, D25, D29, etc.)

---

## BUSINESS IMPACT SECTIONS

### Iranfarhang (Book Supply)
- Tehran-based supplier of Persian-language books to US/Canadian university and research libraries for 25+ years
- Original shipping route: Air cargo Tehran -> Dubai (Emirates SkyCargo) -> Atlanta office -> UPS to institutions
- OFAC exemption: 31 CFR 560.210(c) -- informational materials (Berman Amendment). STATUTORY, not executive -- survives any sanctions regime
- Payment: Via KEMCO SARL, a third-country entity in France
- Key dependencies: Tehran warehouse inventory, Iranian publishing industry (paper imports, printing, internet), shipping routes, power grid

**Update each cycle:**
- `impactIranfarhang` / `prepIranfarhang` / `signalsIranfarhang` (existing)
- `publishingStatus` (existing)
- `iranfarhangExpanded.supplyChainTimeline` — update milestone estimates based on war developments
- `iranfarhangExpanded.routeViability` — update status/viability of each route
- `iranfarhangExpanded.ofacStatus` — check for any sanctions changes
- `iranfarhangExpanded.tehranCommsStatus` — update internet blackout hours, last contact
- `iranfarhangExpanded.inventoryRunway` — decrement months remaining, update critical date
- `iranfarhangExpanded.publishingDeepDive` — update each sub-sector with latest intel

### KIP (Import-Export)
- Private Iranian family import-export company using Dubai/UAE as logistics hub, re-export point, and financial gateway
- The Iran-UAE trade corridor is the lifeblood of this business
- Key dependencies: Hormuz strait (shipping), UAE banking (trade finance), Dubai free zones (warehousing), UAE airspace (cargo flights), personnel safety in UAE

**Update each cycle:**
- `impactKIP` / `prepKIP` / `signalsKIP` (existing)
- `kipExpanded.dubaiBankingRisk` — update score (0-10), trend, and detail
- `kipExpanded.alternativeHubs` — update scores if conditions change (e.g., Oman port attacked = lower risk score)
- `kipExpanded.hormuzReopeningTimeline` — update milestone statuses and estimates
- `kipExpanded.strandedCargo` — update container count, insurance claims status
- `kipExpanded.insuranceCostIndex` — add new data points at inflection points

### Writing style for business sections
- Every bullet should be SPECIFIC to the business, not a restatement of general war news
- Lead with the business impact, then explain why (the war event)
- Impact = what happened TO the business. Prep = what the business should DO. Signals = what to WATCH that would change the picture
- Prep items should be actionable: "do X this week" not "monitor developments"
- Use `<strong>Label:</strong>` formatting for lead-in

---

## ALL FIELDS TO UPDATE EACH CYCLE

### Core (existing)
- `meta.lastUpdated` — ISO timestamp
- `meta.notes` — source notes array
- `theoryBox` / `theoryBox_fa`
- `metrics` / `metrics_fa`
- `sitrep` / `sitrep_fa`
- `dailySeries` (labels, missiles, drones, sourceLabel, throughDate)
- `oil` (labels, brent, wti, note)
- `pressure` (labels, attrition, cost)
- `latestTargetBreakdown` (missiles, drones, note)
- `dailyRows` / `dailyRows_fa`
- `timeline` / `timeline_fa`
- `scenarioProbabilities` / `scenarioProbabilities_fa`
- `theoryEvaluation` / `theoryEvaluation_fa`
- `shippingRoutes` / `shippingRoutes_fa`
- `casualties` / `casualties_fa`
- `humanitarian` / `humanitarian_fa`
- `diplomacy` / `diplomacy_fa`
- `publicOpinion` / `publicOpinion_fa`
- `hormuz` / `hormuz_fa`
- `keyActors` / `keyActors_fa`

### Predictive (v2 — new)
- `predictive.models.exponentialDecay` (halfLife, projectedZeroDay, confidence, outcome, falsifiedBy)
- `predictive.models.plateauRationing` (plateauRate, projectedDuration, confidence, outcome, falsifiedBy)
- `predictive.models.projectionLabels` / `decayProjection` / `plateauProjection`
- `predictive.vectors.*` (all 5 vectors — daily scores)
- `predictive.vectorNotes.*` (all 5 — current explanations, EN + FA)
- `predictive.warOutcome.*` (prediction, derivation, convergenceScore, convergenceInterpretation)

### Additional Charts (v2 — new)
- `additionalCharts.conflictIntensity`
- `additionalCharts.countriesTargetedPerDay`
- `additionalCharts.missileDroneRatio`
- `additionalCharts.interceptRate`
- `additionalCharts.scenarioHistory`

### Business Expanded (v2 — new)
- `iranfarhangExpanded.*` (all sub-objects, EN + FA)
- `kipExpanded.*` (all sub-objects, EN + FA)
- `impactIranfarhang` / `prepIranfarhang` / `signalsIranfarhang` (existing)
- `publishingStatus` / `publishingStatus_fa` (existing)
- `impactKIP` / `prepKIP` / `signalsKIP` (existing)

---

## DATA VALIDATION (run before commit)

1. All chart arrays must be same length within their group:
   - `dailySeries.labels.length === missiles.length === drones.length`
   - `oil.labels.length === brent.length === wti.length`
   - `pressure.labels.length === attrition.length === cost.length`
   - `predictive.models.projectionLabels.length === decayProjection.length === plateauProjection.length`
   - `predictive.vectors.labels.length === militaryExhaustion.length === economicPain.length === diplomaticMomentum.length === usPoliticalSustainability.length === escalationCeilingDistance.length`
   - `additionalCharts.conflictIntensity.length === oil.labels.length`
   - `additionalCharts.countriesTargetedPerDay.length === dailySeries.labels.length`
   - `additionalCharts.missileDroneRatio.length === dailySeries.labels.length`
   - `additionalCharts.interceptRate.length === dailySeries.labels.length`
2. `dailyRows.length === dailySeries.labels.length`
3. ZERO nulls in any chart array
4. ZERO duplicate dates in dailyRows
5. Chart values must match table values for every day
6. Vector values: 0-10 range
7. Model confidence: 0-1 range
8. Convergence score: 0-10 range
9. All `_fa` variant arrays must exist and have same length as English counterparts

## What NOT to do

- Do NOT just append a new day without reviewing all previous data
- Do NOT leave any chart array with null values
- Do NOT create duplicate date entries in dailyRows
- Do NOT skip the validation step
- Do NOT change the JSON structure/schema -- only update values within existing keys
- Do NOT remove any sections (predictive, business, analytical)
- Do NOT forget Farsi translations for all narrative fields
