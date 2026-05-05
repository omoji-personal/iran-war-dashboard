# Operator Queue — Tier-C decisions awaiting operator approval

Format per item:
```
## YYYY-MM-DD — {{question_id_or_topic}} — {{decision_required}}
{{context}}
{{agent_recommendation}}
{{open_issue}}
```

---

## 2026-05-05 — C1 — URGENT: Resolve YES (Ali Khamenei killed 2026-02-28)

Washington Post, CNN, Al Jazeera all confirm Ali Khamenei was killed in the Feb 28 US-Israel strikes.
Portfolio still shows C1 at 8% (incorrect — written with bad initial data).

**Agent recommendation:** Resolve C1 = YES (date: 2026-02-28). Activate successor questions.
Check whether "Iran framework-deal probability shifts >20pp within 30d of C1" — it should, given Mojtaba now leads.

**Open issue:** Confirm the resolution date. Also: was the successor process faction-contested?

---

## 2026-05-05 — C3 — URGENT: Resolve YES (Mojtaba named Supreme Leader 2026-03-09)

Mojtaba Khamenei was elected Supreme Leader by Assembly of Experts (election March 3–8, announced March 9).
Resolution criterion exceeded (he was elected outright, not merely named heir-apparent).

**Agent recommendation:** Resolve C3 = YES (date: 2026-03-09). This also requires re-reading A5 (now applies to Mojtaba, not Ali).

**Open issue:** Does the question "Mojtaba designated heir-apparent" count even though he became Supreme Leader directly? Agent says YES — stronger resolution than required.

---

## 2026-05-05 — 14 probability moves recommended — operator to apply or decline

See `logs/probability-changes/2026-05-05.md` for the full recommended-move table.
Key highest-confidence moves:
- D3: 50% → 68% (gas $4.483, one incident away from $4.50 trigger)
- A3: 12% → 35% (Project Freedom = Earnest Will-style escort in operation)
- B2: 28% → 42% (Iran actively fired on US+SK ships in Hormuz)

**Agent recommendation:** Apply all 14 moves at next operator session.

**Open issue:** Do you want to continue using old portfolio.yaml probabilities or let cron surface recommended moves each tick for manual application?

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

---

## 2026-05-05 — C1/C3 label + resolution review (TICK-GENERATED)

Web research (tick 2026-05-05) confirms Ali Khamenei was killed ~2026-03-01 and Mojtaba
Khamenei became supreme leader ~2026-03-12. Portfolio questions C1/C3 may need update:

- **C1** ("Khamenei dies or is publicly removed from office" at 8%): If this referred to ALI
  Khamenei, it is already resolved YES and should be archived. If it refers to MOJTABA
  Khamenei (current leader), the question text should be updated to say "Mojtaba Khamenei."
- **C3** ("Mojtaba Khamenei publicly designated heir-apparent by Assembly of Experts" at 6%):
  Mojtaba IS the supreme leader, not heir-apparent. This question may be moot or should be
  reframed (e.g., "Mojtaba Khamenei designates his own successor / heir-apparent").

**Agent recommendation:** Operator to clarify C1 scope and resolve/archive C3 as appropriate.

---

## 2026-05-05 — D3 threshold watch (TICK-GENERATED)

AAA national gas average is $4.457 as of 2026-05-05 — $0.043 below the D3 threshold of $4.50.
Brent crude spiked ~6% on 2026-05-04, suggesting further pump price pressure.
If AAA crosses $4.50 and holds 7+ days, D3 resolves YES. Current portfolio: 50%.

**Agent recommendation:** Monitor AAA daily for next 10 days. Operator may wish to increase D3
probability if Brent holds above $110. No auto-change in Phase 0.
