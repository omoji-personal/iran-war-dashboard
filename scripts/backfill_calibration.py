"""R11: Backfill workflow — replay engine on past snapshots when outcomes resolve.

When you mark a resolved outcome in actuals.yaml, this script:
  1. Replays the current engine on every signals_history/<date>.yaml that
     pre-dates the resolution.
  2. Records the engine's predicted P(resolved-bucket) on each replay.
  3. Computes Brier scores per snapshot + aggregate calibration metrics.
  4. Writes docs/calibration-{engine_version}.json.

This is the only way the calibration spine ever becomes meaningful.

Usage:
    # 1. Edit actuals.yaml to record an outcome:
    #    resolved:
    #      - outcome: deal
    #        date: 2026-08-15
    #        notes: "Iran accepts deferred-nuclear framework via Pakistan"
    # 2. Run:
    python -m scripts.backfill_calibration
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
ACTUALS_PATH = REPO_ROOT / "actuals.yaml"
SIGNALS_HISTORY_DIR = REPO_ROOT / "signals_history"
OUT_PATH = REPO_ROOT / "docs" / f"calibration-{__version__}.json"


def replay_distribution(snapshot_path: Path) -> dict[str, float]:
    raw = yaml.safe_load(snapshot_path.read_text())
    signals = Signals(**raw)
    base = all_condition_scores(signals.condition_inputs, signals.today_scalars.gas_price)
    deltas = psych_modifiers(signals, base)
    modified = apply_modifiers(base, deltas)
    syn = synthesized_outcome_probabilities(signals, base, modified)
    return syn["outcome_dist"]


def brier(p: float, actual: int) -> float:
    return (p - actual) ** 2


def backfill() -> dict:
    actuals = yaml.safe_load(ACTUALS_PATH.read_text()) or {"resolved": []}
    resolved = actuals.get("resolved", [])
    if not resolved:
        return {
            "engine_version": __version__,
            "resolved_count": 0,
            "message": "No resolved outcomes in actuals.yaml — nothing to backfill.",
            "next_step": "Mark a resolved outcome in actuals.yaml when one materializes.",
        }

    snapshots = sorted(SIGNALS_HISTORY_DIR.glob("*.yaml")) if SIGNALS_HISTORY_DIR.exists() else []
    per_outcome = []
    all_briers = []

    for r in resolved:
        outcome_name = r["outcome"]
        actual_date = r["date"]
        relevant = [snap for snap in snapshots if snap.stem < actual_date]
        per_pred = []
        for snap in relevant:
            try:
                dist = replay_distribution(snap)
            except Exception as e:
                per_pred.append({"date": snap.stem, "error": str(e)})
                continue
            p = dist.get(outcome_name, 0.0)
            b = brier(p, 1)
            per_pred.append({
                "date": snap.stem,
                "predicted_p": round(p, 3),
                "brier": round(b, 3),
            })
            all_briers.append(b)
        per_outcome.append({
            "outcome": outcome_name,
            "actual_date": actual_date,
            "n_predictions": len(per_pred),
            "mean_predicted_p": round(
                sum(p.get("predicted_p", 0) for p in per_pred) / max(1, len(per_pred)), 3
            ),
            "mean_brier": round(
                sum(p.get("brier", 0) for p in per_pred) / max(1, len(per_pred)), 3
            ),
            "predictions": per_pred,
        })

    aggregate_brier = round(sum(all_briers) / len(all_briers), 3) if all_briers else None

    return {
        "engine_version": __version__,
        "resolved_count": len(resolved),
        "n_snapshots_total": len(snapshots),
        "n_predictions_evaluated": len(all_briers),
        "aggregate_brier": aggregate_brier,
        "per_outcome": per_outcome,
        "interpretation": (
            "Brier ranges 0..1, lower = better. <0.10 is well-calibrated for "
            "high-confidence predictions. 0.25 is the worst case for a 50% prediction."
        ),
    }


def main() -> None:
    out = backfill()
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=2))
    print(f"\nwritten to {OUT_PATH}")


if __name__ == "__main__":
    main()
