# Resume — Iran War Dashboard

**Last session**: 2026-06-15 (full audit + deal-era refresh, Day 108).

## TL;DR — 2026-06-15 deal-era update (shipped, NOT yet pushed at time of writing this line; see git log)

The war is ending. On **June 14** the US and Iran reached a **framework MOU** (signs **June 19**, Switzerland; 60-day window to a permanent deal): US naval blockade lifted, Strait of Hormuz reopening toll-free (physical recovery gated by mine-clearing), nuclear/sanctions/$24B-assets deferred. **Ali Khamenei was killed Feb 28; son Mojtaba has led since March 8** — this corrected a counterfactual the dashboard had carried.

What shipped this session (all cited from a 7-agent intel sweep + 4 adversarial verifiers):
- **Re-rated all 32 questions**; **resolved 9** (B1/B2/B3/B5/C1/C3/D2/D3 = YES, A5 = NO).
- **Added A6** (permanent settlement by Sep 30, ~50/50) and **B6** (ceasefire holds through Aug 31, ~70%) → 34 total.
- **Rewrote** `economic_war_frame` + `base_case` (EN+FA, full+public) to the deal-era worldview.
- **New deal-tracker component** (render + `metadata.deal_tracker`, EN+FA, public-safe) above the board.
- **Resolution rendering**: `status`/`resolution_date` schema + RESOLVED ✓/✕ cards + a "Resolved" cluster + hardened `render_question_card` (no more KeyError on missing fields). Surgical CSS only.
- **Day-108 briefing** seeded (`agent/briefing-2026-06-15.json`, EN+FA, 9 cited events + 5 movers).
- **Softened false-cadence strings** (cron is disabled → "Updated as events warrant").
- **Restored `/legacy`** chart data (`legacy/war-data.json` from the .bak).
- **Reusable scripts**: `agent/apply_2026-06-15_update.py` (ruamel comment-preserving updater), `agent/build_briefing_2026-06-15.py`, `agent/audit-update-workflow.mjs` (the intel+audit workflow).

**Cron is now DISABLED** (`trig_01UD1sGTg9SHWMN2HjY7AiBa`) — updates are manual/on-demand.

- Live: https://iran-war-dashboard-murex.vercel.app/
- Public stripped: https://iran-war-public.vercel.app/
- Spec: `docs/superpowers/specs/2026-05-15-morning-briefing-design.md`
- **91/91 tests green**; public bundle leak-clean (English + Persian).
- **Operator follow-ups**: (1) confirm the `murex` root deploy is access-gated — it serves the PRIVATE root (F-cards + full portfolio.yaml) by design; (2) the June-19 signing would resolve A1 YES; (3) re-enable the cron if desired.

## What shipped this session (5 commits)

| Commit | What |
|---|---|
| `bca82b1` | Design spec |
| `d588066` | Morning Brief code (`fetch_news.py`, `render.render_morning_brief` + helpers, CSS, cron rewrite, 33 new tests) |
| `c2108c9` | Seeded `agent/briefing-2026-05-15.json` (Day 77 — Araghchi New Delhi diplomacy, UK sanctions) |
| `da0ea40` | Vercel build fix: removed broken `apply-d74.py` buildCommand |
| `203cc4c` | UI: 2-col grid at ≥1100px (read left, movers+events right) |

## Architecture

```
RSS (~15 free feeds) + WebSearch (4–6 queries)
  → logs/events/{TODAY}.json
  → agent/briefing-{TODAY}.json  (EN + FA in one LLM pass)
  → scripts/render.py --public
  → index.html / fa.html / public.html / public.fa.html
  → git push origin main  →  Vercel auto-deploy
```

Five safety rails in `render_morning_brief`:
1. Events without URL dropped
2. Mover `why` fact-checked against events (ungrounded → fallback string)
3. `public_safe: false` items stripped from public variants
4. Stale-warning state when JSON missing or >36h old
5. `briefing_partial: true` notice on budget abort

## Cron schedule

- **Routine**: `trig_01UD1sGTg9SHWMN2HjY7AiBa` — enabled, `0 11 * * *` (7am EDT)
- Next fire: 2026-05-16 ~07:04 ET
- **DST note**: cron is UTC-static. Flip to `0 12 * * *` when DST ends Nov 2, 2026
- Manage: https://claude.ai/code/routines/trig_01UD1sGTg9SHWMN2HjY7AiBa

## Open follow-ons

1. **Delete 4 duplicate routines** at https://claude.ai/code/routines (API can't delete):
   - `trig_01F4TiDVqmFbCR6whwUvTM53` (Iran War Dashboard Daily Refresh)
   - `trig_015QwrJK7Uebvg43ekLdqBCG` (iran-war-dashboard-daily)
   - `trig_014xG12iaEeWr9LYkvfXaRc3` (Iran War Dashboard — Evening Update)
   - `trig_01Xrn2c5oXQCmq5gHWfKepJT` (Iran War Dashboard — Morning Update)
   - Optional: `trig_01VhBRTJ8Abm8ZbGPYYDvzqb`, `trig_01Ef9AyEUg3yJfm4dj6gQAaP` (fired one-shots)
2. **`/legacy` chart** is degraded — `legacy/war-data.json` is a 12-byte PLACEHOLDER. The recovery script chain broke after the rebase. Fix path: commit the real war-data.json into the repo, or accept degraded /legacy. Deprioritized.

## Quick resume commands

```bash
cd ~/Desktop/iran-war-dashboard
git log --oneline -8                          # see recent ship history
source .venv/bin/activate
python -m pytest -q                           # expect 85 passed
python scripts/fetch_news.py                  # manual RSS pull if needed
python scripts/render.py --public             # re-render all 4 variants
```

## Key code locations

- `scripts/render.py:854` (`# Morning Brief —`) — render block + helpers
- `dashboard.css` (search `Morning Brief —`) — ~300 lines of CSS, 2-col grid at ≥1100px
- `scripts/fetch_news.py` — RSS pull, 24h filter, fuzzy-title dedup, relevance keywords
- `agent/cron-prompt.phase-0.md` — 10-step procedure spec
- `agent/briefing-2026-05-15.json` — today's seed briefing (model for the schema)

## Hard rules (persist across sessions)

- Keep Inter / system font. **No sweeping CSS passes** — surgical only.
- Persian uses Vazirmatn webfont, Persian numerals, RTL grid auto-flips.
- Never modify `portfolio.yaml` from the cron (Phase 0 = operator-only).
- Never compose `agent/memory.md` by hand (use `scripts/refresh_memory.py`).
- F-question / Iranfarhang / Kipa / AMAG / Berman references must have `public_safe: false`.
- Direct push to main (no draft-PR / proposed-signals branch).
- If the cron's procedure conflicts with the spec at `agent/cron-prompt.phase-0.md`, the spec wins.
