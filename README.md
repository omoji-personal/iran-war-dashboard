# Iran-US Conflict Predictive Agent — v0.2

A Brier-scoreable discrete-event prediction portfolio for the 2026 Iran-US conflict.
Re-architected 2026-05-03 from a wartime-tracker dashboard into a calibrated predictive
agent driven by a daily Claude Code cron tick.

**Live:** https://iran-war-dashboard-murex.vercel.app/
**Legacy (old wartime tracker):** https://iran-war-dashboard-murex.vercel.app/legacy

## What this is

Thirty-two questions across seven categories — diplomatic, military, regime, economic,
US-side, plus two family-business categories (Iranfarhang publishing-import, Kipa
specialty-chemicals importer-distributor on the Iran-UAE corridor). Each has:

- A pre-stated **resolution criterion** + hard deadline
- A point estimate + 80% credible interval
- An **ICD-203 vocabulary label** (US Intelligence Community standard)
- A **strict + broad reference class** at `reference_classes.yaml`
- A **stakeholder-tag set** (PERSONAL flag means directly tied to a family business)
- A **successor-question pipeline** that auto-spawns when the parent resolves

The model is **uncalibrated** — no prediction has resolved yet, no Brier scores exist.
Every probability is presented with a humility disclosure. Two questions (C1 Khamenei
death, C3 Mojtaba succession) carry permanent humility flags because every published
statistical conflict-forecasting model has failed at this outcome class.

## Architecture

- **Single homepage** (`index.html`) — editorial-brief layout, 32 question cards,
  CI bars, ICD-203 labels, 24h diff panel, stakeholder flags, category color accents
- **Daily Claude Code cron** (`trig_01UD1sGTg9SHWMN2HjY7AiBa`, 0700 ET) runs the
  10-step procedure at `agent/cron-prompt.phase-0.md`: scrapers → snapshot → render
  → commit to `proposed-signals/{TODAY}` branch → open draft PR for operator review
- **Free public APIs only** — Polymarket Gamma + Manifold + (optional) Metaculus.
  Total operating cost: **$0/year** (cron runs under existing Claude subscription)
- **Eight first-class committed-markdown logs** — change-history is the product
- **Programmatic `agent/memory.md` regeneration** via `scripts/refresh_memory.py`
  to avoid LLM-composition drift

## Files

| File | Purpose |
|---|---|
| `portfolio.yaml` | The 32 questions + state |
| `reference_classes.yaml` | Strict + broad classes per question |
| `lr_table.yaml` | Sourced LRs (Phase 2+) |
| `agent/cron-prompt.phase-0.md` | Canonical cron procedure spec |
| `agent/memory.md` | Programmatically-regenerated agent state |
| `agent/operator-queue.md` | Tier-C decisions awaiting operator |
| `scripts/render.py` | Generates `index.html` + `public.html` |
| `scripts/refresh_memory.py` | Regenerates `agent/memory.md` |
| `scripts/fetch_polymarket.py` | Polymarket Gamma scraper |
| `scripts/fetch_manifold.py` | Manifold scraper |
| `scripts/fetch_metaculus.py` | Metaculus scraper (auth-gated) |
| `scripts/run_tick.sh` | Manual local tick (alternative to cron) |
| `logs/` | Eight committed-markdown change logs |
| `portfolio_history.json` | Daily snapshots for diff calculation |
| `dashboard.css` | Editorial-brief styling (3300+ lines) |
| `legacy/` | Old wartime-tracker site (preserved at `/legacy`) |

## Local development

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e '.[dev]'

# Run a tick locally (no cron needed):
bash scripts/run_tick.sh

# Or step-by-step:
python3 scripts/fetch_polymarket.py
python3 scripts/fetch_manifold.py
python3 scripts/refresh_memory.py
python3 scripts/render.py --public
python3 -m pytest -q
```

## Operator workflow

1. **Open the homepage** — review what the agent thinks
2. **Edit `portfolio.yaml`** if a probability needs updating (Phase 0 = operator-only)
3. **Run `bash scripts/run_tick.sh`** to immediately re-render + log
4. **Commit + push** when ready
5. **Or wait for the daily cron tick** (0700 ET) — agent opens a draft PR; operator
   merges in ~10 min

Three Tier-C decisions await in `agent/operator-queue.md`:
- Confirm/edit F1-F12 family-business questions
- Approve Phase 0 → Phase 1 transition
- Operator-curated top-of-mind context updates

## Phase progression

- **Phase 0** (LIVE): operator-driven probabilities; cron does scraping + rendering only
- **Phase 1** (week 2-3): agent loop with 3-tier autonomy + 5 more logs + reference-class registry
- **Phase 2** (week 4-5): Tier-1 daily ingest + ConfliBERT extraction + adversarial filter + Bayesian update
- **Phase 3** (week 6-7): sourced LR posterior engine + ensemble layer + per-event retrospective
- **Phase 4** (week 8-9): Persian NLP + ADS-B + Telegram + event-triggered re-runs
- **Phase 5** (week 10-11): calibration page + RSS + monthly recal automation
- **Phase 6** (month 4+): 90-day external review by named domain experts (Sadjadpour / Vaez / Alfoneh)
- **Phase 7+** (long-term): multi-analyst input architecture; calibration page with Brier vs market baselines

## Honest limits

- Specific event timing (>days out) is essentially unforecastable — model predicts
  *susceptibility*, not timing
- Regime onset/collapse (C1, C3) carry permanent humility flags
- Black-swan blindness is structural — every published model failed Arab Spring,
  Crimea, Oct 7, Assad collapse
- No backtest exists yet — all current probabilities are agent-seeded guesses
- Single-author bias persists in v1-v8 — multi-analyst input is Phase 7+

Full design: `docs/superpowers/specs/2026-05-03-predictive-agent-design.md` (v8 —
converged after 7 adversarial-review rounds).

Audit: `docs/audits/AUDIT-2026-05-03.md`.
