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

## 2026-05-04 — C1 resolution candidate — Ali Khamenei death confirmation

Multiple Tier-1 sources (Al Jazeera, Iran International, Times of Israel, NPR) confirm Ali Khamenei
died ~March 1, 2026; Mojtaba Khamenei became Supreme Leader March 12, 2026.

C1 question: "Khamenei dies or is publicly removed from office by 2026-12-31"

**Resolution appears: YES** (death reported March 1, 2026)

But C1 was set May 3, 2026 (after reported death) at 8% — possibly operator is tracking Mojtaba as
the ongoing "Khamenei" subject, or resolution has not yet been applied.

**Operator action required:**
1. Confirm C1 resolves YES with resolution_date 2026-03-01 in portfolio.yaml; OR
2. Confirm that C1 is intentionally tracking Mojtaba Khamenei going forward (amend question text).
Also review A5 notes for accuracy (references pre-death Khamenei statements).

---

## 2026-05-04 — C3 resolution candidate — Mojtaba Khamenei leadership status

C3 question: "Mojtaba Khamenei publicly designated heir-apparent by Assembly of Experts by 2026-12-31"

If C1 resolves YES, Mojtaba was elevated directly to Supreme Leader (not heir-apparent). The C3
resolution criterion may have been met in spirit (public designation by AoE), but the question text
says "heir-apparent" not "supreme leader."

**Agent recommendation:** Resolve C3 YES (elevation by AoE is a superset of designation as heir),
and replace with new question: "Will Mojtaba Khamenei consolidate full IRGC/bazaari loyalty by Dec 31, 2026?"

**Operator action required:** Confirm C3 resolution + decide on successor question.

---

## 2026-05-04 — D3 approaching $4.50 threshold — monitor

D3 question: "US gas national average (AAA) crosses $4.50 sustained 7+d by 2026-09-30"

Current AAA: $4.457 (May 4). Gap: $0.043. Trend: +$0.34/week.

**Operator action:** No portfolio change yet. Monitor daily. Alert when sustained 7+ days above $4.50.

---

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
