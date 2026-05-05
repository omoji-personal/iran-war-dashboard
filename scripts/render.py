"""Render the predictive-agent homepage from portfolio.yaml + memory + logs.

Produces production-grade HTML using the editorial-brief aesthetic:
- Iowan Old Style / Palatino serif for headlines + body
- Inter sans for UI metadata
- Dark navy (#0b1322) + cream (#ecdfd0) + rust (#d97757) palette
- 1480px max-width, 2-col body, responsive

Usage:
    python3 scripts/render.py            # renders index.html
    python3 scripts/render.py --public   # also renders public.html (stripped)
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parent.parent
PORTFOLIO_PATH = REPO_ROOT / "portfolio.yaml"
MEMORY_PATH = REPO_ROOT / "agent" / "memory.md"
QUEUE_PATH = REPO_ROOT / "agent" / "operator-queue.md"
HISTORY_PATH = REPO_ROOT / "portfolio_history.json"
SOURCES_SHIFTED_DIR = REPO_ROOT / "logs" / "sources-shifted"
EVENTS_DIR = REPO_ROOT / "logs" / "events"
OUTPUT_INDEX = REPO_ROOT / "index.html"
OUTPUT_PUBLIC = REPO_ROOT / "public.html"

# Hardcoded reference date for "war Day N" computation. D1 of conflict = 2026-02-28.
WAR_D1_ISO = "2026-02-28"
# Cease-fire start: 2026-04-07 (Day 39)
CEASEFIRE_START_ISO = "2026-04-07"
# Hormuz blockade start: 2026-04-15 (Day 47, est.)
BLOCKADE_START_ISO = "2026-04-15"


ICD203_BUCKETS = [
    (0.00, 0.01, "vanishing", "<1%"),
    (0.01, 0.05, "almost no chance", "1-5%"),
    (0.05, 0.20, "very unlikely", "5-20%"),
    (0.20, 0.45, "unlikely", "20-45%"),
    (0.45, 0.55, "roughly even chance", "45-55%"),
    (0.55, 0.80, "likely", "55-80%"),
    (0.80, 0.95, "very likely", "80-95%"),
    (0.95, 0.99, "almost certain", "95-99%"),
    (0.99, 1.001, "near certain", ">99%"),
]


def icd203(p: float) -> tuple[str, str, str]:
    """Returns (label, range_str, css_class)."""
    p = max(0.0, min(1.0, p))
    for lo, hi, label, range_str in ICD203_BUCKETS:
        if lo <= p < hi:
            css = label.replace(" ", "-")
            return label, range_str, css
    # p == exactly 1.0 hits the last bucket
    label, range_str, _ = ICD203_BUCKETS[-1][2:] if False else ("near certain", ">99%", "near-certain")
    return label, range_str, "near-certain"


CATEGORY = {
    "diplomatic_resolution": ("§ A", "Diplomatic resolution", "cat-diplomacy"),
    "military_escalation": ("§ B", "Military escalation", "cat-military"),
    "regime_leadership": ("§ C", "Regime / leadership", "cat-regime"),
    "economic_structural": ("§ D", "Economic / structural", "cat-economic"),
    "us_side": ("§ E", "US side", "cat-us"),
    "family_business_iranfarhang": ("§ F.1", "Iranfarhang business", "cat-iranfarhang"),
    "family_business_kipa": ("§ F.2", "Kipa business", "cat-kipa"),
}


def load_portfolio() -> dict:
    return yaml.safe_load(PORTFOLIO_PATH.read_text(encoding="utf-8"))


def load_history() -> list[dict]:
    if not HISTORY_PATH.exists():
        return []
    try:
        data = json.loads(HISTORY_PATH.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except json.JSONDecodeError:
        return []


def _is_v02_snapshot(h: dict) -> bool:
    """v0.1 history entries (legacy engine) lack a `questions[]` array; they
    have keys like `scores`, `outcomeProbabilities`, `resolutionProbability`.
    Treating those as a v0.2 baseline produces silently-empty diffs that
    misleadingly read as 'no probability moves' instead of 'no comparable
    baseline'. Only consider snapshots that carry a v0.2 questions[] array."""
    qs = h.get("questions")
    return isinstance(qs, list) and len(qs) > 0


def compute_diffs_vs_yesterday(portfolio: dict, history: list[dict]) -> list[dict]:
    """Compare today's portfolio against the most recent snapshot whose date is
    BEFORE today. Avoids the today-vs-today degenerate-zero-diff bug."""
    today_iso = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    prior = [h for h in history if h.get("date") and h["date"] < today_iso and _is_v02_snapshot(h)]
    if not prior:
        return []
    last = prior[-1]
    last_qs = {q.get("id"): q for q in last.get("questions", [])}
    diffs = []
    for q in portfolio["questions"]:
        qid = q["id"]
        cur_p = q["current_probability"]
        last_q = last_qs.get(qid, {})
        last_p = last_q.get("probability", cur_p)
        delta = cur_p - last_p
        ci = q.get("current_credible_interval_80", [cur_p, cur_p])
        ci_halfwidth = (ci[1] - ci[0]) / 2.0
        # CI-aware noise suppression: only headline diffs > question's CI half-width
        if abs(delta) > ci_halfwidth and ci_halfwidth > 0:
            diffs.append({
                "id": qid,
                "question": q["question"],
                "old_p": last_p,
                "new_p": cur_p,
                "delta_pp": delta * 100,
            })
    return diffs


def war_day(today: datetime) -> int:
    """Days since 2026-02-28 (D1). Returns int >= 1."""
    d1 = datetime.fromisoformat(WAR_D1_ISO).replace(tzinfo=timezone.utc)
    return max(1, (today.date() - d1.date()).days + 1)


def cf_day(today: datetime) -> int:
    """Days since cease-fire start (2026-04-07). Returns 0 if before."""
    cf1 = datetime.fromisoformat(CEASEFIRE_START_ISO).replace(tzinfo=timezone.utc)
    delta = today.date() - cf1.date()
    return max(0, delta.days + 1) if delta.days >= 0 else 0


def blockade_day(today: datetime) -> int:
    """Days since Hormuz blockade start. 0 if before."""
    bs = datetime.fromisoformat(BLOCKADE_START_ISO).replace(tzinfo=timezone.utc)
    delta = today.date() - bs.date()
    return max(0, delta.days + 1) if delta.days >= 0 else 0


def esc(s: str) -> str:
    if s is None:
        return ""
    return (str(s).replace("&", "&amp;")
                  .replace("<", "&lt;")
                  .replace(">", "&gt;")
                  .replace('"', "&quot;"))


_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-Z(])")


def first_sentence(text: str) -> str:
    """Return the first complete sentence (terminating punctuation included).
    Falls back to first line if no sentence boundary found."""
    if not text:
        return ""
    cleaned = " ".join(line.strip() for line in text.strip().splitlines() if line.strip())
    parts = _SENTENCE_SPLIT.split(cleaned, maxsplit=1)
    candidate = parts[0].strip()
    if not candidate:
        return ""
    # Cap at 220 chars even if no sentence boundary
    if len(candidate) > 220:
        candidate = candidate[:217].rstrip() + "…"
    return candidate


def render_question_card(q: dict, stripped: bool = False) -> str:
    p = q["current_probability"]
    label, range_str, label_css = icd203(p)
    ci = q["current_credible_interval_80"]
    humility = q.get("humility_flag", False)
    notes = first_sentence(q.get("notes", ""))
    deadline = q["deadline"]

    cat_meta = CATEGORY.get(q["category"], ("", "", "cat-default"))
    cat_css = cat_meta[2]

    pct = round(p * 100)
    ci_lo = round(ci[0] * 100)
    ci_hi = round(ci[1] * 100)

    flags = []
    if humility:
        flags.append('<span class="card-flag flag-humility" title="Model class has zero validated track record on this outcome type">HUMILITY</span>')
    # PERSONAL flag is operator-private — never shown on the stripped public deploy
    if not stripped:
        for tag in q.get("stakeholder_tags", []):
            if tag == "omid_personal":
                flags.append('<span class="card-flag flag-personal" title="Directly affects family business">PERSONAL</span>')
                break

    return f"""
      <article class="qcard qcard-{cat_css} qcard-prob-{label_css}" id="q-{q['id']}">
        <header class="qcard-head">
          <span class="qcard-id">{esc(q['id'])}</span>
          <span class="qcard-deadline">→ {esc(deadline)}</span>
          <span class="qcard-flags">{''.join(flags)}</span>
        </header>
        <h3 class="qcard-question">{esc(q['question'])}</h3>
        <div class="qcard-numbers">
          <div class="qcard-prob">
            <span class="qcard-prob-num">{pct}<span class="qcard-prob-pct">%</span></span>
            <span class="qcard-prob-label">{esc(label)}</span>
          </div>
          <div class="qcard-ci">
            <span class="qcard-ci-bar" aria-label="80% credible interval, mark at point estimate">
              <span class="qcard-ci-track"></span>
              <span class="qcard-ci-fill" style="left: {ci_lo}%; width: {ci_hi - ci_lo}%"></span>
              <span class="qcard-ci-mark" style="left: {pct}%"></span>
            </span>
            <span class="qcard-ci-label">80% CI: {ci_lo}–{ci_hi}%</span>
          </div>
        </div>
        <p class="qcard-note">{esc(notes)}</p>
      </article>
    """


def render_diff_panel(diffs: list[dict], history: list[dict]) -> str:
    today_iso = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    prior = [h for h in history if h.get("date") and h["date"] < today_iso and _is_v02_snapshot(h)]
    has_prior_baseline = bool(prior)

    if not has_prior_baseline:
        return """
        <section class="diff-panel diff-empty" role="region" aria-label="What changed since the last update">
          <h2 class="diff-h">What changed since the last update</h2>
          <p class="diff-empty-msg">First update — no prior day to compare against. From tomorrow on, this panel will list only the probabilities that moved more than the question's own uncertainty range. Quiet days will say so.</p>
        </section>
        """
    if not diffs:
        last_date = prior[-1]["date"]
        return f"""
        <section class="diff-panel diff-empty" role="region" aria-label="What changed since the last update">
          <h2 class="diff-h">What changed since the last update</h2>
          <p class="diff-empty-msg">No probability moves above the noise floor since {esc(last_date)}. Quiet day. The questions worth watching are unchanged.</p>
        </section>
        """
    items = []
    for d in diffs:
        arrow = "▲" if d["delta_pp"] > 0 else "▼"
        css_dir = "diff-up" if d["delta_pp"] > 0 else "diff-down"
        items.append(f"""
          <li class="diff-item {css_dir}">
            <a href="#q-{d['id']}">
              <span class="diff-id">{esc(d['id'])}</span>
              <span class="diff-arrow">{arrow}</span>
              <span class="diff-delta">{d['delta_pp']:+.1f}pp</span>
              <span class="diff-from-to">({d['old_p']*100:.0f}% → {d['new_p']*100:.0f}%)</span>
              <span class="diff-question">{esc(d['question'])}</span>
            </a>
          </li>
        """)
    return f"""
        <section class="diff-panel" role="region" aria-label="What changed since the last update">
          <h2 class="diff-h">What changed since the last update</h2>
          <ul class="diff-list">{"".join(items)}</ul>
        </section>
    """


def topness(q: dict, last_q_by_id: dict[str, dict], today: datetime | None = None) -> float:
    """Score for 'top question' selection.

    Picks "the question worth watching today" — biased toward questions that
    are actively in play (45-80% probability) rather than always surfacing the
    biggest tail-risk mover. A 70% question holding steady can still be the
    headline if it's high-stakes and the deadline is near.

    `today` is injected (not pulled from datetime.now()) so historical
    snapshot rendering is reproducible.
    """
    if today is None:
        today = datetime.now(timezone.utc)
    cur_p = q["current_probability"]
    qid = q["id"]
    last_q = last_q_by_id.get(qid, {})
    last_p = last_q.get("probability", cur_p)
    abs_delta = abs(cur_p - last_p)
    n_tags = len(q.get("stakeholder_tags", []))
    is_personal = "omid_personal" in q.get("stakeholder_tags", [])
    has_humility = bool(q.get("humility_flag"))
    # Stakes proxy: # stakeholder tags + personal-affects-Omid bonus
    stakes = n_tags * 0.10 + (0.30 if is_personal else 0.0)
    # Recency bonus: questions with deadlines closer to today carry slightly more weight.
    # YAML may parse date strings as datetime.date OR keep them as str — handle both.
    deadline = q["deadline"]
    if hasattr(deadline, "isoformat"):
        deadline_str = deadline.isoformat()
    else:
        deadline_str = str(deadline)
    try:
        d_dt = datetime.strptime(deadline_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        days_to_deadline = max(1, (d_dt.date() - today.date()).days)
        recency = max(0.0, 1.0 - min(days_to_deadline / 365.0, 1.0)) * 0.10
    except (ValueError, TypeError):
        recency = 0.0
    # Stability bias: a question sitting in the 45-80% band is "actively in play"
    # and more interesting to watch than a 12% tail-risk that just jumped 3pp.
    in_play_bonus = 0.15 if 0.45 <= cur_p < 0.80 else 0.0
    # Humility flags suppress (we shouldn't headline a question we admit we can't forecast)
    humility_penalty = -0.30 if has_humility else 0.0
    return abs_delta * 1.0 + stakes + recency + in_play_bonus + humility_penalty


def render_top_question(q: dict, last_q_by_id: dict, history_present: bool) -> str:
    label, _, css = icd203(q["current_probability"])
    pct = round(q["current_probability"] * 100)
    ci = q["current_credible_interval_80"]
    notes = first_sentence(q.get("notes", ""))
    delta_text = ""
    if history_present:
        last_q = last_q_by_id.get(q["id"], {})
        last_p = last_q.get("probability")
        if last_p is not None and abs(q["current_probability"] - last_p) > 0.001:
            d_pp = (q["current_probability"] - last_p) * 100
            arrow = "▲" if d_pp > 0 else "▼"
            delta_text = f' · <span class="topq-delta">{arrow} {d_pp:+.1f}pp since last tick</span>'

    return f"""
      <section class="topq topq-{css}" role="region" aria-label="Today's top question">
        <div class="topq-eyebrow">Today's top question · {esc(q['id'])} · → {esc(q['deadline'])}{delta_text}</div>
        <h2 class="topq-question">{esc(q['question'])}</h2>
        <div class="topq-row">
          <div class="topq-prob">
            <span class="topq-prob-num">{pct}<span class="topq-prob-pct">%</span></span>
            <span class="topq-prob-label">{esc(label)}</span>
            <span class="topq-prob-ci">80% CI: {round(ci[0]*100)}–{round(ci[1]*100)}%</span>
          </div>
          <p class="topq-note">{esc(notes)}</p>
        </div>
        <a class="topq-link" href="#q-{q['id']}">Read full evidence chain ↓</a>
      </section>
    """


def render_headline_narrative(today: datetime, portfolio: dict, stripped: bool = False) -> str:
    """Compose the headline paragraph dynamically from current date + portfolio.

    Earlier version had hardcoded date/figure references. Now derives day numbers
    from a single fixed reference (D1=2026-02-28). Concrete numbers (Brent, gas,
    casualty counts) are NOT in the headline — they age too fast.

    Stripped (public deploy): scrub all personal/business references. The portfolio
    passed in already has F-categories filtered out.
    """
    d = war_day(today)
    cf = cf_day(today)
    bd = blockade_day(today)
    today_str = today.strftime("%B %d, %Y").replace(" 0", " ")
    # Top 3 highest-stakes questions to anchor narrative
    high_stakes = sorted(
        portfolio["questions"],
        key=lambda q: -len(q.get("stakeholder_tags", [])),
    )[:3]
    bullets = []
    for q in high_stakes:
        label, _, _ = icd203(q["current_probability"])
        bullets.append(f"<strong>{esc(q['id'])}</strong> ({esc(label)}, {round(q['current_probability']*100)}%) — {esc(q['question'])}")

    cf_phrase = f"cease-fire Day {cf}" if cf > 0 else "active conflict"
    bd_phrase = f"Hormuz blockade Day {bd}" if bd > 0 else "Hormuz traffic open"

    if stripped:
        body = (
            f"The three highest-stakes questions to watch right now: "
            f"{'; '.join(bullets)}. "
            f"Each card below shows the current probability, the 80% range it's likely "
            f"to fall in, and a one-line rationale. The list is grouped by topic and "
            f"updated each morning."
        )
    else:
        body = (
            f"The three highest-stakes questions to watch right now: "
            f"{'; '.join(bullets)}. "
            f"The PERSONAL-tagged questions track family-business consequences — "
            f"Iranfarhang (Persian-content distribution to US/UK universities) and "
            f"Kipa (specialty-chemicals importer into Iran). Each card below shows the "
            f"current probability, the 80% range it's likely to fall in, and a one-line "
            f"rationale. Updated each morning."
        )

    return f"""
      <section class="headline" role="region" aria-label="Today's headline">
        <div class="headline-eyebrow">Today's read · {esc(today_str)} · {esc(cf_phrase)} · {esc(bd_phrase)} · interpretation, not forecast</div>
        <p class="headline-lead"><span class="dropcap">D</span>{d} of the 2026 Iran-US conflict. The questions below are scored from a daily reading of public news and prediction-market prices. None have resolved yet, so the probabilities have no track record — treat them as structured guesses, not predictions.</p>
        <p class="headline-body">{body}</p>
      </section>
    """


def render_methodology(stripped: bool = False) -> str:
    # Both paths use plain language — the page is read by family + public, not engineers.
    common = """
      <section class="methodology" role="region" aria-label="What to keep in mind">
        <h2 class="meth-h">What to keep in mind</h2>
        <ul class="meth-list">
          <li><strong>The "most-likely scenario" paragraph at the top is the anchor.</strong> It's the single future getting the most probability mass once you average across the questions. The questions below — especially the ones in the "lower-probability" cluster of each topic — are the named ways that base case could break. Most of those tail-risk cards will read low for a reason.</li>
          <li><strong>Experimental — no track record yet.</strong> None of these questions has resolved, so the probabilities haven't been graded against reality. Treat them as structured guesses.</li>
          <li><strong>Two questions are intentionally fuzzy</strong> — anything tied to whether a leader is alive, ill, or being succeeded (Khamenei, Mojtaba). Forecasting models historically fail at these. The number is a placeholder; the rationale is what to read.</li>
          <li><strong>How probabilities move</strong>: each morning, public news and prediction-market prices are re-read. If something shifts a question by more than its 80% range, it shows up at the top in "What changed since the last update."</li>
          <li><strong>What this is not.</strong> It is not financial or political advice. No one is being told to act on these numbers. Probabilities are scenario weighing, not forecasts.</li>
        </ul>
      </section>
    """
    return common


def render_base_case(portfolio: dict, stripped: bool = False) -> str:
    """Render the operator's modal-forecast paragraph above the question board.

    Reads `metadata.base_case_narrative` (private) or
    `metadata.base_case_narrative_public` (stripped public). Renders nothing
    if the relevant field is empty/missing — graceful no-op so the page still
    works during operator transitions.
    """
    md = portfolio.get("metadata", {}) or {}
    if stripped:
        text = (md.get("base_case_narrative_public") or md.get("base_case_narrative") or "").strip()
    else:
        text = (md.get("base_case_narrative") or "").strip()
    if not text:
        return ""
    last_updated = md.get("base_case_last_updated")
    last_updated_str = ""
    if last_updated is not None:
        # YAML may parse as date or string
        last_updated_str = last_updated.isoformat() if hasattr(last_updated, "isoformat") else str(last_updated)
    eyebrow_extra = f" · last revised {esc(last_updated_str)}" if last_updated_str else ""
    # Preserve operator-line breaks but escape for safety
    paragraphs = [esc(p.strip()) for p in text.split("\n\n") if p.strip()]
    if not paragraphs:
        paragraphs = [esc(text)]
    body_html = "".join(f"<p class=\"basecase-body\">{p}</p>" for p in paragraphs)
    return f"""
      <section class="basecase" role="region" aria-label="Most-likely scenario">
        <div class="basecase-eyebrow">Most-likely scenario · operator's modal forecast{eyebrow_extra}</div>
        <h2 class="basecase-h">What's most likely to keep being true</h2>
        {body_html}
        <p class="basecase-foot">Each topic below leads with the questions sitting closest to this base case, then shows the lower-probability scenarios that would break it.</p>
      </section>
    """


def render_logs_section() -> str:
    # Intentionally empty — the rendered page does not surface internal log files
    # to visitors. The "What changed since last tick" panel covers the
    # visitor-relevant change history. The actual log files remain on disk for
    # operator review but are not linked from the page.
    return ""


# Probability boundary that splits "most-likely outcomes" from "lower-probability
# scenarios to watch". A card at exactly 45% is in the "roughly even" ICD-203
# bucket — close enough to coin-flip that we lead with it.
LIKELY_THRESHOLD = 0.45


def _split_likely_tail(questions: list[dict]) -> tuple[list[dict], list[dict]]:
    """Sort by current_probability descending, then partition at LIKELY_THRESHOLD.
    Returns (likely_cluster, tail_cluster)."""
    sorted_qs = sorted(questions, key=lambda q: -q["current_probability"])
    likely = [q for q in sorted_qs if q["current_probability"] >= LIKELY_THRESHOLD]
    tail = [q for q in sorted_qs if q["current_probability"] < LIKELY_THRESHOLD]
    return likely, tail


def render_question_board(by_cat: dict, stripped: bool = False) -> str:
    total = sum(len(qs) for qs in by_cat.values())
    parts = [f'<section class="board" role="region" aria-label="Question portfolio"><h2 class="board-h">Question portfolio · {total} questions</h2>']
    parts.append(
        '<p class="board-sub">Within each topic, most-likely outcomes lead; '
        'lower-probability scenarios to watch follow under the divider. '
        'Each card shows the current probability and the 80% range it\'s likely to fall in.</p>'
    )
    for cat_id, (num, title, css) in CATEGORY.items():
        if cat_id not in by_cat:
            continue
        likely, tail = _split_likely_tail(by_cat[cat_id])
        cluster_blocks: list[str] = []
        if likely:
            cluster_blocks.append(f"""
              <div class="board-cluster board-cluster-likely">
                <h4 class="board-cluster-h">Most-likely outcomes</h4>
                <div class="board-grid">
                  {"".join(render_question_card(q, stripped=stripped) for q in likely)}
                </div>
              </div>
            """)
        if tail:
            cluster_blocks.append(f"""
              <div class="board-cluster board-cluster-tail">
                <h4 class="board-cluster-h">Lower-probability scenarios to watch</h4>
                <div class="board-grid">
                  {"".join(render_question_card(q, stripped=stripped) for q in tail)}
                </div>
              </div>
            """)
        # If both clusters present, draw a thin divider between them
        cluster_html = '<hr class="board-cluster-divider" aria-hidden="true" />'.join(cluster_blocks) if len(cluster_blocks) > 1 else "".join(cluster_blocks)
        parts.append(f"""
          <div class="board-cat board-{css}">
            <header class="board-cat-head">
              <span class="board-cat-num">{esc(num)}</span>
              <h3 class="board-cat-title">{esc(title)}</h3>
              <span class="board-cat-count">{len(by_cat[cat_id])} questions</span>
            </header>
            {cluster_html}
          </div>
        """)
    parts.append("</section>")
    return "\n".join(parts)


# Categories that contain personal/business content — stripped from public deploy
PRIVATE_CATEGORIES = {"family_business_iranfarhang", "family_business_kipa"}
# Stakeholder tags that mark a question as private — even if its category is generic.
# Defense-in-depth against a private question accidentally being placed in a generic
# category (e.g. economic_structural) but still tagged for personal channels.
PRIVATE_STAKEHOLDER_TAGS = {"omid_personal", "iranfarhang_business", "kipa_business"}


def _is_private_question(q: dict) -> bool:
    if q.get("category") in PRIVATE_CATEGORIES:
        return True
    return any(t in PRIVATE_STAKEHOLDER_TAGS for t in q.get("stakeholder_tags", []))


def render_html(portfolio: dict, diffs: list[dict], history: list[dict], stripped: bool = False) -> str:
    today = datetime.now(timezone.utc)
    today_iso = today.strftime("%Y-%m-%d")
    next_tick_local = "Daily 07:00 ET"

    # Stripped public deploy excludes private/personal/business questions entirely.
    # Filter applies BOTH category and stakeholder-tag rules so a Q tagged for
    # private channels but placed in a generic category still gets stripped.
    questions_for_view = [
        q for q in portfolio["questions"]
        if not stripped or not _is_private_question(q)
    ]
    # Stripped portfolio passed to renderers as if it were the full portfolio
    portfolio_view = {**portfolio, "questions": questions_for_view}

    # Stripped diffs: drop any diff whose Q is private — by category, by tag,
    # OR by ID-prefix `F` (covers a Q that was deleted/recategorized between
    # the snapshot and now and would otherwise leak via the diff payload).
    private_qids = {q["id"] for q in portfolio["questions"] if _is_private_question(q)}
    diffs_for_view = [
        d for d in diffs
        if not stripped or (
            d.get("id", "") not in private_qids
            and not str(d.get("id", "")).startswith("F")
        )
    ]

    by_cat: dict[str, list[dict]] = {}
    for q in questions_for_view:
        by_cat.setdefault(q["category"], []).append(q)

    # last_q_by_id: portfolio snapshot from yesterday-or-prior
    prior = [h for h in history if h.get("date") and h["date"] < today_iso and _is_v02_snapshot(h)]
    last_q_by_id = {q.get("id"): q for q in (prior[-1].get("questions", []) if prior else [])}

    # Top question: filtered to public set if stripped
    if questions_for_view:
        top_q = max(questions_for_view, key=lambda q: topness(q, last_q_by_id, today=today))
    else:
        top_q = portfolio["questions"][0]

    title_base = "2026 Iran Conflict — Predictive Agent"
    title = title_base + (" (Public)" if stripped else "")
    n_questions_visible = len(questions_for_view)
    description_text = f"Daily-updated probability brief on {n_questions_visible} questions about the 2026 Iran-US conflict. Experimental — no track record yet."

    d = war_day(today)
    cf = cf_day(today)
    bd = blockade_day(today)
    issue_subline = f"D{d}"
    if cf > 0:
        issue_subline += f" · cease-fire Day {cf}"
    if bd > 0:
        issue_subline += f" · blockade Day {bd}"

    # Public-stripped: keep a SCRUBBED methodology (no operator-queue / portfolio.yaml refs);
    # drop the eight-logs section entirely (those reference internal Markdown logs not
    # user-facing).
    methodology_html = render_methodology(stripped=stripped)
    logs_html = "" if stripped else render_logs_section()

    # Footer keeps only links a visitor would actually click.
    # Internal docs (design spec, audits, cron workflow) are not surfaced —
    # they exist in the repo for the operator's reference, not the page.
    if stripped:
        footer_links_html = ""
    else:
        footer_links_html = '<a href="/legacy">Older dashboard</a>'

    return f"""<!DOCTYPE html>
<html lang="en" dir="ltr">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta name="theme-color" content="#0b1322" />
  <title>{esc(title)}</title>
  <meta property="og:title" content="{esc(title)}" />
  <meta property="og:description" content="{esc(description_text)}" />
  <meta property="og:type" content="article" />
  <meta name="description" content="{esc(description_text)}" />
  <link rel="stylesheet" href="dashboard.css" />
  <link rel="canonical" href="{esc('https://iran-war-public.vercel.app/' if stripped else 'https://iran-war-dashboard-murex.vercel.app/')}" />
</head>
<body class="agent-v2">

  <div class="topbar">
    <div class="topbar-inner">
      <div class="topbar-l">
        <span class="topbar-eyebrow">2026 Iran-US Conflict</span>
        <span class="topbar-title">Predictive Agent</span>
      </div>
      <div class="topbar-r">
        <span class="topbar-meta" title="Page rendered at this time (UTC)">{esc(today.strftime("%Y-%m-%d %H:%M UTC"))}</span>
        <span class="topbar-meta">Next: {esc(next_tick_local)}</span>
      </div>
    </div>
  </div>

  <div class="experimental-banner agent-banner">
    <strong>EXPERIMENTAL — UNCALIBRATED</strong>
    <span>None of these questions has resolved yet, so the probabilities have no track record. Treat them as structured scenario reasoning, not as forecasts.{(
      ''
      if stripped else
      ' <a href="/legacy">Older dashboard</a>'
    )}</span>
  </div>

  <main class="agent-page" role="main" aria-label="Predictive Agent Brief">

    <header class="agent-masthead" role="banner" aria-label="Issue masthead">
      <div class="masthead-class">FOR ANALYTIC PURPOSES · UNCLASSIFIED MODEL OUTPUT · OPERATOR-DRIVEN</div>
      <div class="masthead-row">
        <div class="masthead-l">
          <div class="masthead-eyebrow">Issue · {esc(issue_subline)}</div>
          <h1 class="masthead-title">Predictive Agent</h1>
        </div>
        <div class="masthead-r">
          <div class="masthead-publisher">2026 IRAN-US CONFLICT MONITOR</div>
          <div class="masthead-publisher-sub">Daily 07:00 ET update</div>
        </div>
      </div>
      <div class="masthead-rule"></div>
    </header>

    {render_diff_panel(diffs_for_view, history)}

    {render_top_question(top_q, last_q_by_id, history_present=bool(prior))}

    {render_headline_narrative(today, portfolio_view, stripped=stripped)}

    {render_base_case(portfolio_view, stripped=stripped)}

    {render_question_board(by_cat, stripped=stripped)}

    {logs_html}

    {methodology_html}

  </main>

  <footer class="agent-footer">
    <div class="agent-footer-inner">
      <div class="agent-footer-l">
        <div class="agent-footer-brand">2026 IRAN-US CONFLICT PREDICTIVE AGENT</div>
        <div class="agent-footer-meta">Daily structured scenario analysis · experimental · no track record yet</div>
      </div>
      <div class="agent-footer-r">
        {footer_links_html}
      </div>
    </div>
  </footer>

</body>
</html>
"""


def main():
    import time
    t0 = time.monotonic()
    parser = argparse.ArgumentParser()
    parser.add_argument("--public", action="store_true", help="Also render public.html (stripped)")
    args = parser.parse_args()

    portfolio = load_portfolio()
    history = load_history()
    diffs = compute_diffs_vs_yesterday(portfolio, history)

    # Atomic write via tmp + rename
    full_html = render_html(portfolio, diffs, history, stripped=False)
    tmp = OUTPUT_INDEX.with_suffix(".html.tmp")
    tmp.write_text(full_html, encoding="utf-8")
    tmp.replace(OUTPUT_INDEX)
    print(f"wrote {OUTPUT_INDEX} ({len(full_html)} bytes)")
    if args.public:
        pub_html = render_html(portfolio, diffs, history, stripped=True)
        tmp_pub = OUTPUT_PUBLIC.with_suffix(".html.tmp")
        tmp_pub.write_text(pub_html, encoding="utf-8")
        tmp_pub.replace(OUTPUT_PUBLIC)
        print(f"wrote {OUTPUT_PUBLIC} ({len(pub_html)} bytes)")
    print(f"render took {time.monotonic() - t0:.2f}s")


if __name__ == "__main__":
    main()
