#!/usr/bin/env python3
"""
Vercel build script: restore D72 war-data.json.
1. If war-data.json already has real content (> 1 KB), exit immediately.
2. Otherwise, call apply-d71.py to restore D71 state.
3. Verify we have 71 dailyRows, then append D72 data.
"""
import json, subprocess, sys, os

WAR_DATA = 'legacy/war-data.json'

# ── Guard: skip if file already has real content ───────────────────────────
current = open(WAR_DATA).read().strip()
if len(current) > 1000:
    print("apply-d72.py: war-data.json looks good, no action needed.")
    sys.exit(0)

print("apply-d72.py: PLACEHOLDER detected — running apply-d71.py to restore D71…")

r = subprocess.run([sys.executable, 'legacy/apply-d71.py'],
                   capture_output=False)
if r.returncode != 0:
    print("apply-d72.py: ERROR: apply-d71.py failed", file=sys.stderr)
    sys.exit(1)

d = json.load(open(WAR_DATA))
n = len(d.get('dailyRows', []))
if n != 71:
    print(f"apply-d72.py: ERROR: expected 71 dailyRows after D71 restore, got {n}",
          file=sys.stderr)
    sys.exit(1)

print("apply-d72.py: D71 confirmed (71 rows). Applying D72 additions…")

# ── D72 standard arrays (71 → 72) ─────────────────────────────────────────
d['dailySeries']['labels'].append('May 10')
d['dailySeries']['missiles'].append(0)
d['dailySeries']['drones'].append(0)
d['dailySeries']['confidence'].append(0.72)

d['pressure']['labels'].append('May 10')
d['pressure']['attrition'].append(11.0)
d['pressure']['cost'].append(9.3)

d['predictive']['vectors']['labels'].append('May 10')
d['predictive']['vectors']['militaryExhaustion'].append(7.0)
d['predictive']['vectors']['economicPain'].append(9.2)
d['predictive']['vectors']['diplomaticMomentum'].append(6.3)
d['predictive']['vectors']['usPoliticalSustainability'].append(3.8)
d['predictive']['vectors']['escalationCeilingDistance'].append(2.1)

d['additionalCharts']['geoSpreadLabels'].append('May 10')
d['additionalCharts']['countriesTargetedPerDay'].append(0)
d['additionalCharts']['missileDroneRatio'].append(0)
d['additionalCharts']['interceptRateLabels'].append('May 10')
d['additionalCharts']['interceptRate'].append(0.88)

# ── D72 pre-war-anchor arrays (72 → 73) ───────────────────────────────────────
d['oil']['labels'].append('May 10')
d['oil']['brent'].append(100.49)
d['oil']['wti'].append(95.00)

d['hormuzTransit']['labels'].append('May 10')
d['hormuzTransit']['vessels'].append(3)

d['additionalCharts']['conflictIntensity'].append(3)

# ── D72 daily row ─────────────────────────────────────────────────────────────────────
d['dailyRows'].append({
    "date": "May 10",
    "missiles": 0,
    "drones": 0,
    "primaryTargets": (
        "IRGC WARNS 'HEAVY ASSAULT' ON US BASES IF TANKER ATTACKS CONTINUE; "
        "MOU stalemate persists as Iran reviews 14-point memo — nuclear moratorium "
        "duration (12 vs 15 yrs) main gap; Trump-Xi summit May 14-15 now 4 days away "
        "as hard MOU deadline; China presses Iran directly (Wang Yi): 'immediate end "
        "to hostilities'; Kharg oil spill blame shifts — Iranian official claims "
        "European tanker caused slick; CNN: Iran's 'two-tier internet' exposes "
        "regime control apparatus"
    ),
    "capability": (
        "Zero new Iranian offensive missile or drone strikes on D72. Dominant story: "
        "Iran's IRGC navy issued a stark warning Sunday that any further US attacks on "
        "Iranian oil tankers would be met with a 'heavy assault on US bases in the region "
        "and enemy ships' — the sharpest direct threat since D41. CENTCOM cumulative "
        "blockade scorecard (since Apr 13): 58 commercial ships turned back, 4 Iranian "
        "tankers disabled. Kharg Island oil spill: Iranian official attributed the "
        "~45–71 sq km slick to waste discharged by a European tanker; independent "
        "analysts and the Conflict & Environment Observatory maintain cause is unknown "
        "and the slick is drifting south. CNN investigation published Sunday on Iran's "
        "'Internet Pro' two-tier system: IRGC-linked elites retain connectivity while "
        "~90M citizens remain blacked out — regime using access disparity as a control "
        "mechanism. MOU talks: Witkoff and Kushner continuing remotely; Trump ruled out "
        "in-person envoy trip; 14-point MOU under review by Iranian side; key gap on "
        "uranium enrichment moratorium duration (US: 15 yrs, Iran: ~12 yrs) and HEU "
        "removal vs monitored downblending."
    ),
    "cost": (
        "Brent $100.49 (est, Sun carry from May 8 close — markets closed). "
        "WTI $95.00 (est, Sun carry). Iran rial ~1,789,000/USD (est, carry). "
        "Internet Day 72 = 1,728+ hrs; estimated $35–80M/day economic loss. "
        "Kharg slick drifting south, ~45 sq km remaining; cause unresolved. "
        "Lebanon killed ~2,730+ (est). ~2,000 ships stranded in Gulf. "
        "HRANA ~3,700+ (est). US: 13 KIA, 365 WIA. "
        "Polymarket regime-falls-May-31: ~2%."
    ),
    "assessment": (
        "D72 is a Sunday pressure-building day: no new kinetic events but the diplomatic "
        "clock is loudest it has been. Trump-Xi summit (May 14-15) is 4 days away and "
        "Beijing has now directly pressed Tehran — Wang Yi's 'immediate end to hostilities' "
        "call is the clearest Chinese ultimatum yet. Iran has strong incentive to signal "
        "progress before the summit (Chinese oil imports and economic lifeline at stake). "
        "But IRGC's 'heavy assault' warning simultaneously signals the Revolutionary Guard "
        "is drawing red lines around blockade enforcement. The Kharg spill blame-shift "
        "to a European tanker removes the US/Israeli escalation narrative internally, but "
        "the underlying infrastructure vulnerability remains. CNN's 'two-tier internet' "
        "story is politically explosive inside Iran — IRGC privilege during a national "
        "blackout feeds popular resentment. Escalation probability: ~0.30 (IRGC warning "
        "is a negotiating posture, not imminent action — but blockade enforcement incidents "
        "remain a trigger risk). Deal probability: ~0.40 (summit pressure and Qatari+Pakistan "
        "coordination are the strongest signals yet; MOU gap is bridgeable at 13–14 yrs). "
        "Watch: Iran's formal MOU response before May 14; Xi-Trump Iran language; IRGC "
        "reaction to any further tanker enforcement."
    )
})

# ── Meta ──────────────────────────────────────────────────────────────────────────────
d['meta']['lastUpdated'] = '2026-05-10T18:00:00-04:00'
d['meta']['notes'].insert(0,
    "D72 (May 10): IRGC issues 'heavy assault' warning vs US bases if tanker attacks continue; "
    "Trump-Xi summit 4 days away — China directly presses Iran (Wang Yi); MOU gap: 12 vs 15 yr "
    "enrichment moratorium; Kharg spill blame-shift to European tanker; CNN exposes Iran's "
    "two-tier 'Internet Pro' (IRGC privilege during national blackout); Brent $100.49 est; "
    "zero Iranian offensive strikes streak continues D41-D72"
)

# ── Write ──────────────────────────────────────────────────────────────────────────────
with open(WAR_DATA, 'w') as f:
    json.dump(d, f, indent=2)

print("apply-d72.py: Done. D72 data written to", WAR_DATA)
