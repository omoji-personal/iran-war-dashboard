"""Programmatically refresh agent/memory.md from portfolio + history + logs.

Replaces the prior approach of asking the cron LLM to compose memory each tick
(inconsistent, drift-prone). This script writes a deterministic memory file
that the LLM can read for context but never has to write.

Usage:
    python3 scripts/refresh_memory.py
"""
from __future__ import annotations

import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
PORTFOLIO = REPO_ROOT / "portfolio.yaml"
HISTORY = REPO_ROOT / "portfolio_history.json"
QUEUE = REPO_ROOT / "agent" / "operator-queue.md"
MEMORY = REPO_ROOT / "agent" / "memory.md"
EVENTS_DIR = REPO_ROOT / "logs" / "events"
PROBCHG_DIR = REPO_ROOT / "logs" / "probability-changes"
SOURCES_DIR = REPO_ROOT / "logs" / "sources-shifted"

ICD203 = [
    (0.00, 0.01, "vanishing"),
    (0.01, 0.05, "almost no chance"),
    (0.05, 0.20, "very unlikely"),
    (0.20, 0.45, "unlikely"),
    (0.45, 0.55, "roughly even chance"),
    (0.55, 0.80, "likely"),
    (0.80, 0.95, "very likely"),
    (0.95, 0.99, "almost certain"),
    (0.99, 1.001, "near certain"),
]


def label_for(p: float) -> str:
    p = max(0.0, min(1.0, p))
    for lo, hi, label in ICD203:
        if lo <= p < hi:
            return label
    return "near certain"


CATEGORY_ORDER = [
    "diplomatic_resolution", "military_escalation", "regime_leadership",
    "economic_structural", "us_side",
    "family_business_iranfarhang", "family_business_kipa",
]


def category_title(cat_id: str) -> str:
    return {
        "diplomatic_resolution": "A. Diplomatic resolution",
        "military_escalation": "B. Military escalation",
        "regime_leadership": "C. Regime / leadership",
        "economic_structural": "D. Economic / structural",
        "us_side": "E. US side",
        "family_business_iranfarhang": "F.1 Iranfarhang business",
        "family_business_kipa": "F.2 Kipa business",
    }.get(cat_id, cat_id)


def _ordered_categories(by_cat: dict) -> list[str]:
    """Return categories in canonical order, then any extras seen in portfolio.
    Ensures new categories added to portfolio.yaml become visible automatically
    instead of being silently dropped by a hardcoded list."""
    seen = list(CATEGORY_ORDER)
    extras = [c for c in by_cat.keys() if c not in seen]
    return [c for c in seen if c in by_cat] + extras


# Marker that fences the operator-curated context block. Lines between these
# markers are preserved verbatim across ticks; without the markers, prior
# operator notes are wiped each tick by the regenerator.
OP_BLOCK_BEGIN = "<!-- BEGIN operator-curated context (preserved across ticks) -->"
OP_BLOCK_END = "<!-- END operator-curated context -->"


def extract_operator_block(memory_text: str) -> str | None:
    """Pull the operator-curated block from existing memory.md if present.
    Returns the inner content (between markers, exclusive) or None if missing."""
    if OP_BLOCK_BEGIN not in memory_text or OP_BLOCK_END not in memory_text:
        return None
    start = memory_text.index(OP_BLOCK_BEGIN) + len(OP_BLOCK_BEGIN)
    end = memory_text.index(OP_BLOCK_END)
    return memory_text[start:end].strip("\n")


def load_portfolio() -> dict:
    return yaml.safe_load(PORTFOLIO.read_text(encoding="utf-8"))


def load_history() -> list[dict]:
    if not HISTORY.exists():
        return []
    try:
        d = json.loads(HISTORY.read_text(encoding="utf-8"))
        return d if isinstance(d, list) else []
    except json.JSONDecodeError:
        return []


def recent_logs(directory: Path, days: int = 7) -> list[Path]:
    """Return up to `days` most-recent log files in a daily-log directory."""
    if not directory.exists():
        return []
    files = sorted([p for p in directory.iterdir() if p.suffix == ".md"], reverse=True)
    return files[:days]


def queue_summary() -> str:
    if not QUEUE.exists():
        return "_No operator-queue.md._"
    text = QUEUE.read_text(encoding="utf-8")
    # Extract H2 headers (## ...) as queue items, skip template/placeholder lines
    items = []
    for l in text.splitlines():
        if not l.startswith("## "):
            continue
        body = l[3:].strip()
        # Skip the literal template line "YYYY-MM-DD — {{question_id_or_topic}} ..."
        if "{{" in body or body.startswith("YYYY-MM-DD"):
            continue
        items.append(body)
    if not items:
        return "_Empty._"
    return "\n".join(f"- {l}" for l in items[:10])


def recent_probability_changes_in(days: int = 7, history: list[dict] | None = None) -> str:
    """Compute moves > CI half-width since `days` ago."""
    if history is None:
        history = load_history()
    if len(history) < 2:
        return "_No prior snapshots — first ticks of Phase 0._"
    portfolio = load_portfolio()
    cur_qs = {q["id"]: q for q in portfolio["questions"]}
    today_iso = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    cutoff_dt = datetime.now(timezone.utc).date() - timedelta(days=days)
    cutoff_iso = cutoff_dt.isoformat()

    # Find earliest snapshot in window
    in_window = [h for h in history if h.get("date") and cutoff_iso <= h["date"] < today_iso]
    if not in_window:
        return "_No snapshots in last {}d._".format(days)
    base = in_window[0]
    base_qs = {q.get("id"): q for q in base.get("questions", [])}

    changes = []
    for qid, q in cur_qs.items():
        cur_p = q["current_probability"]
        base_p = base_qs.get(qid, {}).get("probability", cur_p)
        delta = cur_p - base_p
        ci = q.get("current_credible_interval_80", [cur_p, cur_p])
        ci_half = (ci[1] - ci[0]) / 2.0
        if abs(delta) > ci_half and ci_half > 0:
            arrow = "▲" if delta > 0 else "▼"
            changes.append(
                f"- **{qid}** {arrow} {delta*100:+.1f}pp "
                f"({base_p*100:.0f}% → {cur_p*100:.0f}%) — {q['question'][:80]}"
            )
    if not changes:
        return f"_No moves above CI noise floor in last {days}d (since {base['date']})._"
    return "\n".join(changes)


def render_memory() -> str:
    portfolio = load_portfolio()
    history = load_history()
    now = datetime.now(timezone.utc)
    now_str = now.strftime("%Y-%m-%dT%H:%M:%S UTC")

    by_cat: dict[str, list[dict]] = {}
    for q in portfolio["questions"]:
        by_cat.setdefault(q["category"], []).append(q)

    out = []
    out.append(f"# Agent Memory — last regenerated {now_str}")
    out.append("")
    out.append(f"_This file is **programmatically regenerated** each tick by `scripts/refresh_memory.py` from `portfolio.yaml`, `portfolio_history.json`, `agent/operator-queue.md`, and recent logs._")
    out.append("")

    # Portfolio summary
    out.append("## Portfolio summary (current state)")
    out.append("")
    out.append(f"Engine version: **{portfolio['metadata']['engine_version']}** · "
               f"Spec: **{portfolio['metadata']['spec_version']}** · "
               f"Questions: **{len(portfolio['questions'])}** · "
               f"History snapshots: **{len(history)}**")
    out.append("")
    for cat_id in _ordered_categories(by_cat):
        if cat_id not in by_cat:
            continue
        out.append(f"### {category_title(cat_id)}")
        out.append("")
        for q in by_cat[cat_id]:
            p = q["current_probability"]
            label = label_for(p)
            humility = " 🚩 [HUMILITY]" if q.get("humility_flag") else ""
            personal = " 👤 [PERSONAL]" if "omid_personal" in q.get("stakeholder_tags", []) else ""
            out.append(
                f"- **{q['id']}** {p*100:.0f}% (*{label}*){humility}{personal} → {q['deadline']}: {q['question'][:80]}"
            )
        out.append("")

    # Recent changes
    out.append("## Recent probability changes (last 7d)")
    out.append("")
    out.append(recent_probability_changes_in(days=7, history=history))
    out.append("")

    # Operator queue
    out.append("## Open Tier-C operator decisions")
    out.append("")
    out.append(queue_summary())
    out.append("")

    # Recent logs
    out.append("## Recent log files")
    out.append("")
    for label, dir_path in [
        ("Events", EVENTS_DIR),
        ("Probability changes", PROBCHG_DIR),
        ("Sources shifted", SOURCES_DIR),
    ]:
        files = recent_logs(dir_path, days=5)
        if files:
            out.append(f"- **{label}**: " + ", ".join(f"`{f.name}`" for f in files))
    out.append("")

    # Top-of-mind context — operator-curated; PRESERVED VERBATIM across ticks.
    # The block between OP_BLOCK_BEGIN/END markers in the existing memory.md is
    # carried forward unchanged. If no prior memory.md exists OR the markers are
    # missing, a minimal seed is written and the operator owns subsequent edits.
    out.append("## Top-of-mind context (operator-curated)")
    out.append("")
    out.append("_Operator: add fresh notes between the markers below. Each tick `refresh_memory.py` preserves whatever is between the markers verbatim — it does NOT regenerate this block. If you delete the markers, you lose preservation._")
    out.append("")
    out.append(OP_BLOCK_BEGIN)
    existing_block = None
    if MEMORY.exists():
        try:
            existing_block = extract_operator_block(MEMORY.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError):
            existing_block = None
    if existing_block is not None:
        out.append(existing_block)
    else:
        # Minimal seed only when no prior block exists. Operator overwrites this
        # on first edit; thereafter it's preserved verbatim.
        out.append("_(operator-curated context will appear here once written. The regenerator preserves this block verbatim across ticks.)_")
    out.append(OP_BLOCK_END)
    out.append("")

    return "\n".join(out)


def main() -> None:
    text = render_memory()
    # Atomic write: tmp + rename so partial writes never leave memory.md half-done
    tmp = MEMORY.with_suffix(".md.tmp")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(MEMORY)
    print(f"refreshed {MEMORY}")
    print(f"  {len(text.splitlines())} lines")


if __name__ == "__main__":
    main()
