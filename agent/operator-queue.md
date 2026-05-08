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

## 2026-05-08 — 🔴 CRITICAL — C1 resolution: Khamenei death

Multiple Tier-1 sources confirm Ali Khamenei was killed in strikes on 2026-02-28.
Portfolio still shows C1 at 8% (*very unlikely*). C1 appears to have RESOLVED YES.

**Agent recommendation**: Mark C1 resolved=YES, date=2026-02-28. Evaluate successors:
- "Mojtaba succeeds within 90d?" → YES (already head of state as of May 2026)
- "Faction war (rival public claim) within 30d?" → assess
- "IRGC publicly endorses successor within 14d?" → assess
- "Iran framework-deal probability shifts >20pp within 30d?" → likely YES

Sources: Wikipedia 2026 Iran war ceasefire; Euronews 2026-05-07; PBS NewsHour; Iran International.

---

## 2026-05-08 — 🔴 CRITICAL — B1 + B2 resolution: US-Iran fire exchange Day 70

On 2026-05-08 (Day 70), US and Iran exchanged fire in Hormuz:
- CENTCOM acknowledged strikes on Iranian coastal areas (Qeshm Island, Bandar Khamir, Sirik) → B1 resolution criterion may be met.
- Iran launched missiles/drones/small boats against 3 US Navy destroyers → B2 resolution criterion may be met.
Trump stated ceasefire remains in effect. Both B1 and B2 require operator confirmation before being marked resolved.

**Agent recommendation**: Review and resolve B1 and B2 YES if criteria satisfied. Evaluate successors.

Sources: Al Jazeera Day 70; NBC News; CNN Live; CNBC May 8.

---

## 2026-05-08 — 🟡 D3 threshold crossed (Day 1): AAA gas at $4.558

AAA national average hit $4.558 on 2026-05-07 — Day 1 above the $4.50 resolution threshold.
D3 requires sustained 7+ consecutive days. Monitor daily.

**Agent recommendation**: Update D3 probability from 42% to ~70–80% given:
(a) threshold already crossed; (b) Brent ~$100 with active Hormuz conflict;
(c) AAA rising $0.25/week. Revisit after 7d to confirm resolution.

Source: AAA Newsroom 2026-05-08; Fox Business.

---

## 2026-05-08 — 🟡 A1 Polymarket divergence: 22% portfolio vs 61–74% market

Polymarket "US-Iran deal before 2027": 61% ($119k liquidity).
Polymarket "deal by Dec 31 2026": 74% ($184k liquidity).
Portfolio A1: 22%. Gap = 39–52pp.

A1 criterion is stricter than "deal" — requires joint readout + written framework + mediator.
Discount warranted but 22% vs 74% likely overcorrects.

**Agent recommendation**: Update A1 to 35–45%. Discount from market for strict criterion,
with additional downside from today's fire-exchange event.

---

## 2026-05-08 — 🟡 C3 framing review: Mojtaba is Supreme Leader, not heir-apparent

C3 asks "Mojtaba Khamenei publicly designated heir-apparent by Assembly of Experts."
He IS now Supreme Leader — the question framing is potentially moot or resolved.

**Agent recommendation**: Assess C3 resolution (YES if formal succession process met criterion)
or void/replace with successor question (e.g., "Mojtaba publicly appears in public by Dec 31?").

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
