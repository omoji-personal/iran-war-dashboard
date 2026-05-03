# Operator Queue — Tier-C decisions awaiting operator approval

Format per item:
```
## YYYY-MM-DD — {{question_id_or_topic}} — {{decision_required}}
{{context}}
{{agent_recommendation}}
{{open_issue}}
```

---

## 2026-05-03 — F1-F12 portfolio confirmation — confirm/edit family-business questions

The 12 F-class questions (F1-F6 Iranfarhang, F7-F12 Kipa) were generated from
deep-research agents on 2026-05-03 reviewing both business folders. They are
provisional and need your confirm/edit/replace pass.

**Agent recommendation:** keep all 12 as-is for first 30d; revise based on which
prove decision-useful vs noisy.

**Open issue:** which (if any) should be cut, modified, or added.

---

## 2026-05-03 — Phase 0 → Phase 1 transition trigger

Phase 0 MVP ships today with manual probabilities for all 32 questions.
Phase 1 (agent loop with 3-tier autonomy + reference-class registry seed)
upgrades when:
- Operator has loaded the new homepage at least once
- Operator has confirmed F1-F12 portfolio (above)

**Agent recommendation:** transition Phase 0 → Phase 1 within 14d of MVP launch
to avoid the model staying in operator-driven mode indefinitely.

## 2026-05-03 — Free-only operating constraint (CONFIRMED by user)

User specified: agent runs under existing Claude subscription. RemoteTrigger
cron + free public APIs only. **Total operating cost: $0/year.**

What's IN (free):
- Polymarket Gamma API (no auth)
- Manifold REST API (no auth)
- ConflictForecast.org (Phase 2+; public dashboard)
- bonbast.com (Phase 2+ via careful scrape; public)
- TGJU.org (Phase 2+ via public scrape)
- ACLED Iran Crisis Live (Phase 2+ via public CSV)
- News sites (Reuters/AP/Axios/CNN — public, fair-use scrape)
- GDELT GKG (Phase 2+ via free BigQuery public dataset)
- Cron via RemoteTrigger (subscription-included)

What's OUT (paid — explicitly out-of-scope unless user opts in):
- Kpler (oil tracking, paid)
- Spire (AIS data, paid)
- Windward (AIS anomaly detection, paid)
- Bloomberg (market data, paid)
- Janes / IISS (military intel, paid)
- Stratfor / Crisis24 / Eurasia Group / Verisk Maplecroft (paid)

What requires manual user opt-in (free-with-account):
- Metaculus API token (free; user creates account if desired; agent skips gracefully without it)
- Telegram channel monitoring (free Telethon; user provides API_ID + API_HASH if desired)

If a future Phase identifies a specific bottleneck that paid feeds would solve,
agent surfaces in operator-queue with cost + value justification. User decides.
