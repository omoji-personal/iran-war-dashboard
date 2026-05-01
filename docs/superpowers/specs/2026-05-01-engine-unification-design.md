# Engine Unification — Design Spec

**Project:** P1 of 5 (Engine Unification → Calibration → Model → Market → Visual)
**Status:** Approved (delegated authority)
**Date:** 2026-05-01
**Author:** Claude (Opus 4.7) under user delegation

## Problem

`war-data.json` is hand-edited daily. The dashboard renders directly from it. Over time two voices have emerged:

1. **Fresh narrative voice** — `meta.notes`, `scenarioProbabilities`, `dailyRows`, `hormuzTransit`, `pressure`, `dailySeries`. Updated daily.
2. **Frozen engine voice** — `decisionEngine.dailyIndicators` (stops Apr 14), `decisionEngine.probabilityChangelog` (stops D45), `decisionEngine.leadingIndicators` (D44 narrative), `decisionEngine.calibration.methodology` ("current D37"), `decisionEngine.confidence.methodology` (pre-blockade prose), `coalitionFracture` (stops D38). Plus 7 stale flags including `ceasefireMode.enabled=true` (10 days post-expiry).

Root cause: there is no mechanical link between the two voices. They are independently typed.

The dashboard's premise is *prediction*. A prediction surface that drifts 2-4 weeks behind its inputs is no longer a prediction surface.

## Goal

A single source of truth (`signals.yaml`) that, when changed, regenerates `war-data.json` mechanically. Drift becomes structurally impossible. The dashboard surface is unchanged in shape; only its provenance changes.

This is the foundation for Projects 2–5 (Calibration, Model, Market, Visual). None of them can be built cleanly without it.

## Non-goals

- Web UI for editing signals (CLI is fine)
- Database (yaml + git history is fine)
- ML / model retraining (rule-based math)
- Retroactive recompute of historical days (snapshots are immutable)
- Multi-author tooling (single author)
- Visual changes to the dashboard (P5 territory)

## Architecture

```
signals.yaml          ──► engine.compute() ──► war-data.json (existing shape)
(NEW: source of truth)                                │
   │                                                  └─► dashboard.js (unchanged)
   └─► signals_history/                              
       2026-05-01.yaml ◄── auto-snapshot per emit ──►│
                                                      │
                                              engine_history.json
                                              (P2 hook — written but not consumed yet)
```

**Mental model:** `signals.yaml` in, `war-data.json` out. The dashboard never knows the engine exists.

## Repo layout (additive only)

```
iran-war-dashboard/
├── signals.yaml                  ← NEW: the only file edited daily
├── signals_history/              ← NEW: dated snapshots, append-only
│   └── 2026-05-01.yaml
├── engine_history.json           ← NEW: per-emit snapshot of computed outputs (P2 will consume)
├── engine/                       ← NEW
│   ├── __init__.py
│   ├── __main__.py               ← `python -m engine emit | lint | migrate | dry-run`
│   ├── schema.py                 ← pydantic: Signals model
│   ├── compute.py                ← scoring + outcomes + indicators (~300 LOC)
│   ├── emit.py                   ← assembles war-data.json from Signals + computed
│   └── migrate.py                ← one-time seed from current war-data.json
├── tests/                        ← NEW
│   ├── fixtures/
│   │   ├── signals_d63.yaml
│   │   └── expected_war-data_d63.json
│   ├── test_compute.py
│   └── test_emit_snapshot.py
├── pyproject.toml                ← NEW: deps (pydantic, pyyaml, pytest)
├── war-data.json                 ← unchanged shape; now machine-emitted
├── dashboard.js                  ← unchanged
├── dashboard.css                 ← unchanged (already lifted in design audit)
├── index.html                    ← unchanged
└── scripts/                      ← unchanged
```

## `signals.yaml` shape

The daily-edit file. Replaces hand-editing of 14 different keys across war-data.json.

```yaml
meta:
  day: 63                       # war day
  cf_day: 24                    # ceasefire day
  date: 2026-05-01
  notes:
    - "D63 (May 1, cfDay24): WAR POWERS DEADLINE + TRUMP BRIEFED ON CENTCOM STRIKE PLAN..."

mode:
  ceasefire_status: hollow      # active | hollow | extended_indef | collapsed
  # ceasefire_enabled is DERIVED: hollow/active/extended_indef → true; collapsed → false

constants:                      # rarely change — extracted to one place
  pre_war_brent: 65
  pre_war_hormuz: 135
  pre_war_gas: 3.00
  ceasefire_start_day: 39
  ceasefire_original_deadline_day: 53

today_scalars:
  brent: 114
  brent_intraday_high: 126
  wti: 103.50
  gas_price: 4.30
  hormuz_vessels: 7
  rial_per_usd: 1810000
  zero_attack_streak_days: 24
  internet_blackout_hours: 1536
  ships_stranded: 2000
  us_kia: 15
  us_wounded: 520
  us_aircraft_lost: 7
  lebanon_killed: 2521
  iran_civ_killed_hrana: 3540

condition_inputs:
  deal:
    iran_proposal_active: false      # D60 proposal rejected D62
    us_acceptance_signal: 0.2        # 0..1
    nuclear_gap_pp: 15               # 5yr vs 20yr enrichment freeze
    deal_score_override: null        # if set, used directly (escape hatch)
  us_exit:
    gas_pain_above_threshold: true   # gas_price > 4.20
    war_powers_passed: true
    centcom_strike_plan_briefed: true
    us_exit_score_override: null
  iran_acceptance:
    khamenei_public_vow_against: true
    irgc_in_charge: true
    formal_proposals_rejected: 3
    iran_acceptance_score_override: null
  escalation:
    centcom_briefed: true
    hezbollah_action_recent: true
    new_blockade_action: true
    escalation_score_override: null

new_events:
  violation:                     # appended to ceasefireViolations
    severity: 3
    actor: Hezbollah
    target: "IDF artillery, Shomera"
    description: "Hezbollah drone wounded 12 IDF soldiers..."
  negotiation: null              # appended to ceasefireNegotiations if present
  recovery_point:                # appended to ceasefireEconomicRecovery
    hormuz_daily: 7
    brent_daily: 114
    ships_stranded: 2000
  daily_series:                  # appended to dailySeries.{missiles,drones}
    missiles: 0
    drones: 0
  daily_row:                     # appended to dailyRows
    date: "May 01"
    missiles: 0
    drones: 0
    primary_targets: ""
    capability: "..."
    cost: "..."
    assessment: "D63 — ..."
```

~50 lines per day. Most fields stable; only scalars + new_events truly change daily.

## What gets COMPUTED (not typed)

Every audit-flagged stale surface, plus everything mechanically derivable:

**Decision engine scores:**
- `decisionEngine.dealAvailability.score` ← weighted from `condition_inputs.deal.*` (or override)
- `decisionEngine.usExitPressure.score` ← weighted from `condition_inputs.us_exit.*`
- `decisionEngine.iranAcceptance.score` ← weighted from `condition_inputs.iran_acceptance.*`
- `decisionEngine.escalationProximity.score` ← weighted from `condition_inputs.escalation.*`

**Outcome probabilities (5 buckets):**
- `outcomeProbabilities.negotiatedResolution` ← `dealAvailability * usExitPressure * iranAcceptance`
- `outcomeProbabilities.escalationCatastrophe` ← `escalationProximity * (1 - dealAvailability)`
- `outcomeProbabilities.protractedContinuation` ← residual after escalation + negotiated
- `outcomeProbabilities.internationalIntervention` ← function of escalation + coalition
- `outcomeProbabilities.other` ← 1 − sum(above)
- (Methodology pulled from existing prose — `derivation_*` strings templated)

**Scalar indicators (28 fields):**
- `warDays` ← `meta.day`
- `daysToDeadline` ← computed (or `null` when past)
- `gasPrice` ← `today_scalars.gas_price`
- `brentShock` ← `(brent - pre_war_brent) / pre_war_brent`
- `hormuzRecovery` ← `hormuz_vessels / pre_war_hormuz`
- `launchRate7DMA` ← rolling sum of last-7 `dailySeries.{missiles,drones}` from history
- `launchRateVsD1` ← `launchRate7DMA / d1Missiles`
- All cumulative casualties ← from `today_scalars`

**Narrative:**
- `decisionEngine.confidence.methodology` ← templated, references today's actual conditions
- `decisionEngine.calibration.*.methodology` ← templated, today-aware
- `decisionEngine.leadingIndicators[].signal` ← templated from current signals + recent slope
- `decisionEngine.dailyIndicators` ← rebuilt from full signal history each emit

**Mode + deadline:**
- `ceasefireMode.enabled` ← derived from `mode.ceasefire_status` (hollow/active/extended_indef → true)
- `ceasefireDeadline.deadline` ← null when status=extended_indef
- `ceasefireDeadline.extensions` ← computed from history of status transitions
- `ceasefireDeadline.context` ← templated

**Series labels:**
- `dailySeries.throughDate` ← from `meta.date`
- `dailySeries.labels` ← rebuilt from history
- `coalitionFracture.labels` ← rebuilt from history (no longer frozen at D38)

## CLI surface

```
python -m engine emit       # read signals.yaml, write war-data.json + history snapshot
python -m engine dry-run    # show diff against current war-data.json, don't write
python -m engine lint       # validate signals.yaml + flag inconsistencies
python -m engine migrate    # one-time: seed signals.yaml from current war-data.json
```

## Daily workflow (post-migration)

```bash
$ vim signals.yaml             # update meta.day, today_scalars, new_events, notes
$ python -m engine emit        # regenerate war-data.json + snapshot
$ git add -A && git commit -m "D64 update"
$ git push                     # auto-deploys via Vercel
```

## Migration plan

1. `python -m engine migrate` reads current `war-data.json` + `meta.notes[0]` (D63 prose)
2. Reverse-engineers a seed `signals.yaml`:
   - Extracts scalars from notes (regex: `Brent \$([\d.]+)`, `gas \$([\d.]+)`, etc.)
   - Pulls condition scores back into `condition_inputs.*` defaults
   - Inserts `*_score_override` for any value the engine math doesn't reproduce within tolerance
3. Writes `signals.yaml` + `signals_history/2026-05-01.yaml`
4. Re-emits `war-data.json` from the seeded signals
5. Diff old vs new printed to terminal:
   - Expected: stale prose → current; stale scalars → correct
   - User reviews; can edit `signals.yaml` and re-emit
6. When diff acceptable: old `war-data.json` is replaced (backup at `.war-data.json.pre-engine.bak`)
7. Commit. From here forward: edit `signals.yaml` only.

## Error handling

- pydantic validates `signals.yaml` on load → field-level error messages
- `engine emit` writes atomically (tmp + rename) — `war-data.json` is never partially-written
- `engine emit` always backs up to `.war-data.json.bak` before writing
- `engine emit --dry-run` shows diff without writing
- `engine lint` flags inconsistencies (e.g., `mode.ceasefire_status=collapsed` but `condition_inputs.escalation.new_blockade_action=false` — likely typo)
- Empty/missing override fields are silently treated as None — no warnings spam

## Testing

- `tests/test_compute.py` — unit tests per scoring function: given canned signals, assert exact scores within ±0.01 tolerance
- `tests/test_emit_snapshot.py` — golden-file: emit from `tests/fixtures/signals_d63.yaml`, compare against `tests/fixtures/expected_war-data_d63.json`
- `tests/test_migration.py` — round-trip: migrate from current war-data.json, emit, assert key surfaces match within tolerance
- Run via `pytest`. Goal: changing engine math without updating tests = CI fails.

## Project boundary (definition of "done")

1. ✅ `signals.yaml` exists and is hand-edited
2. ✅ `python -m engine emit` regenerates `war-data.json` either identically or with explicit deltas user accepted
3. ✅ Dashboard renders correctly (manual visual confirmation across both modes)
4. ✅ All audit-flagged surfaces now derived (drift impossible by construction):
   - **Stale surfaces (6):** `decisionEngine.dailyIndicators`, `decisionEngine.probabilityChangelog`, `decisionEngine.leadingIndicators`, `decisionEngine.calibration.*.methodology`, `decisionEngine.confidence.methodology`, `coalitionFracture`
   - **Stale flags (7):** `ceasefireMode.enabled`, `ceasefireDeadline.deadline`, `ceasefireDeadline.extensions`, `ceasefireDeadline.context`, `ceasefireCalibration.source`, `decisionEngine.indicators.warDays`, `decisionEngine.indicators.daysToDeadline`
5. ✅ `signals_history/` writing on every emit — calibration spine ready to consume
6. ✅ `pytest` passes
7. ✅ A `.git/hooks/pre-commit` hook fails if `signals.yaml` changed but `war-data.json` did not (workflow safety)

## Risk register

| Risk | Mitigation |
|---|---|
| Migration produces different scores than hand-typed (math ≠ gut) | `engine migrate` shows diff; user can set `*_score_override` to preserve gut value |
| Engine drift from evolving methodology | Tests + `engine_version` field in snapshots; bump version when methodology changes |
| Daily workflow friction (forget to run `engine emit`) | Pre-commit hook: signals.yaml changed without war-data.json change → fail |
| Python deps in a JS project | `pyproject.toml` + `.python-version` (already used in scripts/) |
| Vercel build doesn't run Python — fine, war-data.json stays committed | No runtime engine; emit is local-only |
| New per-day fields added to war-data.json shape later | engine.emit is the single place to add them; pydantic forces explicit handling |

## Hooks for future projects

- **P2 (Calibration):** consumes `engine_history.json` (per-emit snapshots of probabilities). Already written by P1; P2 just builds the read-side.
- **P3 (Model):** modifies `compute.py` only. Schema unchanged.
- **P4 (Market):** new `signals.market_polymarket`, etc. Schema extension; compute.py uses them as additional inputs.
- **P5 (Visual):** zero engine changes. Pure dashboard.js + dashboard.css + index.html.

## Open questions deferred

- **Backtesting** — running engine.compute over historical signals_history snapshots to evaluate model changes. Belongs to P3, not P1.
- **Multi-source ensemble weighting** — P3.
- **Live market data fetch** — P4.
