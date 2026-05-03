"""R20: Engine-version diff harness.

When `engine.__version__` bumps, replay every snapshot in engine_history.json
through the current engine and report:
  (a) average shift per outcome bucket,
  (b) any snapshot whose top-bucket changed.

Block deploys where shifts exceed thresholds without an explicit changelog
entry. (CI integration TBD — for now, run manually before bumping engine
version.)

Usage:
    python -m scripts.engine_version_diff
"""
from __future__ import annotations

import json
from pathlib import Path

import yaml

from engine import __version__
from engine.compute import (
    all_condition_scores,
    apply_modifiers,
    psych_modifiers,
    synthesized_outcome_probabilities,
)
from engine.schema import Signals


REPO_ROOT = Path(__file__).resolve().parent.parent
ENGINE_HISTORY = REPO_ROOT / "engine_history.json"
SIGNALS_HISTORY_DIR = REPO_ROOT / "signals_history"


def replay_snapshot(signals_yaml_path: Path) -> dict:
    """Replay engine on a snapshot's signals.yaml; return outcome distribution."""
    raw = yaml.safe_load(signals_yaml_path.read_text())
    signals = Signals(**raw)
    base = all_condition_scores(signals.condition_inputs, signals.today_scalars.gas_price)
    deltas = psych_modifiers(signals, base)
    modified = apply_modifiers(base, deltas)
    syn = synthesized_outcome_probabilities(signals, base, modified)
    return syn["outcome_dist"]


def diff_snapshots(prev_history: list[dict], current_engine_version: str) -> dict:
    """For each prior snapshot, replay through current engine + compare."""
    diffs = []
    for entry in prev_history:
        date = entry.get("date")
        prev_op = entry.get("outcomeProbabilities", {})
        # Map prev keys → standard buckets
        prev_buckets = {
            "deal": prev_op.get("negotiatedResolution", 0.0),
            "escalation": prev_op.get("escalationCatastrophe", 0.0),
            "protracted": prev_op.get("protractedContinuation", 0.0),
            "intervention": prev_op.get("internationalIntervention", 0.0),
        }
        snapshot_yaml = SIGNALS_HISTORY_DIR / f"{date}.yaml"
        if not snapshot_yaml.exists():
            diffs.append({"date": date, "skipped": "no signals snapshot"})
            continue
        try:
            new_buckets = replay_snapshot(snapshot_yaml)
        except Exception as e:
            diffs.append({"date": date, "error": str(e)})
            continue
        delta = {}
        for k in set(prev_buckets) | set(new_buckets):
            d = (new_buckets.get(k, 0.0) - prev_buckets.get(k, 0.0)) * 100
            delta[k] = round(d, 1)
        prev_top = max(prev_buckets.items(), key=lambda kv: kv[1])[0] if prev_buckets else None
        new_top = max(new_buckets.items(), key=lambda kv: kv[1])[0] if new_buckets else None
        diffs.append({
            "date": date,
            "prev_engine_version": entry.get("engineVersion"),
            "prev_top": prev_top,
            "new_top": new_top,
            "top_changed": prev_top != new_top,
            "delta_pp": delta,
            "max_abs_pp": max(abs(v) for v in delta.values()) if delta else 0.0,
        })
    return {
        "current_engine_version": current_engine_version,
        "n_snapshots": len(prev_history),
        "n_top_changes": sum(1 for d in diffs if d.get("top_changed")),
        "average_max_pp": round(
            sum(d.get("max_abs_pp", 0) for d in diffs) / max(1, len(diffs)),
            2,
        ),
        "diffs": diffs,
    }


def main() -> None:
    if not ENGINE_HISTORY.exists():
        print(f"no engine_history.json at {ENGINE_HISTORY} — nothing to diff")
        return
    prev = json.loads(ENGINE_HISTORY.read_text())
    if not isinstance(prev, list):
        prev = []
    if not prev:
        print("engine_history.json is empty — nothing to diff against")
        return
    report = diff_snapshots(prev, __version__)
    print(json.dumps(report, indent=2))
    out_path = REPO_ROOT / "docs" / f"engine-diff-{__version__}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2))
    print(f"\nwritten to {out_path}")
    if report["n_top_changes"] > 0:
        print(f"\nWARNING: {report['n_top_changes']} snapshot(s) had top-bucket change. "
              "Review before bumping engine version.")


if __name__ == "__main__":
    main()
