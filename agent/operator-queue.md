# Operator Queue — Tier-C decisions awaiting operator approval

Format per item:
```
## YYYY-MM-DD — {{question_id_or_topic}} — {{decision_required}}
{{context}}
{{agent_recommendation}}
{{open_issue}}
```

---

## 2026-05-03 — C1 RESOLUTION — Khamenei (Ali) killed Feb 28; mark C1 = RESOLVED YES

**Priority: HIGH — affects successor question chain**

Web sources (Washington Times, CNBC, CBS News, Al Jazeera, Fox News) confirm:
- Ali Khamenei killed in US-Israel strikes on Feb 28, 2026.
- Mojtaba Khamenei confirmed issuing Supreme Leader statements by Apr 30, 2026.

**Agent recommendation:** Operator should:
1. Set `C1.current_probability = 1.0` (resolved YES) in portfolio.yaml
2. Set `C1.resolution_date = 2026-02-28`
3. Add note: `resolved: YES — Ali Khamenei killed Feb 28 per multiple Tier-1 sources`
4. Review C1 successors_on_resolve_yes questions and queue for addition if not yet in portfolio

**Note:** Agent has HUMILITY FLAG on C1 because of initial uncertainty about whether
Ali Khamenei survived. Web search on 2026-05-03 cron #1 confirms resolution.

---

## 2026-05-03 — C3 RESOLUTION — Mojtaba designated heir; mark C3 = RESOLVED YES

**Priority: HIGH — successor question chain**

Web sources confirm Mojtaba Khamenei is now operating as Supreme Leader
(per Washington Times headline "Iran's Ayatollah Mojtaba Khamenei says Tehran protect nuclear missile").

**Agent recommendation:** Operator should:
1. Set `C3.current_probability = 1.0` (resolved YES) in portfolio.yaml
2. Set `C3.resolution_date: 2026-02-28` (or nearest confirmed date of succession)
3. Add note: `resolved: YES — Mojtaba confirmed Supreme Leader by Apr 30 per multiple sources`

---

## 2026-05-03 — A1 SIGNAL DIVERGENCE — our 18% vs Polymarket 56% (by 2027)

**Priority: MEDIUM**

Polymarket `us-iran-nuclear-deal-before-2027` at 56% ($120K liquidity).
Manifold `US-Iran nuclear deal by end of June?` at 30% (148 traders).
Our A1 (framework deal by Sep 30, 2026) at 18%.

Date differences explain some gap (our Sep-30 horizon vs PM Dec-31 horizon).
But ~38pp divergence is substantial. Active negotiations with 14-point proposal in motion.

**Agent recommendation:** Operator re-examine A1 given market signals. Consider if 18% still
correct or if negotiations trajectory warrants upward revision. Agent cannot update (Phase 0).

---

## 2026-05-03 — A2 SIGNAL DIVERGENCE — Hormuz Polymarket 51% by June vs our 25% by Dec

**Priority: MEDIUM**

Polymarket `strait-of-hormuz-traffic-returns-to-normal-by-end-of-june`: 51% ($151K liq).
Our A2 horizon is Dec 31, 2026 — later than June, so our probability should be ≥ 51%.
Current A2 at 25% appears low relative to market signal.

**Agent recommendation:** Operator reconsider A2 upward, potentially to 45-55% range,
unless there's a specific reason to believe the Dec-31 outcome is less likely than Jun-30.

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
- Operator has approved ~$4,000/year operating budget

**Agent recommendation:** transition Phase 0 → Phase 1 within 14d of MVP launch
to avoid the model staying in operator-driven mode indefinitely.
