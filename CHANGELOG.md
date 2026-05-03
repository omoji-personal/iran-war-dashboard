# Changelog

## v0.2.0 (2026-05-03) — Predictive Agent re-architecture

Replaces the v0.1 wartime-tracker dashboard with a Brier-scoreable discrete-event
prediction portfolio driven by a daily Claude Code cron tick.

### Added
- **`portfolio.yaml`** — 32 questions across 7 categories (A diplomatic / B military
  / C regime / D economic / E US side / F.1 Iranfarhang / F.2 Kipa)
- **`reference_classes.yaml`** — strict + broad reference classes per question
- **`lr_table.yaml`** — sourced LRs (every LR labeled historical-analog /
  market-implied / explicitly-subjective with replacement criteria)
- **`agent/cron-prompt.phase-0.md`** — canonical 10-step cron procedure
- **`agent/memory.md`** — programmatically regenerated state (via
  `scripts/refresh_memory.py`)
- **`agent/operator-queue.md`** — Tier-C decisions awaiting operator
- **`scripts/render.py`** — generates `index.html` + `public.html` from
  portfolio.yaml + history
- **`scripts/refresh_memory.py`** — deterministic memory regeneration
  (replaces LLM hand-composition drift)
- **`scripts/fetch_polymarket.py`** — Polymarket Gamma API scraper (no auth)
- **`scripts/fetch_manifold.py`** — Manifold REST scraper (no auth)
- **`scripts/fetch_metaculus.py`** — Metaculus REST scraper (auth-gated 2025+)
- **`scripts/run_tick.sh`** — manual local-tick alternative to cron
- **`logs/`** — eight first-class committed-markdown change logs
- **`portfolio_history.json`** — daily portfolio snapshots for diff calculation
- **`actuals.yaml`** — resolved-outcome ledger (empty Phase 0; populated as
  questions resolve)
- **`tests/test_portfolio.py`** — schema/structural tests for portfolio +
  reference classes + LR table
- **`tests/test_render.py`** — render-pipeline tests
- **`tests/test_scrapers.py`** — scraper unit tests
- Editorial-brief homepage layout: 32 question cards with CI bars,
  ICD-203 vocabulary labels, humility/personal flags, 24h diff panel,
  category-color accents (7 distinct colors)
- HTTP security headers: X-Content-Type-Options, Referrer-Policy, X-Frame-Options
- ARIA landmarks on every section for screen-reader accessibility
- Agent v0.2 CSS: dark navy + cream + rust palette, Iowan Old Style serif +
  Inter sans, responsive

### Changed
- Daily cron `trig_01UD1sGTg9SHWMN2HjY7AiBa` repurposed: old signals.yaml-based
  news refresh → new 10-step Phase-0 procedure
  - Writes to `proposed-signals/{TODAY}` branch + draft PR (per audit R19)
  - NEVER pushes to main directly; operator merges in ~10 min
- `dashboard.css` retains both legacy SaaS styles (for /legacy) AND new
  agent-v2 styles (3300+ lines)
- Cost: $0/year (free public APIs only; cron under existing Claude subscription)

### Removed
- `signals.yaml`, `signals_history/`, `war-data.json`, `engine/`,
  `tests/test_compute.py`, `tests/test_advanced.py`,
  `tests/test_reproducibility.py`, `dashboard.js`,
  `scripts/{build-public,sensitivity_sweep,backfill_calibration,engine_version_diff,update_d48_evening}.py`
  → moved to `legacy/`
- All prior magic-number coefficients and score_overrides
- `alphaSignals` trade output (no edge claim)
- `synthesized_outcome_probabilities` 5-bucket distribution (now derived view
  of question portfolio)
- 12+18 stakeholder profiles (kept ~6 with documented decision relevance)
- 38 exotic_signals (kept ~10 that pass the 3-question gate)

### Fixed (post-launch adversarial review, same session)
- Round 1: dead-code purge, `engine_history.json` → `portfolio_history.json`
  rename, render.py topness/diff/icd203 boundary bugs, hardcoded date math
- Round 2: legacy `dashboard.js` absolute-path break, programmatic memory
  regeneration, cron prompt pip-install consistency
- Round 3: ARIA roles, content-type headers for `.yaml`, CSS box-shadow
  hover (avoid CLS)
- Round 4: cron-prompt RemoteTrigger update for memory refresh,
  `__import__` cleanup
- Round 5: queue parse skips template/placeholder lines, README Kipa
  description corrected, CSS focus-within for keyboard users, HTTP
  security headers
- Round 6: legacy canonical URL, `%-d` cross-platform fix, atomic
  memory write
- Round 7: portfolio engine_version → 0.2.0 (no -rc1)

### Known limitations
- No prediction has resolved yet — model is uncalibrated
- Metaculus public API requires auth as of 2025 (script gracefully skips)
- Polymarket tag filter doesn't actually filter; we fetch broadly + locally filter
- Single-author bias persists in v1-v8 (multi-analyst is Phase 7+)
- Black-swan blindness is structural

## v0.1.0 (Apr 2026)

Initial wartime-tracker dashboard. Now at /legacy.
