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

## What NOT to do

- Do NOT just append a new day without reviewing all previous data
- Do NOT leave any chart array with null values
- Do NOT create duplicate date entries in dailyRows
- Do NOT skip the validation step
- Do NOT change the JSON structure/schema — only update values within existing keys
