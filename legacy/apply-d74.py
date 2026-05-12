#!/usr/bin/env python3
"""
Vercel build script: restore D74 war-data.json.
1. If war-data.json already has real content (> 1 KB), exit immediately.
2. Otherwise, call apply-d72.py to restore D72 state.
3. Verify 72 dailyRows, then append D73 (May 11) + D74 (May 12).
"""
import json, subprocess, sys

WAR_DATA = 'legacy/war-data.json'

current = open(WAR_DATA).read().strip()
if len(current) > 1000:
    print("apply-d74.py: war-data.json looks good, no action needed.")
    sys.exit(0)

print("apply-d74.py: PLACEHOLDER detected — running apply-d72.py to restore D72…")

r = subprocess.run([sys.executable, 'legacy/apply-d72.py'], capture_output=False)
if r.returncode != 0:
    print("apply-d74.py: ERROR: apply-d72.py failed", file=sys.stderr)
    sys.exit(1)

d = json.load(open(WAR_DATA))
n = len(d.get('dailyRows', []))
if n != 72:
    print(f"apply-d74.py: ERROR: expected 72 dailyRows after D72 restore, got {n}",
          file=sys.stderr)
    sys.exit(1)

print("apply-d74.py: D72 confirmed (72 rows). Applying D73 + D74 additions…")

# ── D73 (May 11) standard arrays (72 → 73) ────────────────────────────
d['dailySeries']['labels'].append('May 11')
d['dailySeries']['missiles'].append(0)
d['dailySeries']['drones'].append(0)
d['dailySeries']['confidence'].append(0.70)

d['pressure']['labels'].append('May 11')
d['pressure']['attrition'].append(11.2)
d['pressure']['cost'].append(9.5)

d['predictive']['vectors']['labels'].append('May 11')
d['predictive']['vectors']['militaryExhaustion'].append(7.1)
d['predictive']['vectors']['economicPain'].append(9.3)
d['predictive']['vectors']['diplomaticMomentum'].append(5.5)
d['predictive']['vectors']['usPoliticalSustainability'].append(3.5)
d['predictive']['vectors']['escalationCeilingDistance'].append(1.7)

d['additionalCharts']['geoSpreadLabels'].append('May 11')
d['additionalCharts']['countriesTargetedPerDay'].append(0)
d['additionalCharts']['missileDroneRatio'].append(0)
d['additionalCharts']['interceptRateLabels'].append('May 11')
d['additionalCharts']['interceptRate'].append(0.88)

# ── D73 pre-war-anchor arrays (73 → 74) ───────────────────────────
d['oil']['labels'].append('May 11')
d['oil']['brent'].append(103.50)
d['oil']['wti'].append(97.85)

d['hormuzTransit']['labels'].append('May 11')
d['hormuzTransit']['vessels'].append(3)

d['additionalCharts']['conflictIntensity'].append(4)

# ── D73 daily row ─────────────────────────────────────────────────
d['dailyRows'].append({
    "date": "May 11",
    "missiles": 0,
    "drones": 0,
    "primaryTargets": (
        "TRUMP: CEASEFIRE 'ON MASSIVE LIFE SUPPORT' — REJECTS IRAN COUNTER-PROPOSAL "
        "AS 'PIECE OF GARBAGE'; Iran demands Hormuz sovereignty, war compensation, "
        "end of blockade + sanctions relief — no nuclear concessions in phase 1; "
        "CENTCOM cumulative: 61 ships redirected (↑3 from D72), 4 tankers disabled; "
        "Turkish FM Fidan to visit Qatar May 12 for Iran war talks; "
        "Israeli strikes kill 4 in S. Lebanon; Hezbollah drone wounds 3 IDF soldiers; "
        "Brent +3% to ~$103.50 on 'life support' shock"
    ),
    "capability": (
        "Zero new Iranian offensive missile or drone strikes on D73. The dominant story: "
        "Trump publicly declared the ceasefire 'on massive life support' after calling "
        "Tehran's counterproposal 'the weakest' and a 'piece of garbage' — he said he "
        "'didn't even finish reading it.' Iran's response, submitted via Pakistani "
        "mediators, focused on ending the war on all fronts including Lebanon, demanded "
        "compensation for war damage, asserted Iranian sovereignty over the Strait of "
        "Hormuz, called for lifting the US naval blockade, lifting sanctions, and "
        "removing the ban on Iranian oil sales — crucially offering no nuclear "
        "concessions in the first phase, which US negotiators called a non-starter. "
        "CENTCOM blockade cumulative: 61 commercial ships redirected (up from 58 at "
        "D72), 4 Iranian tankers disabled. Lebanese health ministry: Israeli strikes "
        "killed 4 in southern Lebanon, wounded 8; two medics injured while responding. "
        "Three IDF soldiers lightly injured by Hezbollah explosive drone near Lebanese "
        "border. Turkish FM Hakan Fidan to visit Qatar on May 12 for Iran war talks "
        "focused on Gulf impact and Hormuz navigational safety. Internet Day 73: "
        "~1,752+ hours; Bloomberg estimates $2.6B+ cumulative digital-economy loss."
    ),
    "cost": (
        "Brent $103.50 est (+3%, 'life support' spike from $100.49 D72 close). "
        "WTI $97.85 est. Iran rial ~1,820,000/USD (est, continued depreciation). "
        "Internet Day 73 = 1,752+ hrs; $35–80M/day ongoing loss. "
        "Lebanon killed ~2,740+ (est). ~2,000 ships stranded in Gulf. "
        "HRANA ~3,720+ (est). US: 13 KIA, 365 WIA (est, no new update). "
        "Polymarket regime-falls-May-31: ~2%."
    ),
    "assessment": (
        "D73 marks the sharpest escalation in diplomatic tone since D66: Trump's "
        "'piece of garbage' rejection and 'massive life support' declaration is the "
        "most negative US signal since hostilities began. Context matters — Trump "
        "rhetoric at its most theatrical also precedes his most significant diplomatic "
        "event (Xi summit, now 3 days away), creating incentive for a last-minute "
        "Iranian concession or US face-saving pivot. Iran's counterproposal was "
        "deliberately maximalist: demanding all-front war end, Hormuz sovereignty, "
        "compensation, and sanctions relief before nuclear talks — a non-starter for "
        "Washington, which requires enrichment limits as a baseline. Oil's +3% spike "
        "reflects markets pricing extended Hormuz closure. CENTCOM's cumulative "
        "61-redirected scorecard signals the blockade is hardening, not softening. "
        "Turkish FM's Qatar visit is Ankara inserting itself as a mediator. "
        "Escalation probability: ~0.45 (highest since D66-67; 'life support' + no "
        "nuclear offer + summit pressure = volatile window). Deal probability: ~0.30 "
        "(dropped sharply; Xi summit is last clear catalyst but the gap is wide). "
        "Watch: Iranian revised MOU response before May 14; Xi-Trump Iran language; "
        "any US military signaling."
    )
})

# ── D74 (May 12) standard arrays (73 → 74) ────────────────────────────
d['dailySeries']['labels'].append('May 12')
d['dailySeries']['missiles'].append(0)
d['dailySeries']['drones'].append(0)
d['dailySeries']['confidence'].append(0.68)

d['pressure']['labels'].append('May 12')
d['pressure']['attrition'].append(11.4)
d['pressure']['cost'].append(9.6)

d['predictive']['vectors']['labels'].append('May 12')
d['predictive']['vectors']['militaryExhaustion'].append(7.2)
d['predictive']['vectors']['economicPain'].append(9.4)
d['predictive']['vectors']['diplomaticMomentum'].append(5.8)
d['predictive']['vectors']['usPoliticalSustainability'].append(3.4)
d['predictive']['vectors']['escalationCeilingDistance'].append(1.6)

d['additionalCharts']['geoSpreadLabels'].append('May 12')
d['additionalCharts']['countriesTargetedPerDay'].append(0)
d['additionalCharts']['missileDroneRatio'].append(0)
d['additionalCharts']['interceptRateLabels'].append('May 12')
d['additionalCharts']['interceptRate'].append(0.88)

# ── D74 pre-war-anchor arrays (74 → 75) ───────────────────────────
d['oil']['labels'].append('May 12')
d['oil']['brent'].append(104.97)
d['oil']['wti'].append(98.50)

d['hormuzTransit']['labels'].append('May 12')
d['hormuzTransit']['vessels'].append(3)

d['additionalCharts']['conflictIntensity'].append(4)

# ── D74 daily row ─────────────────────────────────────────────────
d['dailyRows'].append({
    "date": "May 12",
    "missiles": 0,
    "drones": 0,
    "primaryTargets": (
        "TRUMP DEPARTS FOR BEIJING — XI SUMMIT MAY 14-15 (2 DAYS); "
        "China rebuffs US pressure to use leverage on Iran; both sides contain "
        "Iran differences to protect broader summit agenda; Brent $104.97 (+0.73%); "
        "Israeli strikes kill 7 in S. Lebanon; zero Iranian offensive strikes D67-D74"
    ),
    "capability": (
        "Zero new Iranian offensive missile or drone strikes on D74. Trump departed "
        "for Beijing on Tuesday ahead of the May 14–15 summit with Xi Jinping — the "
        "most consequential diplomatic meeting since the conflict began. Iran war is "
        "the central unresolved shadow over the meeting: Trump has pressed Xi to use "
        "China's leverage over Tehran (China buys ~90% of Iranian oil exports) but "
        "Beijing has rebuffed these requests, protecting discounted Iranian oil imports "
        "and Gulf trade relationships. Both administrations signaled intent to contain "
        "Iran disagreements so trade, fentanyl, and Taiwan items can proceed — but "
        "analysts expect Iran to dominate at least one session. Lebanon: Israeli strikes "
        "killed 7 people and wounded 7 in southern Lebanon; the Lebanon ceasefire "
        "(started Apr 16) is under increasing strain with both Israel and Hezbollah "
        "escalating operations. Brent hit $104.97, up 0.73% from May 11, as markets "
        "continue pricing extended Hormuz closure following Trump's 'life support' "
        "declaration. No revised Iranian MOU proposal received as of day's end."
    ),
    "cost": (
        "Brent $104.97 (confirmed, +0.73% from May 11 close). "
        "WTI $98.50 est (range $96.93–$100.35 intraday). "
        "Iran rial ~1,840,000/USD (est). Internet Day 74 = 1,776+ hrs; "
        "Bloomberg cumulative ~$2.6B+ economic loss. "
        "Lebanon killed ~2,747+ (est, +7 May 12). ~2,000 ships stranded in Gulf. "
        "HRANA ~3,740+ (est). US: 13 KIA, 365 WIA (no new update). "
        "Polymarket regime-falls-May-31: ~2%."
    ),
    "assessment": (
        "D74 is summit eve: Trump en route to Beijing, two days before the "
        "highest-stakes diplomacy of the conflict. The strategic calculus: China "
        "holds enormous potential leverage over Iran but has declined to use it "
        "coercively, viewing US pressure as an infringement on sovereign economic "
        "relationships. Xi's most likely play — offer vague 'responsible actor' "
        "stability language while extracting trade or Taiwan concessions in return "
        "for any Iran signaling. Brent at $104.97 reflects markets fully pricing "
        "extended Hormuz closure post-'life support' declaration. Iran's next move: "
        "a revised MOU proposal with more explicit nuclear language (or a hard "
        "refusal) was expected before May 14 but had not arrived by end of D74. "
        "IRGC posture remains threatening (D72 'heavy assault' warning) but no "
        "new kinetic actions. Lebanon escalation is a real risk vector — a major "
        "Hezbollah attack before May 14 would complicate summit dynamics. "
        "Escalation probability: ~0.42 (slightly eased from D73 peak; summit "
        "creates a pause in US escalation decision-making). Deal probability: ~0.32 "
        "(Xi summit is the remaining near-term catalyst; watch for Iran's revised "
        "proposal in next 48h and Xi-Trump joint statement language on Iran). "
        "Watch: Iran revised MOU response; Xi-Trump joint communićué Iran language; "
        "Lebanon ceasefire trajectory."
    )
})

# ── Meta ──────────────────────────────────────────────────────
d['meta']['lastUpdated'] = '2026-05-12T14:00:00-04:00'
d['meta']['notes'].insert(0,
    "D73 (May 11): Trump rejects Iran counterproposal as 'piece of garbage', "
    "declares ceasefire 'on massive life support'; Iran demands Hormuz sovereignty + "
    "war compensation + sanctions relief with no nuclear phase-1 concessions; "
    "CENTCOM 61 ships redirected (↑3); Brent +3% to ~$103.50 est; "
    "Lebanon 4 killed; Turkish FM to Qatar"
)
d['meta']['notes'].insert(0,
    "D74 (May 12): Trump departs for Beijing; Xi summit May 14-15 (2 days); "
    "China rebuffs Iran leverage requests; Brent $104.97 confirmed; "
    "Lebanon 7 killed; zero Iranian strikes D67-D74; no revised MOU received"
)

with open(WAR_DATA, 'w') as f:
    json.dump(d, f, indent=2)

print("apply-d74.py: Done. D73 + D74 data written to", WAR_DATA)
