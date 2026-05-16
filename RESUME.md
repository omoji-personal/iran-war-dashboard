# Resume — Iran War Dashboard Morning Brief

**Last session**: 2026-05-15 (shipped Morning Brief feature end-to-end).

## TL;DR

The Morning Brief is **shipped and live**. The cron is **scheduled and enabled** at 7am EDT. Nothing is half-done.

- Live: https://iran-war-dashboard-murex.vercel.app/
- Public stripped: https://iran-war-public.vercel.app/
- Spec: `docs/superpowers/specs/2026-05-15-morning-briefing-design.md`
- Cron procedure: `agent/cron-prompt.phase-0.md`
- 85/85 tests green

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
