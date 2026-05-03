#!/usr/bin/env python3
"""D48 EVENING addendum (Apr 16, 2026, 16:00 ET).

Builds on the morning D48 commit (c59b0ae) which added Munir-Tehran +
'in principle' extension narrative across the standard per-day arrays
but missed:
  - hormuzTransit Apr 16
  - ceasefireViolations Apr 15 + Apr 16
  - ceasefireNegotiations Apr 15 + Apr 16
  - ceasefireEconomicRecovery Apr 15 + Apr 16

Also augments dailyRows[Apr 16] with afternoon developments the
morning commit could not have known:
  - Trump 5PM ET announcement of 10-day Israel-Lebanon ceasefire
  - Gen. Caine widening blockade scope WORLDWIDE
  - Hegseth 'ready to restart combat' threat
  - 14 ships turned away (vs 10+ in morning)
"""

import json
from pathlib import Path

ROOT = Path(__file__).parent.parent
DATA = ROOT / "war-data.json"

with open(DATA) as f:
    d = json.load(f)

# ---- Sanity ----
assert d["dailyRows"][-1]["date"] == "Apr 16", "expected dailyRows last Apr 16"
assert d["hormuzTransit"]["labels"][-1] == "Apr 15", "expected hormuz still Apr 15 (morning gap)"
assert d["ceasefireViolations"][-1]["day"] == "Apr 14", "expected violations gap"
assert d["ceasefireNegotiations"][-1]["date"] == "Apr 14", "expected negotiations gap"
assert d["ceasefireEconomicRecovery"]["labels"][-1] == "Apr 14", "expected recovery gap"

# ---- 1. hormuzTransit: add Apr 16 ----
d["hormuzTransit"]["labels"].append("Apr 16")
d["hormuzTransit"]["vessels"].append(6)  # CNBC "few tankers"; trending up vs blockade

# ---- 2. predictive vectors: bump last entry on Lebanon-ceasefire + Caine-worldwide ----
pv = d["predictive"]["vectors"]
pv["economicPain"][-1] = 8.0              # 7.7 -> 8.0 (worldwide blockade scope)
pv["diplomaticMomentum"][-1] = 7.5        # 6.5 -> 7.5 (Lebanon ceasefire = breakthrough)
pv["usPoliticalSustainability"][-1] = 4.0 # 3.5 -> 4.0 (Lebanon ceasefire = political win)
pv["escalationCeilingDistance"][-1] = 4.0 # 3.5 -> 4.0 (de-escalation track active)

# ---- 3. dailyRows[Apr 16]: append EVE UPDATE sections ----
row = d["dailyRows"][-1]
eve_primary = (
    "  ||  D48 EVE UPDATE (Apr 16 16:00 ET): TRUMP ANNOUNCED 10-DAY ISRAEL-LEBANON "
    "CEASEFIRE EFFECTIVE 5PM ET. Hezbollah said it would abide if Israeli attacks stop; "
    "Israel retains self-defense right; can be extended by mutual consent. Iran Speaker "
    "Ghalibaf: Lebanon ceasefire 'as important as' Iran's. Gen. Dan Caine (Joint Chiefs) "
    "WIDENED blockade scope WORLDWIDE — US forces will stop any vessel 'tied to Tehran "
    "or carrying supplies' (weapons, oil, metals, electronics) anywhere globally, including "
    "Pacific operations against ships that left before blockade began. 14 ships turned "
    "away cumulative (was 10+); zero boardings. Hegseth: US 'ready to restart combat' if "
    "no deal. Iran armed forces threatened to block Persian Gulf + Sea of Oman + Red Sea. "
    "POLYMARKET DRAMATIC SHIFT: ceasefire-extended-by-Apr-21 = 78% (vs 18% pre-blockade); "
    "holds-Apr-30 = 68%; holds-May-31 = 79%; conflict-ends-Dec-31 = 97%. Lebanon dead 2,100+. "
    "Internet 1,120+ hrs ($1.8B cost)."
)
row["primary"] = row["primary"] + eve_primary

eve_cost = (
    "  ||  EVE: WTI rebounded intraday on US crude inventory draw (-9.13M bbl vs +154K "
    "expected). Iran rial -8% since war (-60% since 2025), inflation 47%/food 105%, payroll "
    "concerns. Blockade widened worldwide = max-pressure economic isolation; 14 ships now."
)
row["cost"] = row["cost"] + eve_cost

eve_assessment = (
    "  ||  EVE REASSESSMENT: Israel-Lebanon ceasefire 5PM ET = THIRD positive on top of "
    "Munir-Tehran + 'in principle' extension. Removes the second-front pressure that was "
    "breaking original Iran ceasefire. Polymarket extension odds 78% confirms market "
    "pricing in deal. Counter-pressure: Caine worldwide blockade + Hegseth combat threat "
    "= calibrated stick paired with carrots. The bet: squeeze Iran to terms in next 5 "
    "days before Apr 21 expiry, OR formalize the AP-reported 'in principle' extension. "
    "Convergence ~6.5 (from 5.7). Deal probability now plausibly leading collapse for "
    "first time."
)
row["assessment"] = row["assessment"] + eve_assessment

# ---- 4. ceasefireViolations: BACKFILL Apr 15 + ADD Apr 16 ----
d["ceasefireViolations"].append({
    "day": "Apr 15",
    "cfDay": 8,
    "incidents": [
        {
            "type": "blockade",
            "severity": 8,
            "actor": "US Navy",
            "target": "Iranian ports",
            "description": "Blockade Day 2 fully implemented (CENTCOM). 13 ships turned away cumulative. No boardings. Iran FM: 'piracy.' Trump Fox Business: 'close to over, very close to over.'",
            "description_fa": "محاصره روز دوم به طور کامل اجرا شد (سنتکام). ۱۳ کشتی بازگردانده شد. ترامپ: «بسیار نزدیک به پایان است.»",
            "withinScope": "yes"
        },
        {
            "type": "accusation",
            "severity": 4,
            "actor": "Iran",
            "target": "US",
            "description": "Iran spokeswoman Mohajerani: $270B war compensation demand. 5-pt counter: end attacks + security guarantees + $270B reparations + Hormuz sovereignty + intl recognition.",
            "description_fa": "سخنگوی ایران مهاجرانی: مطالبه ۲۷۰ میلیارد دلار غرامت جنگ. شرایط ۵ ماده‌ای ایران.",
            "withinScope": "no"
        },
        {
            "type": "accusation",
            "severity": 4,
            "actor": "Israel",
            "target": "Lebanon",
            "description": "Israel-Hezbollah strikes continue. Lebanon dead 2,100+. UN experts condemn 'unprecedented' Israeli bombing.",
            "description_fa": "حملات اسرائیل-حزب‌الله ادامه دارد. لبنان بیش از ۲۱۰۰ کشته. کارشناسان سازمان ملل بمباران را «بی‌سابقه» محکوم کردند.",
            "withinScope": "disputed"
        }
    ],
    "totalCount": 3,
    "maxSeverity": 8
})

d["ceasefireViolations"].append({
    "day": "Apr 16",
    "cfDay": 9,
    "incidents": [
        {
            "type": "blockade",
            "severity": 9,
            "actor": "US Joint Chiefs (Caine)",
            "target": "All Iran-linked shipping worldwide",
            "description": "Gen. Caine WIDENED blockade scope WORLDWIDE — US forces will stop any vessel 'tied to Tehran or carrying supplies' (weapons, oil, metals, electronics) anywhere globally, including Pacific. 14 ships turned away cumulative. Hegseth: 'ready to restart combat' if no deal.",
            "description_fa": "ژنرال کین دامنه محاصره را در سراسر جهان گسترش داد — هر کشتی متصل به تهران در هر نقطه از جهان متوقف می‌شود. هگست: آماده از سرگیری جنگ.",
            "withinScope": "yes"
        },
        {
            "type": "threat",
            "severity": 5,
            "actor": "Iran armed forces",
            "target": "Persian Gulf + Sea of Oman + Red Sea",
            "description": "Iran armed forces threatened to block Persian Gulf, Sea of Oman, AND Red Sea shipping in retaliation for worldwide blockade. Rhetorical — 10-day zero-attack streak intact.",
            "description_fa": "نیروهای مسلح ایران تهدید به مسدود کردن خلیج فارس، دریای عمان و دریای سرخ کردند. ۱۰ روز بدون حمله.",
            "withinScope": "no"
        }
    ],
    "totalCount": 2,
    "maxSeverity": 9
})

# ---- 5. ceasefireNegotiations: BACKFILL Apr 15 + ADD Apr 16 ----
d["ceasefireNegotiations"].append({
    "date": "Apr 15",
    "cfDay": 8,
    "event": "Trump 'close to over' (Fox Business) + Iran $270B reparations counter + business internet partial",
    "event_fa": "ترامپ «بسیار نزدیک به پایان» + ضدپیشنهاد ۲۷۰ میلیارد دلار ایران + اینترنت تجاری جزئی",
    "participants": ["Trump", "Iran spokeswoman Mohajerani", "Iran science ministry"],
    "outcome": "signaling",
    "significance": 7,
    "keyGap": "$270B reparations + Hormuz sovereignty are biggest gaps; nuclear 5-yr vs 20-yr enrichment freeze still unresolved."
})

d["ceasefireNegotiations"].append({
    "date": "Apr 16",
    "cfDay": 9,
    "event": "Munir (Pakistan army chief) in Tehran with US proposal; Trump announces 10-day Israel-Lebanon ceasefire 5PM ET; AP: 'in principle' agreement to extend Iran ceasefire beyond Apr 21",
    "event_fa": "منیر (رئیس ارتش پاکستان) در تهران با پیشنهاد آمریکا؛ ترامپ آتش‌بس ۱۰ روزه اسرائیل-لبنان از ۵ بعدازظهر؛ توافق «در اصول» برای تمدید آتش‌بس ایران",
    "participants": ["Trump", "Pakistan army chief Munir", "Iranian officials Tehran", "Hezbollah", "Israel", "Lebanon", "Sec. Rubio", "Sec. Hegseth", "Press Sec Leavitt"],
    "outcome": "breakthrough",
    "significance": 9,
    "keyGap": "'In principle' extension not formally agreed (US official to CNBC). Nuclear gap: 5-yr vs 20-yr enrichment freeze, ~440kg HEU stockpile. Hegseth 'restart combat' threat is paired stick. 5 days to Apr 21 expiry."
})

# ---- 6. ceasefireEconomicRecovery: BACKFILL Apr 15 + ADD Apr 16 ----
recov = d["ceasefireEconomicRecovery"]
recov["labels"].extend(["Apr 15", "Apr 16"])
recov["hormuzDaily"].extend([4, 6])
recov["brentDaily"].extend([95.72, 94.89])
recov["shipsStranded"].extend([825, 830])
recov["note"] = (
    "Blockade WIDENED worldwide D48 (Gen. Caine — any Iran-linked vessel anywhere). "
    "Hormuz still ~6 vessels (90% below pre-war 135). Brent fell to $94.89 on Lebanon "
    "ceasefire + Munir Tehran + 'in principle' extension hopes, offsetting blockade "
    "escalation. Israel-Lebanon 10-day truce 5PM ET D48 = removes proxy-front pressure. "
    "Polymarket ceasefire-extension odds 78% (from 18%) = markets pricing in deal."
)

# ---- 7. meta ----
d["meta"]["lastUpdated"] = "2026-04-16T16:00:00-04:00"
eve_note = (
    "D48 EVE UPDATE (Apr 16 16:00 ET): ISRAEL-LEBANON CEASEFIRE 5PM ET + BLOCKADE "
    "WIDENED WORLDWIDE + POLYMARKET 78% EXTENSION. (1) TRUMP ANNOUNCED 10-DAY "
    "ISRAEL-LEBANON CEASEFIRE effective 5PM ET — Hezbollah accepts if Israeli strikes "
    "stop; Israel retains self-defense; extendable by mutual consent. Iran Speaker "
    "Ghalibaf: 'as important as' Iran ceasefire. (2) BLOCKADE WIDENED WORLDWIDE — "
    "Gen. Dan Caine (Joint Chiefs): US forces will stop any Iran-linked vessel ANYWHERE "
    "globally (weapons, oil, metals, electronics), including Pacific operations. 14 ships "
    "turned away cumulative; zero boardings. (3) WHITE HOUSE: Leavitt 'productive and "
    "ongoing'; Trump talks 'probably, maybe over the weekend'; Hegseth 'ready to restart "
    "combat' if no deal. (4) IRAN: armed forces threatened Persian Gulf + Sea of Oman + "
    "Red Sea blockade in retaliation; rial -8% since war (-60% since 2025); inflation 47%, "
    "food 105%; internet $1.8B cost. (5) POLYMARKET DRAMATIC SHIFT: ceasefire-extended-by-"
    "Apr-21 = 78%, holds-Apr-30 = 68%, holds-May-31 = 79%, holds-Dec-31 = 98%, conflict-"
    "ends-Dec-31 = 97%, Trump-announces-end-by-Jun-30 = 85%. Brent $94.89 (-0.04%), WTI "
    "intraday volatility $90.72-$94.62 on US crude inventory draw. Hormuz ~6 vessels. "
    "10-day Iran zero-attack streak. Lebanon dead 2,100+. Ceasefire Day 10. 5 days to "
    "Apr 21 expiry. ALSO: backfilled Apr 15 + Apr 16 entries into ceasefireViolations / "
    "Negotiations / EconomicRecovery (morning commit only updated standard per-day arrays)."
)
d["meta"]["notes"].insert(0, eve_note)

with open(DATA, 'w') as f:
    json.dump(d, f, indent=2, ensure_ascii=False)
    f.write("\n")

print("OK — D48 EVE addendum written.")
print(f"  hormuzTransit: {len(d['hormuzTransit']['labels'])} (last {d['hormuzTransit']['labels'][-1]} vessels {d['hormuzTransit']['vessels'][-1]})")
print(f"  ceasefireViolations: {len(d['ceasefireViolations'])} (last {d['ceasefireViolations'][-1]['day']} cfDay {d['ceasefireViolations'][-1]['cfDay']})")
print(f"  ceasefireNegotiations: {len(d['ceasefireNegotiations'])} (last {d['ceasefireNegotiations'][-1]['date']})")
print(f"  ceasefireEconomicRecovery: {len(recov['labels'])} (last {recov['labels'][-1]})")
print(f"  predictive vectors[-1]: econPain={pv['economicPain'][-1]}, diplo={pv['diplomaticMomentum'][-1]}, usPol={pv['usPoliticalSustainability'][-1]}, escalDist={pv['escalationCeilingDistance'][-1]}")
print(f"  dailyRows[Apr 16] primary length: {len(row['primary'])} chars")
