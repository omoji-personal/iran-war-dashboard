# Morning Briefing — Design Spec

**Date:** 2026-05-15
**Status:** v1 (brainstormed; awaiting user review)
**Origin:** User report that the live site "shows static info on refresh" despite the existing daily-cron architecture. Diagnosis: (a) the cron has not landed since D68 on 2026-05-06 (9-day silent staleness), and (b) the first viewport is dominated by evergreen prose (masthead → "Today's read" → "Why this page exists" frame → "What's most likely to keep being true" base case) that does not change day-to-day even when data does.

## 0. Goal

Make the live site at `https://iran-war-dashboard-murex.vercel.app/` feel like a fresh morning briefing on every refresh. Specifically:

1. The first viewport visibly changes every morning at 07:00 ET.
2. A reader who skims for 30 seconds learns what moved overnight, what the agent thinks today, and what events drove the changes.
3. Failure to refresh is loud, not silent — a stale-warning state replaces the briefing when the cron has not run in >36h.
4. Zero new operating cost — runs entirely inside the existing Claude Code subscription + Vercel free tier.

## 1. Layout — what the user sees

The current top of the page (masthead + "Today's read" headline + "Why this page exists" frame + "What's most likely to keep being true" base case + "What changed since the last update" diff + top question) is replaced by a single **Morning Brief** block. The 32 question cards stay underneath, unchanged. The evergreen frame / methodology prose moves into a collapsible "About this page" footer.

The Morning Brief block has four stacked panels:

### 1.1 Overnight strip (one row)

`D77 · May 15 · 07:00 ET tick · 14 events overnight · 3 probability moves · cron OK ✓`

Renders straight from the briefing JSON. Three states:
- **Fresh** (briefing ≤24h old): neutral header style, green check.
- **Aging** (24–36h): yellow warning, "Last updated 28h ago".
- **Stale** (>36h or `cron-failed` flag present): red banner, "Last update: 2026-05-15 07:00 ET · cron has not refreshed in 38h · briefing below may be out of date".

### 1.2 The read (2–3 paragraphs)

Fresh narrative written each morning by the cron LLM. Replaces today's static "Today's read" + "What's most likely to keep being true" sections — those become inputs the LLM rewrites every morning, not durable prose. Length: 150–300 words. Tone matches today's editorial-brief voice.

### 1.3 What moved (probability movers)

The 3–5 questions whose `current_probability` shifted most in the last 24h, each one line:

```
F8  ▼ 7pp · 48% → 41% · rial recovered to 1.72M overnight per Bourse&Bazaar
B1  ▲ 3pp · 15% → 18% · IRGC missile near US destroyer per Reuters
A1  — · 22% (unchanged) · talks stalled per AP
```

Empty-state when nothing moved: "No probability moves on the question cards since {{LAST_CHANGE_DATE}}." (Same copy as today's diff panel.)

### 1.4 What happened (events)

5–8 bullet headlines from the overnight news scan, each with a source link:

```
• Iran's commercial FX rate eased to 1.72M IRR/USD overnight — Bourse&Bazaar
• Araghchi confirmed meeting with Wang Yi in Beijing — Tasnim
• IRGC fired anti-ship missile near USS Bulkeley in Hormuz — Reuters
…
```

Provides the audit trail behind the read + the movers. A skeptical reader can verify the LLM is not inventing.

## 2. Pipeline — what the cron does

Replaces today's 9-step Phase-0 procedure at `agent/cron-prompt.phase-0.md`. New procedure:

1. **Read state** *(unchanged)* — `agent/memory.md`, `portfolio.yaml`, recent logs, `agent/operator-queue.md`.
2. **Fetch market signals** *(unchanged)* — Polymarket + Manifold + Metaculus → `logs/sources-shifted/{TODAY}.md`.
3. **Fetch news (NEW)** — `scripts/fetch_news.py` pulls last 24h items from a curated RSS feed list (initial set in §5.1) via Python `feedparser`. Writes raw items to `logs/events/{TODAY}.json` with fields: `source`, `title`, `url`, `published_at`, `lang`, `summary`.
4. **Web-search supplement (NEW)** — LLM runs 4–6 targeted WebSearch queries to fill RSS gaps (e.g. "Hormuz shipping today", "Trump Iran statement 24h"). Appends to `logs/events/{TODAY}.json` with `source: web-search`.
5. **Detect probability moves** *(unchanged)* — compare `portfolio.yaml` to last `portfolio_history.json` snapshot, write `logs/probability-changes/{TODAY}.md`.
6. **Generate briefing copy (NEW)** — single LLM pass synthesizes the four panels into `agent/briefing-{TODAY}.json`. Schema in §3. Produces both `en` and `fa` blocks in one pass.
7. **Append history** *(unchanged)* — `scripts/append_history.py`.
8. **Refresh memory** *(unchanged)* — `scripts/refresh_memory.py`.
9. **Render (modified)** — `scripts/render.py` reads `agent/briefing-{TODAY}.json` and emits the Morning Brief block into `index.html`, `fa.html`, `public.html`, `public.fa.html`. Public variants strip blocks with `public_safe: false`.
10. **Commit straight to main (CHANGED)** — no draft PR. Push to `main`. Vercel auto-deploys. If any earlier step fails, push a `cron-failed-{TODAY}.flag` file so the render layer flips to the stale-warning state.

Removed from today's flow: the draft-PR + operator-merge gate (steps 9 and the surrounding `gh pr create --draft` block). Phase 0's "portfolio.yaml is operator-only" rule stays — the briefing is *commentary on* portfolio values, never *edits* them.

## 3. Briefing JSON schema

`agent/briefing-{TODAY}.json`:

```json
{
  "tick_date": "2026-05-15",
  "tick_timestamp_utc": "2026-05-15T11:00:00Z",
  "day_number": 77,
  "cron_status": "ok",
  "events_count_24h": 14,
  "probability_moves_24h": 3,
  "briefing_partial": false,
  "en": {
    "read_paragraphs": ["…", "…", "…"],
    "movers": [
      {
        "qid": "F8",
        "direction": "down",
        "delta_pp": 7,
        "old": 48,
        "new": 41,
        "why": "rial recovered to 1.72M overnight",
        "citation_url": "https://...",
        "public_safe": false
      }
    ],
    "events": [
      {
        "headline": "Iran's commercial FX rate eased to 1.72M IRR/USD overnight",
        "source_name": "Bourse&Bazaar",
        "url": "https://...",
        "published_at": "2026-05-15T03:12:00Z",
        "public_safe": true
      }
    ]
  },
  "fa": { "…": "same shape, Persian text" }
}
```

`scripts/render.py` reads this file. If absent or older than 36h, it renders the stale-warning state and the 32 question cards still appear from `portfolio.yaml`.

## 4. Safety rails

The cron commits to main with no human gate. Five rails compensate.

### 4.1 Citations required per event bullet

Every `events[].url` must be non-empty and resolvable. `render.py` drops events with missing URLs. If fewer than 3 cited events survive, the panel renders "No verified overnight events" rather than partial content.

### 4.2 Mover rows are computed, not invented

`render.py` regenerates `movers[]` from the actual `portfolio_history.json` diff. The LLM only supplies the `why` string per row, and that string is fact-checked: it must reference a substring or entity that appears in one of the surviving events. If it does not, the `why` is replaced with `(no event-grounded explanation generated this tick)`.

### 4.3 Public-variant scrubber

`public_safe: false` on any briefing block excludes it from `public.html` / `public.fa.html`. F-question movers and PERSONAL-tagged content (Iranfarhang/Kipa references) stay out of the public set, matching today's behavior in `scripts/build-public.py`. If a public-variant render would result in <3 surviving events, the public movers + events panels render empty-state copy instead of the full sanitized version.

### 4.4 Stale-warning state

`render.py` checks for either condition:
- `cron-failed-{TODAY}.flag` exists in repo root, OR
- `agent/briefing-{TODAY}.json` is missing OR its `tick_timestamp_utc` is >36h old at render time.

If either holds, the overnight strip flips to the red stale banner. The "the read" panel shows the most recent successful briefing's text with a "Last fresh briefing: {{DATE}}" prefix. The movers and events panels show "No fresh data — cron has not refreshed in {{HOURS}}h."

### 4.5 Budget abort

The existing $5 / 30min / 50 tool-call cap stays. If steps 3–6 push past the cap, the cron writes whatever briefing material it has, sets `briefing_partial: true`, and `render.py` emits a "Briefing truncated — partial data only" notice above the panels. Better partial than fabricated.

## 5. New / changed files

### 5.1 `scripts/fetch_news.py` (new)

Python script using `feedparser`. Initial feed list (free, no auth):

- Reuters Middle East — `https://www.reuters.com/world/middle-east/rss`
- AP World News — `https://apnews.com/index.rss`
- Al-Monitor Iran — `https://www.al-monitor.com/feeds/iran-pulse.rss`
- Amwaj Media — `https://amwaj.media/rss`
- Bourse & Bazaar — `https://www.bourseandbazaar.com/articles?format=rss`
- IRNA English — `https://en.irna.ir/rss`
- Tasnim English — `https://www.tasnimnews.com/en/rss/feed/0`
- Tehran Times — `https://www.tehrantimes.com/rss`
- Iran International — `https://www.iranintl.com/en/rss.xml`
- Times of Israel Iran — `https://www.timesofisrael.com/topic/iran/feed/`
- Long War Journal — `https://www.longwarjournal.org/feed`
- WarOnTheRocks — `https://warontherocks.com/feed/`
- Crisis Group MidEast — `https://www.crisisgroup.org/middle-east-north-africa/rss.xml`
- US State Dept press releases — `https://www.state.gov/press-releases/feed/`
- WhiteHouse.gov briefing room — `https://www.whitehouse.gov/briefing-room/feed/`

Filters out items older than 24h. Writes `logs/events/{TODAY}.json` per §3 schema. Idempotent.

### 5.2 `agent/cron-prompt.phase-0.md` (rewrite)

Update the 10-step procedure to match §2. Add explicit step for briefing-JSON generation with the schema from §3. Replace the `gh pr create --draft` block with direct `git push origin main`.

### 5.3 `scripts/render.py` (modified)

Reads `agent/briefing-{TODAY}.json` when present, emits the Morning Brief block as the first child of `<main class="agent-page">`. Removes the existing `<section class="headline">`, `<section class="frame">`, `<section class="basecase">`, `<section class="diff-panel">`, `<section class="topq">` blocks from the rendered output; their content (frame + methodology paragraphs) moves into a collapsible `<details class="about-this-page">` block at the page footer.

### 5.4 `dashboard.css` (additions)

New rules for `.morning-brief`, `.brief-strip`, `.brief-read`, `.brief-movers`, `.brief-events`, `.brief-strip-stale`, `.brief-strip-aging`. Reuses existing typography tokens. No font/family changes (per user's `feedback_iran_dashboard_design.md` HARD RULE: keep Inter/system font, no sweeping passes).

### 5.5 `agent/briefing-{TODAY}.json` (new daily artifact)

Per §3. Committed each tick. Not gitignored.

### 5.6 `cron-failed-{TODAY}.flag` (new fail-state artifact)

Empty file at repo root, written by the cron's failure branch. Stale-warning trigger per §4.4.

## 6. Bilingual handling

Step 6 of the cron (briefing generation) produces both `en` and `fa` blocks in a single LLM pass. The Persian text follows the existing Persian-typography conventions in the repo (Vazirmatn webfont, bidi-fixed dates, Persian numerals where appropriate per the recent Round-17/18 commits). No separate translation pass — the LLM writes both directly to keep cost at one round-trip.

If the FA block is missing or shorter than the EN block by >50%, `render.py` falls back to rendering the EN block in `fa.html` with a small "Persian translation pending" note, rather than emitting truncated Persian.

## 7. What is intentionally NOT in this design

- **No human approval gate.** Operator picked fully-auto in brainstorming. If hallucinations become a problem in practice, add a 5-minute review window or revert to today's draft-PR flow — but that's a v2 decision, not v1.
- **No probability adjustments by the LLM.** Phase 0's "portfolio.yaml is operator-only" rule stays. The briefing is commentary on existing values.
- **No adversarial review pass before publish.** Considered but rejected: it doubles the tick cost in LLM time and would push past the 30min budget. The five safety rails in §4 + the visible source links in the events panel are the substitute.
- **No new external services.** No paid news APIs, no paid translation, no paid hosting. Strict $0 marginal cost.
- **No mobile-specific briefing layout.** Existing responsive CSS handles narrow widths; the Morning Brief block reuses it.

## 8. Open questions for the implementer

These are intentionally left for the implementation plan rather than decided here, because they're small and the right answer becomes obvious once code starts:

- Exact CSS token set for the stale banner — should match the existing `experimental-banner` red but at higher saturation.
- Whether to log every cron tick's briefing JSON history into `portfolio_history.json`-style artifact, or rely on git history for retrospectives.
- Whether `fetch_news.py` should de-duplicate near-identical headlines from multiple sources (likely yes, fuzzy-match titles, threshold TBD by implementer).

## 9. Acceptance criteria

The feature is shipped when:

1. The cron at `trig_01UD1sGTg9SHWMN2HjY7AiBa` runs for 3 consecutive days and produces a fresh briefing each morning visible at the live URL by 07:30 ET.
2. The first viewport on refresh contains the Morning Brief block, not the evergreen frame/base-case prose.
3. Manually deleting `agent/briefing-{TODAY}.json` and re-rendering produces the stale-warning state correctly.
4. Public variant (`public.html`) contains no F-question movers and no PERSONAL-tagged events.
5. A non-English reader at `fa.html` sees a Persian briefing of comparable length to the English one.
6. Cost over 30 days: $0 marginal (verified by no new billing line items on Vercel / no new paid API keys in repo).
