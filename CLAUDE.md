# Iran War Dashboard

## Current State
- v2 predictive rebuild + Morning Brief + deal-era refresh shipped
- 34 questions (A1–A6, B1–B6, C1–C4, D1–D4, E1–E2, F1–F12); 9 resolved, 25 open
- Deal-tracker component + resolution rendering (RESOLVED ✓/✕ cards) live
- Last data: **D108 (2026-06-15)** — June 14 US-Iran framework MOU (signs June 19, Switzerland; 60-day window); US naval blockade lifted; Strait of Hormuz reopening toll-free (physical recovery gated by mine-clearing). Ali Khamenei **killed Feb 28**, son **Mojtaba** Supreme Leader since March 8 (this corrected a counterfactual the data had carried). Brent ~$84, rial ~1.62M, US gas ~$4.07.
- Daily refresh cron (`trig_01UD1sGTg9SHWMN2HjY7AiBa`) is **DISABLED** — updates are now manual/on-demand. Chrome strings no longer promise a daily cadence.

## Repo
- `origin` → `git@github.com:omoji-personal/iran-war-dashboard.git` (SSH, push works)
- Two dashboards, both auto-deploy on `git push origin main`:
  - `iran-war-dashboard-murex.vercel.app` — full (index.html, with business sections)
  - `iran-war-public.vercel.app` — stripped (build command: `python3 scripts/build-public.py`, output: `public-dist/`)
- Manual public deploy (fallback): `./deploy-public.sh`

## Session Context
<!-- Claude Code: update this section at end of each session -->
_Last updated: 2026-06-15 — Full audit + deal-era update (cited intel sweep: 7 intel agents + repo audit + 4 verifiers, all real sources). Re-rated all 32 questions, resolved 9 (B1/B2/B3/B5/C1/C3/D2/D3 YES, A5 NO), added A6 (permanent settlement) + B6 (ceasefire holds), rewrote frame + base_case (EN+FA), added deal-tracker metadata + render component, added resolution rendering (surgical render.py + CSS), seeded Day-108 briefing. Restored `/legacy` chart (legacy/war-data.json from .bak). 91 tests green; public bundle leak-clean. One-shot updater: `agent/apply_2026-06-15_update.py`; briefing builder: `agent/build_briefing_2026-06-15.py`; intel workflow: `agent/audit-update-workflow.mjs`. NOTE for operator: the `murex` root deploy serves the PRIVATE root (index.html + portfolio.yaml with family-business F-cards) by design — confirm that Vercel project is access-gated; the public surface is the separate stripped `iran-war-public`._
