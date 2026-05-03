# Cron Workflow — R19 (audit 2026-05-03)

## Status today

The daily 0700 ET refresh cron (`trig_01UD1sGTg9SHWMN2HjY7AiBa`) writes
`signals.yaml` directly on `main` and pushes — Vercel auto-deploys with no
human gate. If the news fetcher hallucinates or mis-classifies an event, the
bad signal lands in production before any human sees it.

## Recommended workflow

The cron should write to a `proposed-signals` branch and open (or update) a
draft PR. A human approves the merge.

### Cron prompt update

When updating the cron prompt at `https://claude.ai/code/routines`, replace
the current "commit + push to main" instructions with:

```
1. Fetch news + update signals.yaml as before.
2. Run `python -m engine emit` to produce war-data.json.
3. Run `python -m pytest -q` and confirm 35/35 pass. STOP if tests fail.
4. Switch to a branch named `proposed-signals/YYYY-MM-DD`:
     git checkout -B proposed-signals/$(date -u +%Y-%m-%d)
5. Commit signals.yaml + war-data.json + signals_history/<date>.yaml + engine_history.json.
6. Push the branch:
     git push -u origin proposed-signals/$(date -u +%Y-%m-%d)
7. Create or update a draft PR via gh:
     gh pr create --draft \
       --title "Proposed signals — $(date -u +%Y-%m-%d)" \
       --body "Automated daily refresh. Review the signals.yaml diff + war-data.json deltas before merging." \
       || gh pr edit proposed-signals/$(date -u +%Y-%m-%d) \
            --body "Automated daily refresh. Review the signals.yaml diff before merging."
8. Do NOT merge. Human reviews and merges manually.
```

### Invariant check (alternative, lower-friction)

If the user prefers to keep auto-deploy on main, add a post-commit invariant
check:
- No single signal moved >0.30 in 24h without an explicit `change_reason`
  field added to the signals.yaml frontmatter for that day.
- If invariant fails, the cron commits to `proposed-signals/` instead of main
  and opens a PR with a "REVIEW REQUIRED — outlier change" tag.

This is enforced by `scripts/invariant_check.py` (TBD — not yet implemented).

## Migration

The user controls scheduling; I cannot change the cron prompt without their
approval. To apply this recommendation:

1. Visit https://claude.ai/code/routines/trig_01UD1sGTg9SHWMN2HjY7AiBa
2. Edit the prompt body to match the steps above.
3. Save.

The verification cron (`trig_01Ef9AyEUg3yJfm4dj6gQAaP` and similar one-shots)
do not need to change — they are read-only.
