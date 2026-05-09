#!/usr/bin/env python3
"""
One-time Vercel build fix: restore D70 war-data.json from git history
(HEAD~1 = commit 2385d9f, the last good version) and apply D71 data.

Safe to leave in place: if war-data.json already has real data (> 1 KB)
the script exits immediately with no changes.
"""
import json, subprocess, sys

WAR_DATA = 'legacy/war-data.json'

# ── Guard: skip if file already has real content ───────────────────────────
current = open(WAR_DATA).read().strip()
if len(current) > 1000:
    print("apply-d71.py: war-data.json looks good, no action needed.")
    sys.exit(0)

print("apply-d71.py: PLACEHOLDER detected — restoring D70 from git history…")

# ── Restore D70 from HEAD~1 (Vercel shallow clone always has HEAD~1) ──────
r = subprocess.run(['git', '--no-pager', 'show', 'HEAD~1:' + WAR_DATA],
                   capture_output=True, text=True)
if r.returncode != 0:
    # fallback: try specific D70 hash
    r = subprocess.run(['git', '--no-pager', 'show',
                        '2385d9f:' + WAR_DATA],
                       capture_output=True, text=True)
if r.returncode != 0:
    print(f"apply-d71.py: ERROR: could not retrieve D70 data\n{r.stderr}",
          file=sys.stderr)
    sys.exit(1)

d = json.loads(r.stdout)
print("apply-d71.py: D70 restored, applying D71 additions…")

# ── D71 standard arrays (70 → 71) ─────────────────────────────────────────
d['dailySeries']['labels'].append('May 09')
d['dailySeries']['missiles'].append(0)
d['dailySeries']['drones'].append(0)
d['dailySeries']['confidence'].append(0.75)

d['pressure']['labels'].append('May 09')
d['pressure']['attrition'].append(10.9)
d['pressure']['cost'].append(9.2)

d['predictive']['vectors']['labels'].append('May 09')
d['predictive']['vectors']['militaryExhaustion'].append(6.9)
d['predictive']['vectors']['economicPain'].append(9.1)
d['predictive']['vectors']['diplomaticMomentum'].append(5.8)
d['predictive']['vectors']['usPoliticalSustainability'].append(4.1)
d['predictive']['vectors']['escalationCeilingDistance'].append(2.0)

d['additionalCharts']['geoSpreadLabels'].append('May 09')
d['additionalCharts']['countriesTargetedPerDay'].append(0)
d['additionalCharts']['missileDroneRatio'].append(0)
d['additionalCharts']['interceptRateLabels'].append('May 09')
d['additionalCharts']['interceptRate'].append(0.88)

# ── D71 pre-war-anchor arrays (71 → 72) ───────────────────────────────────
d['oil']['labels'].append('May 09')
d['oil']['brent'].append(101.65)
d['oil']['wti'].append(95.46)

d['hormuzTransit']['labels'].append('May 09')
d['hormuzTransit']['vessels'].append(3)

d['additionalCharts']['conflictIntensity'].append(3)

# ── D71 daily row ──────────────────────────────────────────────────────────
d['dailyRows'].append({
    "date": "May 09",
    "missiles": 0,
    "drones": 0,
    "primaryTargets": (
        "KHARG OIL SPILL: 80k-bbl slick (~71 sq km) at Iran's main crude export terminal; "
        "US fires on 2 more Iranian tankers in Hormuz enforcement; Araghchi: US chose "
        "'reckless military adventure' over diplomacy; Iran MOU response still pending — "
        "48-hr US deadline expired; Trump-Xi summit (May 14-15) looms as hard deadline"
    ),
    "capability": (
        "Zero new Iranian offensive missile or drone strikes on D71. Dominant story: "
        "satellite imagery shows ~80,000-barrel oil slick (~71 sq km) from Kharg Island, "
        "Iran's main crude export terminal — first detected May 5, cause unknown (accident, "
        "airstrike, or sabotage). US blockade enforcement: two more Iranian tankers fired "
        "upon and disabled near the Strait. Iranian FM Araghchi: 'Every time a diplomatic "
        "solution is on the table, the U.S. opts for a reckless military adventure.' Iran FM "
        "still reviewing US MOU — 48-hr Rubio deadline expired with no formal answer. Qatari "
        "PM told VP Vance on Friday 'high probability' of deal; Pakistan+Qatar mediation "
        "tracks now coordinated. Rubio flagged Iran's attempt to set up a Strait control "
        "agency as 'unacceptable.' Trump-Xi summit (May 14-15) now 5 days away — Beijing "
        "pressed Tehran to pursue diplomacy; Iran focus expected to dominate summit agenda."
    ),
    "cost": (
        "Brent $101.65 (est, weekend carry from D70 close — markets closed Sat; Kharg "
        "spill risk premium partially offsets). WTI $95.46 (est, weekend carry). Iran rial "
        "~1,789,000/USD (est, carry). Internet Day 72 = 1,728+ hrs. Kharg oil spill "
        "~80k bbls = ~$8.1M at spot prices. Lebanon killed ~2,730+ (est). "
        "~2,000 ships stranded in Gulf. HRANA ~3,690+ (est). "
        "Polymarket regime-falls-by-May-31: 2.2%. Deal-by-Jun30 ~52% (est, stable)."
    ),
    "assessment": (
        "D71 surfaces a new strategic variable: the Kharg Island oil spill. If caused by "
        "US airstrike or sabotage, it constitutes a major escalation against Iran's most "
        "critical economic asset — Kharg handles ~90% of Iranian oil exports. If a "
        "maintenance failure, it still underscores how Iran's energy infrastructure is "
        "deteriorating. Either way, it hands Araghchi a rhetorical weapon feeding IRGC "
        "hardliners resisting the MOU nuclear moratorium. The 48-hr US ultimatum expired "
        "with no Iranian answer — standard procedural delay, but Trump's patience is finite "
        "ahead of Xi summit. Vance-Qatar PM meeting signals Pakistan+Qatar tracks now "
        "coordinated. Trump-Xi summit (May 14-15) is 5 days away — both sides want Hormuz "
        "language in the summit communique. Escalation probability: ~0.32 (Kharg spill "
        "unknown cause keeps a floor); deal probability: ~0.38 (Qatari PM optimism + "
        "summit pressure). Watch: cause of Kharg spill; Iran's formal MOU response; "
        "Rubio reaction to Iran's Strait control agency; Trump statements pre-Xi summit."
    )
})

# ── Meta ──────────────────────────────────────────────────────────────────────────
d['meta']['lastUpdated'] = '2026-05-09T18:00:00-04:00'
d['meta']['notes'].insert(0,
    "D71 (May 09): KHARG ISLAND OIL SPILL — 80k-bbl slick at Iran's main crude terminal; "
    "US fires on 2 more Iranian tankers; Araghchi condemns US 'reckless military adventure'; "
    "Iran MOU response overdue; Vance-Qatar PM: 'high probability' of deal; "
    "Trump-Xi summit (May 14-15) now hard deadline; Brent $101.65 est (wknd carry); "
    "zero Iranian offensive strikes D41-D71 streak"
)

# ── Write ──────────────────────────────────────────────────────────────────────────
with open(WAR_DATA, 'w') as f:
    json.dump(d, f, indent=2)

print("apply-d71.py: Done. D71 data written to", WAR_DATA)
