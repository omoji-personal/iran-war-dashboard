"""Render the predictive-agent homepage from portfolio.yaml + memory + logs.

Produces production-grade HTML using the existing editorial-brief aesthetic:
- Iowan Old Style / Palatino serif for headlines + body
- Inter sans for UI metadata
- Dark navy (#0b1322) + cream (#ecdfd0) + rust (#d97757) palette
- 1480px max-width, 2-col body, responsive

Usage:
    python3 scripts/render.py            # renders index.html
    python3 scripts/render.py --public   # also renders public.html
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parent.parent
PORTFOLIO_PATH = REPO_ROOT / "portfolio.yaml"
MEMORY_PATH = REPO_ROOT / "agent" / "memory.md"
QUEUE_PATH = REPO_ROOT / "agent" / "operator-queue.md"
HISTORY_PATH = REPO_ROOT / "engine_history.json"
OUTPUT_INDEX = REPO_ROOT / "index.html"
OUTPUT_PUBLIC = REPO_ROOT / "public.html"


ICD203_BUCKETS = [
    (0.00, 0.01, "vanishing", "<1%"),
    (0.01, 0.05, "almost no chance", "1-5%"),
    (0.05, 0.20, "very unlikely", "5-20%"),
    (0.20, 0.45, "unlikely", "20-45%"),
    (0.45, 0.55, "roughly even chance", "45-55%"),
    (0.55, 0.80, "likely", "55-80%"),
    (0.80, 0.95, "very likely", "80-95%"),
    (0.95, 0.99, "almost certain", "95-99%"),
    (0.99, 1.01, "near certain", ">99%"),
]


def icd203(p: float) -> tuple[str, str, str]:
    """Returns (label, range_str, css_class)."""
    for lo, hi, label, range_str in ICD203_BUCKETS:
        if lo <= p < hi:
            css = label.replace(" ", "-")
            return label, range_str, css
    return "unknown", "?", "unknown"


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


def compute_24h_diffs(portfolio: dict, history: list[dict]) -> list[dict]:
    diffs = []
    if not history:
        return diffs
    last = history[-1]
    last_qs = {q.get("id"): q for q in last.get("questions", [])}
    for q in portfolio["questions"]:
        qid = q["id"]
        cur_p = q["current_probability"]
        last_q = last_qs.get(qid, {})
        last_p = last_q.get("probability", cur_p)
        delta = cur_p - last_p
        ci = q.get("current_credible_interval_80", [cur_p, cur_p])
        ci_halfwidth = (ci[1] - ci[0]) / 2.0
        if abs(delta) > ci_halfwidth and ci_halfwidth > 0:
            diffs.append({
                "id": qid,
                "question": q["question"],
                "old_p": last_p,
                "new_p": cur_p,
                "delta_pp": delta * 100,
            })
    return diffs


def esc(s: str) -> str:
    if s is None:
        return ""
    return (str(s).replace("&", "&amp;")
                  .replace("<", "&lt;")
                  .replace(">", "&gt;")
                  .replace('"', "&quot;"))


def first_line(text: str) -> str:
    if not text:
        return ""
    for line in text.strip().splitlines():
        line = line.strip()
        if line:
            return line
    return ""


def render_question_card(q: dict) -> str:
    p = q["current_probability"]
    label, range_str, label_css = icd203(p)
    ci = q["current_credible_interval_80"]
    humility = q.get("humility_flag", False)
    notes = first_line(q.get("notes", ""))
    deadline = q["deadline"]

    cat_meta = CATEGORY.get(q["category"], ("", "", "cat-default"))
    cat_css = cat_meta[2]

    pct = round(p * 100)
    ci_lo = round(ci[0] * 100)
    ci_hi = round(ci[1] * 100)

    flags = []
    if humility:
        flags.append('<span class="card-flag flag-humility" title="Model class has zero validated track record on this outcome type">HUMILITY</span>')
    for tag in q.get("stakeholder_tags", []):
        if tag == "omid_personal":
            flags.append('<span class="card-flag flag-personal" title="Affects user personally">PERSONAL</span>')
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
            <span class="qcard-ci-bar">
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


def render_diff_panel(diffs: list[dict]) -> str:
    if not diffs:
        return """
        <section class="diff-panel diff-empty">
          <h2 class="diff-h">What changed in last 24h</h2>
          <p class="diff-empty-msg">First tick — no prior baseline. Future updates show only probability movements <em>larger than each question's 80% credible-interval half-width</em> (CI-aware noise suppression — small wobbles within model uncertainty are not reported).</p>
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
        <section class="diff-panel">
          <h2 class="diff-h">What changed in last 24h</h2>
          <ul class="diff-list">{"".join(items)}</ul>
        </section>
    """


def topness(q: dict) -> float:
    n_tags = len(q.get("stakeholder_tags", []))
    is_personal = "omid_personal" in q.get("stakeholder_tags", [])
    bonus = 0.3 if is_personal else 0.0
    return q["current_probability"] * 0.5 + n_tags * 0.15 + bonus


def render_top_question(q: dict) -> str:
    label, _, css = icd203(q["current_probability"])
    pct = round(q["current_probability"] * 100)
    ci = q["current_credible_interval_80"]
    notes = first_line(q.get("notes", ""))
    return f"""
      <section class="topq topq-{css}">
        <div class="topq-eyebrow">Today's top question · {esc(q['id'])} · → {esc(q['deadline'])}</div>
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


def render_headline_narrative() -> str:
    return """
      <section class="headline">
        <div class="headline-eyebrow">Today's headline · interpretation, not forecast</div>
        <p class="headline-lead"><span class="dropcap">D</span>65 of conflict (cease-fire Day 26 with active blockade limbo). Iran's 14-point counter-proposal is in motion via Pakistani mediators; Trump is reviewing the &ldquo;concept of the deal&rdquo; but reports as &ldquo;not satisfied.&rdquo; Khamenei's Apr 30 nuclear-and-missile vow &mdash; his first public statement since the conflict began &mdash; has hardened red lines on the issue most central to any framework.</p>
        <p class="headline-body">Polymarket's deal-by-Jun30 contract sits at <strong>36%</strong> (down 3pp). Hormuz blockade is at Day 17 with ~2,000 ships stranded; Iran's Hormuz Sovereignty Law is advancing in parliament. Brent has retreated from the $126 D62 intraday high to ~$108; US gas $4.45 (+0.013/d). Khamenei reportedly recovering from severe burns; publicly unseen since Feb 28. Mojtaba reported &ldquo;unconscious / face-burnt&rdquo; per March 2026 multiple-source coverage. Iran oil storage 12-22d remaining (Kpler). USD/IRR free-market reached 1.45M Dec 2025 and trajectory points higher.</p>
      </section>
    """


def render_methodology() -> str:
    return """
      <section class="methodology">
        <h2 class="meth-h">Methodology + honesty disclosures</h2>
        <ul class="meth-list">
          <li><strong>EXPERIMENTAL — UNCALIBRATED.</strong> No prediction has resolved yet. Model has no validated track record. Brier scores against Polymarket / Metaculus / AR baseline begin populating Phase 2+ as resolutions accumulate.</li>
          <li><strong>Probabilities are operator-set initial reads</strong> in Phase 0 MVP. Bayesian update + 5-input ensemble (Bayesian, baseline, market, external SOTA, named-expert composite) activates Phase 2.</li>
          <li><strong>Two questions carry permanent humility flags</strong> (C1 Khamenei death, C3 Mojtaba succession) — every published statistical conflict-forecasting model has failed to predict regime-fracture / leader-incapacity events. Treat probabilities as structurally uncertain, not numeric.</li>
          <li><strong>Reference classes</strong> (strict + broad tiers) governing each probability are at <code>reference_classes.yaml</code>.</li>
          <li><strong>Sourced LR table</strong> (every likelihood ratio carries source class — historical-analog / market-implied / explicitly-subjective with replacement criteria) at <code>lr_table.yaml</code>. Activates Phase 2.</li>
          <li><strong>No alpha-trade output.</strong> Until 1-year Brier beats relevant benchmark for the specific outcome class, no actionable trade signals are surfaced.</li>
          <li><strong>External 90-day adversarial review</strong> by Sadjadpour / Vaez / Alfoneh planned — 5 most-divergent predictions sent for critique; feedback published as artifact + drives method changes.</li>
          <li>Full design at <code>docs/superpowers/specs/2026-05-03-predictive-agent-design.md</code> (v8 — converged after 7 adversarial-review rounds). Audit at <code>docs/audits/AUDIT-2026-05-03.md</code>.</li>
        </ul>
      </section>
    """


def render_logs_section() -> str:
    return """
      <section class="logs-section">
        <h2 class="logs-h">Eight first-class change logs</h2>
        <p class="logs-sub">For a <em>living</em> model the change-history is the product. All logs are committed Markdown, append-only per cron tick.</p>
        <div class="logs-grid">
          <a class="log-card" href="logs/events"><span class="log-name">Event log</span><span class="log-desc">Every ingested event with source, cluster ID, applied LRs</span></a>
          <a class="log-card" href="logs/probability-changes"><span class="log-name">Probability-change log</span><span class="log-desc">Every probability movement with attribution chain</span></a>
          <a class="log-card" href="logs/agent-decisions"><span class="log-name">Agent-decision log</span><span class="log-desc">What the agent investigated, why, what it found</span></a>
          <a class="log-card" href="logs/sources-shifted"><span class="log-name">Sources-shifted log</span><span class="log-desc">Polymarket / Metaculus / expert deltas</span></a>
          <a class="log-card" href="logs/adversarial-inputs"><span class="log-name">Adversarial-input log</span><span class="log-desc">Quarantined claims, deception flags, state-media positioning</span></a>
          <a class="log-card placeholder"><span class="log-name">LR-revision log</span><span class="log-desc">Phase 2+: every LR change with old, new, source class, justification</span></a>
          <a class="log-card placeholder"><span class="log-name">Resolution log</span><span class="log-desc">Phase 2+: every question resolved with Brier, post-mortem</span></a>
          <a class="log-card placeholder"><span class="log-name">Reference-class log</span><span class="log-desc">Phase 2+: members added/removed with justification</span></a>
        </div>
      </section>
    """


def render_question_board(by_cat: dict) -> str:
    parts = ['<section class="board"><h2 class="board-h">Question portfolio · 32 questions</h2>']
    for cat_id, (num, title, css) in CATEGORY.items():
        if cat_id not in by_cat:
            continue
        parts.append(f"""
          <div class="board-cat board-{css}">
            <header class="board-cat-head">
              <span class="board-cat-num">{esc(num)}</span>
              <h3 class="board-cat-title">{esc(title)}</h3>
              <span class="board-cat-count">{len(by_cat[cat_id])} questions</span>
            </header>
            <div class="board-grid">
              {"".join(render_question_card(q) for q in by_cat[cat_id])}
            </div>
          </div>
        """)
    parts.append("</section>")
    return "\n".join(parts)


def render_html(portfolio: dict, diffs: list[dict], stripped: bool = False) -> str:
    by_cat: dict[str, list[dict]] = {}
    for q in portfolio["questions"]:
        by_cat.setdefault(q["category"], []).append(q)

    top_q = max(portfolio["questions"], key=topness)

    now = datetime.now(timezone.utc)
    next_tick_local = "Daily 06:00 ET (next tomorrow morning)"

    title = "2026 Iran Conflict — Predictive Agent"
    if stripped:
        title += " (Public)"

    return f"""<!DOCTYPE html>
<html lang="en" dir="ltr">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{esc(title)}</title>
  <meta property="og:title" content="{esc(title)}" />
  <meta property="og:description" content="Daily structured scenario analysis — predictive-agent v0.2 (Phase 0 MVP). 32 Brier-scoreable discrete-event predictions across diplomatic / military / regime / economic / US-side / family-business categories. Experimental — uncalibrated." />
  <meta property="og:type" content="article" />
  <meta name="description" content="Daily predictive-agent brief on the 2026 Iran conflict. Experimental — uncalibrated." />
  <link rel="stylesheet" href="dashboard.css" />
  <link rel="canonical" href="https://iran-war-dashboard-murex.vercel.app/" />
  <script defer src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
</head>
<body class="agent-v2">

  <div class="topbar">
    <div class="topbar-inner">
      <div class="topbar-l">
        <span class="topbar-eyebrow">2026 Iran Conflict</span>
        <span class="topbar-title">Predictive Agent</span>
      </div>
      <div class="topbar-r">
        <span class="topbar-meta">Tick: {esc(now.strftime("%Y-%m-%d %H:%M UTC"))}</span>
        <span class="topbar-meta">Next: {esc(next_tick_local)}</span>
        <span class="topbar-meta">Engine v{esc(portfolio["metadata"]["engine_version"])}</span>
        <span class="topbar-meta">Phase 0 MVP</span>
      </div>
    </div>
  </div>

  <div class="experimental-banner agent-banner">
    <strong>EXPERIMENTAL — UNCALIBRATED</strong>
    <span>No prediction has resolved yet. Model has no validated track record. Treat probabilities as structured scenario reasoning, not as forecasts.
    <a href="docs/superpowers/specs/2026-05-03-predictive-agent-design.md">Design spec</a> ·
    <a href="docs/audits/AUDIT-2026-05-03.md">Audit</a> ·
    <a href="/legacy">Legacy dashboard</a></span>
  </div>

  <main class="agent-page">

    <header class="agent-masthead">
      <div class="masthead-class">FOR ANALYTIC PURPOSES · UNCLASSIFIED MODEL OUTPUT · OPERATOR-DRIVEN</div>
      <div class="masthead-row">
        <div class="masthead-l">
          <div class="masthead-eyebrow">Issue · D65 · cease-fire Day 26 · blockade Day 17</div>
          <h1 class="masthead-title">The Read</h1>
        </div>
        <div class="masthead-r">
          <div class="masthead-publisher">2026 IRAN CONFLICT MONITOR</div>
          <div class="masthead-publisher-sub">Predictive Agent · Daily 0700 ET cron</div>
        </div>
      </div>
      <div class="masthead-rule"></div>
    </header>

    {render_diff_panel(diffs)}

    {render_top_question(top_q)}

    {render_headline_narrative()}

    {render_question_board(by_cat)}

    {render_logs_section()}

    {render_methodology()}

  </main>

  <footer class="agent-footer">
    <div class="agent-footer-inner">
      <div class="agent-footer-l">
        <div class="agent-footer-brand">2026 IRAN CONFLICT PREDICTIVE AGENT</div>
        <div class="agent-footer-meta">Daily structured scenario analysis · cron-driven · experimental · uncalibrated</div>
      </div>
      <div class="agent-footer-r">
        <a href="docs/superpowers/specs/2026-05-03-predictive-agent-design.md">Design spec (v8)</a>
        <a href="docs/audits/AUDIT-2026-05-03.md">Audit (2026-05-03)</a>
        <a href="docs/CRON-WORKFLOW.md">Cron workflow</a>
        <a href="portfolio.yaml">Portfolio (YAML)</a>
        <a href="reference_classes.yaml">Reference classes</a>
        <a href="lr_table.yaml">LR table</a>
      </div>
    </div>
  </footer>

</body>
</html>
"""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--public", action="store_true", help="Also render public.html")
    args = parser.parse_args()

    portfolio = load_portfolio()
    history = load_history()
    diffs = compute_24h_diffs(portfolio, history)

    OUTPUT_INDEX.write_text(render_html(portfolio, diffs, stripped=False), encoding="utf-8")
    print(f"wrote {OUTPUT_INDEX}")
    if args.public:
        OUTPUT_PUBLIC.write_text(render_html(portfolio, diffs, stripped=True), encoding="utf-8")
        print(f"wrote {OUTPUT_PUBLIC}")


if __name__ == "__main__":
    main()
