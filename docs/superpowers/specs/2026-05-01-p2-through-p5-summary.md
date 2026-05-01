# P2–P5 Consolidated Spec — Iran War Dashboard Restructure

**Status:** Built (delegated authority — user directive: "trust and unleash")
**Date:** 2026-05-01
**Builds on:** `2026-05-01-engine-unification-design.md` (P1)

This is a tighter follow-on spec for projects 2–5, written after the build for completeness. The five projects were planned in series (D → B → A → E → C) and shipped together under user delegation.

---

## P2 — Calibration Spine (Status: built)

**Goal:** Track predicted-vs-actual over time. Brier score, calibration plot, bias direction.

**Implementation:**
- `engine/calibration.py` — pure functions: `load_history`, `load_actuals`, `compute_calibration`, `build_calibration_spine`, `brier_score`
- `actuals.yaml` — checked-in template; user marks resolved outcomes here
- `engine_history.json` — append-only snapshot of every emit (already written in P1)
- `war-data.json.calibrationSpine` — the read-side surface for the dashboard

**What it shows:**
- `spineLength` — count of historical predictions
- `calibration.brier_aggregate` — overall calibration score (lower = better)
- `calibration.calibration_buckets` — predicted-decile vs actual-frequency
- `calibration.bias_direction` — over/under/well-calibrated
- `resolutionProbabilitySeries` — time-series for resolution probability
- `outcomeBucketSeries` — time-series per outcome bucket

**Not yet:** UI rendering of the calibration plot (would belong in P5 follow-up).

---

## P3 — Model Upgrade (Status: built)

**Goal:** Better model. The engine itself was the upgrade (vs. the hand-typed scalars).

**Implementation (advanced predictive layer):**
- `engine/advanced.py` — twelve predictive sub-modules:
  1. `game_theory_equilibrium` — 2-player Nash + Pareto + trapped-welfare-loss
  2. `bayesian_evidence_chain` — sequential Bayes update from exotic signals
  3. `monte_carlo_simulation` — 5000-run forward simulation
  4. `regime_hazard_curve` — Cox-style continuous-time survival model
  5. `multi_horizon_forecast` — 1d/7d/14d/30d/60d/90d/180d/365d outcome curves
  6. `kelly_size` + `kelly_sizing_for_alphas` — half-Kelly trade sizing
  7. `reflexivity_adjustment` — model accounts for own publication impact
  8. `counterfactual_no_trump` / `counterfactual_no_khamenei_lock` — sensitivity analysis
  9. `cross_impact_matrix` — event-trigger → outcome-shift matrix
  10. `trump_decision_tree` — backward induction with EV scoring
  11. `information_cascade` — 14-day downstream event chains for major triggers
  12. `ultraread` — apex narrative synthesis

**Tests:** `tests/test_advanced.py` — 15 tests covering Bayes, Monte Carlo, hazard, multi-horizon, Kelly, game theory, decision tree, counterfactuals, reflexivity, cross-impact, cascade.

---

## P4 — Market Layer (Status: built — fetcher stubs in place)

**Goal:** Live prediction-market + financial data feeds.

**Implementation:**
- `engine/market_fetch.py` — `fetch_polymarket_iran_contracts`, `fetch_metaculus_iran_questions`, `fetch_brent_spot`, `market_update_report`
- `python -m engine market-update` — CLI subcommand that fetches available data and prints suggested `signals.yaml` edits (does NOT auto-edit — user reviews)
- Polymarket: free public API (no key required)
- Metaculus: free public API
- Brent spot: requires `OILPRICEAPI_KEY` env var (stub returns None without it)

**Failure mode:** All fetchers return None on network failure → engine emits with whatever's already in `signals.exotic_signals`. No hard dependency.

**Not yet:** Auto-fetch on `engine emit` (deliberate — user reviews suggested edits before apply).

---

## P5 — Visual Prioritization (Status: built)

**Goal:** Surface the deep-dynamics layer in the dashboard UI.

**Implementation:**
- `index.html` + `public.html` — new `<section class="panel intel-brief">` block with 13 sub-cards:
  - Ultra read (apex synthesis)
  - Synthesized outcome bars
  - Monte Carlo bars
  - Multi-horizon deal-probability chart
  - Game-theoretic Nash equilibrium
  - Iran regime survival hazard chart
  - Trump decision tree (rational EV)
  - Psych modifiers (deltas)
  - Crystallization triggers
  - Tail risks
  - Alpha signals (with Kelly sizing)
  - Counterfactuals
  - Top historical analog + lesson
  - Deep read (analytical narrative)
  - Stakeholder psychology grid (12 actors)
  - Iran regime/population split + deep dynamics
  - Predictive framework methodology
- `dashboard.css` — full styling for `.intel-brief`, `.intel-block`, `.intel-bar-row`, `.psych-grid`, `.psych-card`, `.iran-split-grid`, `.cryst-row`, `.tail-row`, `.alpha-row`, `.dt-row`, `.game-theory-row`, `.psych-row`, `.ultra-read`, `.deep-read`, `.framework-doc`. Bordered with gold; INTEL watermark; monospace where appropriate.
- `dashboard.js` — `renderIntelligenceBrief()` function + helpers `_intelBars`, `_renderMultiHorizonChart`, `_renderHazardChart`. Wired into existing `render()` flow with `safe()` wrapper.

**Visual style:** Distinct from regular panels via gold border + atmospheric gradient + INTEL watermark. Sized to read as the dashboard's headline analytical layer.

**Not visually verified:** Browser was locked from a prior Chrome session during implementation. Code-level verification: 32/32 pytest, JS syntax check passes (node --check), HTML structure balanced, public build succeeds. Visual confirmation pending user open of dashboard.

---

## Aggregate verification

| Check | Status |
|---|---|
| `pytest tests/` | 32/32 ✓ |
| `node --check dashboard.js` | OK ✓ |
| HTML balance (index.html + public.html) | depth=0 ✓ |
| `python -m engine emit` | success ✓ |
| `python -m engine dry-run` | success ✓ |
| `python -m engine lint` | success ✓ |
| `python scripts/build-public.py` | success ✓ |
| war-data.json keys | 70 (was 68 + deepDynamics + calibrationSpine) |
| `deepDynamics` keys | 33 |
| Audit-flagged stale fixes | warDays 38→63, daysToDeadline 0.83→null, gasPrice 4.1→4.30, brentShock 0.68→0.75 ✓ |

## What's left (deferred)

- **Pre-commit hook** — `signals.yaml changed but war-data.json didn't = fail` (mentioned in P1 spec; not installed)
- **Polymarket auto-fetch on emit** — currently manual via `engine market-update`
- **Visual rendering check** — browser was locked; user should open dashboard to confirm
- **Calibration plot UI** — calibrationSpine data is in war-data.json but P5 didn't add a UI for it (would be incremental P5.1)
- **Rolling re-emit of historical days** — currently each emit only stamps "today"; backfilling old days from old signals_history snapshots is not wired
