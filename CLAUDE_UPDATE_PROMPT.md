# Iran War Dashboard — Recurring Update Instructions

You are updating the Iran War Dashboard (iran-war-dashboard-murex.vercel.app).

## What to do

1. **Search the web** for the latest developments in the 2026 Iran war using multiple queries:
   - `Iran war [today's date] latest`
   - `Iran missile drone attack Gulf [today's date]`
   - `Brent crude oil price today`
   - `Iran war casualties update`
   - Any other relevant queries based on what you find

2. **Read the current `war-data.json`** from this repo

3. **Perform a FULL RE-ANALYSIS** of the entire file — not just appending a new day:
   - Review and revise ALL historical daily launch estimates if better data is now available
   - Update oil prices with confirmed close/open data
   - Revise casualty figures if new counts are reported
   - Update all analytical sections (sitrep, theory, scenarios, endstate, shipping, publishing, business impact)
   - Add the new day's data if a new day has started since the last update
   - If still the same day, update the existing day's entry with latest information

4. **Ensure data integrity**:
   - All chart arrays (dailySeries.labels, missiles, drones) must be same length
   - All oil arrays (labels, brent, wti) must be same length
   - All pressure arrays (labels, attrition, cost) must be same length
   - dailyRows must match dailySeries in count, dates, and values
   - ZERO nulls in any chart array
   - ZERO duplicate dates in dailyRows
   - Chart values must match table values for every day

5. **Write the updated `war-data.json`** to the repo

6. **Commit and push**:
   ```
   git add war-data.json
   git commit -m "war-data update [timestamp]"
   git push origin main
   ```

## Data methodology

- **D1–D10 missiles/drones**: JPost verified day-by-day (cumul: 2,410 missiles / 3,560 drones)
- **D11**: UAE MoD official (13 missiles + 39 drones UAE-only, scaled ×2.08 for all-theater)
- **D12+**: Fragment estimates from Gulf state reports, scaled via INSS ratio (UAE ≈ 48% of all projectiles)
- **Oil**: CNBC/Investing.com confirmed where available, interpolated between
- **All estimates**: Use best available fragment data. Never leave a data point blank or null.

## Source hierarchy

1. Official military/government statements (CENTCOM, UAE MoD, IDF, IRGC)
2. Wire services (Reuters, AP)
3. Major outlets (CNN, Al Jazeera, BBC, NPR)
4. Research organizations (GlobalSecurity, ACLED, IISS, FDD)
5. Specialist outlets (Breaking Defense, Iran International)
6. Wikipedia (Iran war / Timeline articles — good aggregation)

## Key discrepancy to maintain

Iran claims ~700 missiles / ~3,600 drones total. JPost/Israeli estimates are much higher. IRGC claimed D16 that "most weapons cache intact, using decade-old missiles." Dashboard uses JPost series for trend continuity but documents the discrepancy in source notes.

## Business context for impact analysis

### Iranfarhang (Book Supply)
- Tehran-based supplier of Persian-language books to US/Canadian university and research libraries for 25+ years
- Original shipping route: Air cargo Tehran → Dubai (Emirates SkyCargo) → Atlanta office → UPS to institutions
- OFAC exemption: 31 CFR §560.210(c) — informational materials (Berman Amendment). STATUTORY, not executive — survives any sanctions regime
- Payment: Via KEMCO SARL, a third-country entity in France
- Key dependencies: Tehran warehouse inventory, Iranian publishing industry (paper imports, printing, internet), shipping routes, power grid
- Analysis should focus on: route viability, inventory status, publishing industry conditions, client communications, OFAC/legal status, family safety

### KIP (Import-Export)
- Private Iranian family import-export company using Dubai/UAE as logistics hub, re-export point, and financial gateway
- The Iran-UAE trade corridor is the lifeblood of this business
- Key dependencies: Hormuz strait (shipping), UAE banking (trade finance), Dubai free zones (warehousing), UAE airspace (cargo flights), personnel safety in UAE
- Analysis should focus on: Dubai hub operability, banking freeze risk, alternative hub assessment (Turkey/Georgia/Oman/Malaysia), stranded inventory, insurance, personnel safety, Hormuz reopening timeline

### Writing style for business sections
- Every bullet should be SPECIFIC to the business, not a restatement of general war news
- Lead with the business impact, then explain why (the war event)
- Impact = what happened TO the business. Prep = what the business should DO. Signals = what to WATCH that would change the picture
- Prep items should be actionable: "do X this week" not "monitor developments"
- Use `<strong>Label:</strong>` formatting for lead-in

## New analytical sections (added D27)

In addition to the core data, update these analytical sections each cycle:

- **`casualties` / `casualties_fa`**: Array of objects `{group, figure, statusColor, detail}`. Track by group: Iran, Lebanon, Israel, Iraq, Gulf States. Include source discrepancy note. Update figures from IRNA, HRANA, Hengaw, Health Ministries.
- **`humanitarian` / `humanitarian_fa`**: Array of HTML-safe strings. Cover: internet blackout duration, displacement, infrastructure damage, nuclear safety, medical crisis, economic impact.
- **`diplomacy` / `diplomacy_fa`**: Array of HTML-safe strings. Track: peace proposals, intermediary channels, positions of each side, deadlines, G7/UN moves.
- **`publicOpinion` / `publicOpinion_fa`**: Array of HTML-safe strings. Track: US polls (Pew, AP-NORC, Quinnipiac, etc.), congressional reactions, international statements.
- **`hormuz` / `hormuz_fa`**: Array of HTML-safe strings. Track: blockade status, safe passage framework expansion, mine threat, toll legislation, insurance crisis, military deployments (82nd Airborne), key questions.
- **`keyActors` / `keyActors_fa`**: Array of HTML-safe strings. Track: each major actor (US, Israel, Iran/IRGC, Pakistan, India, Hezbollah, Houthis, GCC, 82nd Airborne, IAEA) with current status and role.

All of these use `<strong>Label:</strong>` formatting for the lead-in of each bullet point.

## What NOT to do

- Do NOT just append a new day without reviewing all previous data
- Do NOT leave any chart array with null values
- Do NOT create duplicate date entries in dailyRows
- Do NOT skip the validation step
- Do NOT change the JSON structure/schema — only update values within existing keys
- Do NOT remove any of the new analytical sections (casualties, humanitarian, diplomacy, publicOpinion, hormuz, keyActors)
