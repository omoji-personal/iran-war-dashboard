"""Append today's portfolio snapshot to portfolio_history.json.

Idempotent: if today's date already has an entry, replace it. Otherwise append.

Without this step, render.py's diff calculation reads stale baselines and
silently emits "no probability moves" because it cannot find a comparable
prior snapshot.

Usage:
    python3 scripts/append_history.py
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
PORTFOLIO = REPO_ROOT / "portfolio.yaml"
HISTORY = REPO_ROOT / "portfolio_history.json"


def build_snapshot(portfolio: dict, today_iso: str) -> dict:
    """v0.2 snapshot shape: { date, day, engine_version, questions: [{id, probability, ci, label}] }
    The render.py diff path keys off `questions[].id` and `questions[].probability`."""
    questions = []
    for q in portfolio.get("questions", []):
        questions.append({
            "id": q["id"],
            "probability": q["current_probability"],
            "credible_interval_80": q.get("current_credible_interval_80", []),
            "icd203_label": q.get("current_icd203_label"),
            "category": q.get("category"),
            "stakeholder_tags": list(q.get("stakeholder_tags", [])),
        })
    return {
        "date": today_iso,
        "engineVersion": portfolio.get("metadata", {}).get("engine_version"),
        "spec_version": portfolio.get("metadata", {}).get("spec_version"),
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "questions": questions,
    }


def main() -> int:
    if not PORTFOLIO.exists():
        print(f"[append_history] missing {PORTFOLIO}", file=sys.stderr)
        return 1
    portfolio = yaml.safe_load(PORTFOLIO.read_text(encoding="utf-8"))
    today_iso = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    snapshot = build_snapshot(portfolio, today_iso)

    history: list[dict] = []
    if HISTORY.exists():
        try:
            data = json.loads(HISTORY.read_text(encoding="utf-8"))
            if isinstance(data, list):
                history = data
        except json.JSONDecodeError as e:
            print(f"[append_history] WARNING: existing {HISTORY} is malformed JSON ({e}); writing fresh history.", file=sys.stderr)
            history = []

    # Drop any entry for today (idempotent on retry)
    history = [h for h in history if h.get("date") != today_iso]
    history.append(snapshot)
    history.sort(key=lambda h: h.get("date") or "")

    # Atomic write
    tmp = HISTORY.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(history, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp.replace(HISTORY)
    print(f"[append_history] wrote {today_iso} snapshot ({len(snapshot['questions'])} questions); history now {len(history)} entries")
    return 0


if __name__ == "__main__":
    sys.exit(main())
