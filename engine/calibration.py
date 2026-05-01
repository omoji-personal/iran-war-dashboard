"""Calibration spine — predicted-vs-actual tracking + Brier scoring.

When an outcome materializes, mark it in actuals.yaml. Engine then computes:
  - Brier score for each historical prediction
  - Calibration plot data (predicted P bucket vs actual frequency)
  - Bias direction (model running high or low)
  - Confidence-interval coverage (X% of intervals contained truth)

For ongoing/unresolved outcomes, just surfaces the prediction time-series.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

import yaml


def load_history(path: Path) -> list[dict]:
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except json.JSONDecodeError:
        return []


def load_actuals(path: Path) -> dict:
    """Load resolved-outcome marks. Schema:

    resolved:
      - outcome: deal | escalation | protracted | intervention
        date: 2026-08-15
        notes: ""
    """
    if not path.exists():
        return {"resolved": []}
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        return {"resolved": []}
    raw.setdefault("resolved", [])
    return raw


def brier_score(predicted_p: float, actual: int) -> float:
    """Brier score for binary outcome. Lower = better. Range [0, 1]."""
    return (predicted_p - actual) ** 2


def compute_calibration(history: list[dict], actuals: dict) -> dict:
    """For each resolved outcome, compute Brier on every historical prediction
    that pre-dates it. Returns aggregate metrics + per-outcome detail.
    """
    resolved = actuals.get("resolved", [])
    if not resolved or not history:
        return {
            "resolved_count": len(resolved),
            "history_count": len(history),
            "brier_aggregate": None,
            "calibration_buckets": None,
            "bias_direction": None,
            "per_outcome": [],
        }

    per_outcome = []
    all_briers = []
    bucket_counts = {0: [0, 0], 1: [0, 0], 2: [0, 0], 3: [0, 0], 4: [0, 0],
                     5: [0, 0], 6: [0, 0], 7: [0, 0], 8: [0, 0], 9: [0, 0]}

    for r in resolved:
        outcome_name = r["outcome"]
        actual_date = r["date"]
        # Predictions made before actual date
        relevant_history = [h for h in history if h.get("date", "") < actual_date]
        per_pred = []
        for h in relevant_history:
            outcome_dist = (h.get("outcomeProbabilities") or {})
            # Map outcome names -> dist keys
            key_map = {
                "deal": "negotiatedResolution",
                "escalation": "escalationCatastrophe",
                "protracted": "protractedContinuation",
                "intervention": "internationalIntervention",
            }
            key = key_map.get(outcome_name, outcome_name)
            predicted_p = outcome_dist.get(key, 0.0)
            actual = 1  # outcome happened
            b = brier_score(predicted_p, actual)
            per_pred.append({"date": h["date"], "predicted_p": predicted_p, "brier": b})
            all_briers.append(b)
            # Calibration bucket (decile of predicted probability)
            bucket = min(9, int(predicted_p * 10))
            bucket_counts[bucket][0] += 1  # predictions
            bucket_counts[bucket][1] += actual  # actuals
        per_outcome.append({
            "outcome": outcome_name,
            "actual_date": actual_date,
            "n_predictions": len(per_pred),
            "mean_predicted_p": round(sum(p["predicted_p"] for p in per_pred) / max(1, len(per_pred)), 3),
            "mean_brier": round(sum(p["brier"] for p in per_pred) / max(1, len(per_pred)), 3),
            "predictions": per_pred[-30:],  # last 30 for chart
        })

    aggregate_brier = round(sum(all_briers) / len(all_briers), 3) if all_briers else None

    # Calibration buckets — predicted-bucket-mean vs actual-frequency
    calibration_buckets = []
    for b in range(10):
        n, a = bucket_counts[b]
        if n > 0:
            calibration_buckets.append({
                "bucket": f"{b*10}-{b*10+10}%",
                "n": n,
                "actual_freq": round(a / n, 3),
                "predicted_mid": (b * 0.1) + 0.05,
            })

    # Bias: average (predicted - actual) across all
    bias = None
    if all_briers:
        signed_errors = []
        for r in resolved:
            outcome_name = r["outcome"]
            actual_date = r["date"]
            relevant = [h for h in history if h.get("date", "") < actual_date]
            for h in relevant:
                outcome_dist = h.get("outcomeProbabilities") or {}
                key_map = {
                    "deal": "negotiatedResolution",
                    "escalation": "escalationCatastrophe",
                    "protracted": "protractedContinuation",
                    "intervention": "internationalIntervention",
                }
                key = key_map.get(outcome_name, outcome_name)
                predicted_p = outcome_dist.get(key, 0.0)
                signed_errors.append(predicted_p - 1)  # negative = under-predicted
        if signed_errors:
            mean_signed = sum(signed_errors) / len(signed_errors)
            bias = "underpredicted" if mean_signed < -0.05 else "overpredicted" if mean_signed > 0.05 else "well-calibrated"

    return {
        "resolved_count": len(resolved),
        "history_count": len(history),
        "brier_aggregate": aggregate_brier,
        "calibration_buckets": calibration_buckets,
        "bias_direction": bias,
        "per_outcome": per_outcome,
    }


def build_calibration_spine(history: list[dict], actuals: dict) -> dict:
    """Top-level surface for war-data.json.calibrationSpine."""
    cal = compute_calibration(history, actuals)

    # Time series of resolution probability (the dashboard's headline number)
    resolution_series = [
        {
            "date": h.get("date"),
            "day": h.get("day"),
            "estimate": (h.get("resolutionProbability") or {}).get("estimate"),
            "low": (h.get("resolutionProbability") or {}).get("low"),
            "high": (h.get("resolutionProbability") or {}).get("high"),
        }
        for h in history
    ]

    # Time series of each outcome bucket
    outcome_series_keys = ["negotiatedResolution", "escalationCatastrophe", "protractedContinuation", "internationalIntervention", "other"]
    outcome_series = {k: [] for k in outcome_series_keys}
    for h in history:
        op = h.get("outcomeProbabilities") or {}
        for k in outcome_series_keys:
            outcome_series[k].append({"date": h.get("date"), "value": op.get(k)})

    return {
        "spineLength": len(history),
        "calibration": cal,
        "resolutionProbabilitySeries": resolution_series,
        "outcomeBucketSeries": outcome_series,
        "actualsKnown": cal["resolved_count"],
    }
