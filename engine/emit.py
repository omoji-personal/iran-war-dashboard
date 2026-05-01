"""Assemble war-data.json from a Signals object + the previous war-data.json baseline.

Strategy: keep static / long-tail content (timeline, country lists, business
sections, etc.) flowing through from the previous war-data.json untouched.
Only OVERWRITE the keys the engine controls. Append new_events to per-day
arrays. The dashboard never knows the engine exists.
"""
from __future__ import annotations

import copy
import json
from datetime import datetime
from pathlib import Path  # noqa: F401 — used by calibration spine reads below
from typing import Any

from . import __version__
from .advanced import (
    bayesian_evidence_chain,
    counterfactual_no_khamenei_lock,
    counterfactual_no_trump,
    cross_impact_matrix,
    game_theory_equilibrium,
    information_cascade,
    kelly_sizing_for_alphas,
    monte_carlo_simulation,
    multi_horizon_forecast,
    reflexivity_adjustment,
    regime_hazard_curve,
    trump_decision_tree,
    ultraread,
)
from .calibration import build_calibration_spine, load_actuals, load_history
from .compute import (
    alpha_signals,
    all_condition_scores,
    apply_modifiers,
    calibration_methodology,
    ceasefire_deadline,
    ceasefire_extensions_count,
    ceasefire_mode_enabled,
    confidence_methodology,
    contrarian_check,
    crystallization_triggers,
    deep_read,
    derived_indicators,
    exotic_triggers,
    forward_projections,
    historical_analog_projection,
    outcome_probabilities,
    predictive_framework_doc,
    psych_modifiers,
    regime_fracture_probability,
    resolution_probability,
    synthesized_outcome_probabilities,
    tail_risks,
)
from .schema import Signals


def _label_from_date(iso_date: str) -> str:
    """2026-05-01 -> 'May 01' (matches existing dailySeries label format)."""
    dt = datetime.fromisoformat(iso_date)
    return dt.strftime("%b %d")


def _rolling_7day_sum(series: list[int]) -> float:
    if not series:
        return 0.0
    window = series[-7:]
    return round(sum(window) / max(1, len(window)), 1)


def assemble(signals: Signals, previous: dict[str, Any]) -> dict[str, Any]:
    """Merge signals + previous baseline into a fresh war-data.json dict.

    `previous` is mutated-by-copy; the original is not modified.
    """
    out = copy.deepcopy(previous)
    today_label = _label_from_date(signals.meta.date.isoformat())

    # ----- META -----
    out["meta"] = out.get("meta", {})
    out["meta"]["lastUpdated"] = f"{signals.meta.date.isoformat()}T07:00:00-04:00"
    out["meta"]["preWarBaselines"] = {
        "d1Missiles": signals.constants.d1_missiles,
        "preWarOil": signals.constants.pre_war_brent,
        "preWarHormuz": int(signals.constants.pre_war_hormuz),
        "preWarGas": signals.constants.pre_war_gas,
    }
    # Prepend today's notes to existing notes (keep history)
    existing_notes = out["meta"].get("notes", [])
    new_notes = list(signals.meta.notes)
    # If first existing note already references this day, replace it; else prepend
    if existing_notes and existing_notes[0].startswith(f"D{signals.meta.day} "):
        out["meta"]["notes"] = new_notes + existing_notes[1:]
    else:
        out["meta"]["notes"] = new_notes + existing_notes

    # ----- MODE -----
    out["ceasefireMode"] = {"enabled": ceasefire_mode_enabled(signals)}
    out["ceasefireStartIdx"] = signals.constants.ceasefire_start_day

    # ----- DAILY SERIES (append today's row) -----
    ds = out.setdefault("dailySeries", {})
    labels = ds.get("labels", [])
    missiles = ds.get("missiles", [])
    drones = ds.get("drones", [])
    if today_label not in labels:
        labels.append(today_label)
        missiles.append(signals.new_events.daily_series.missiles)
        drones.append(signals.new_events.daily_series.drones)
    else:
        idx = labels.index(today_label)
        missiles[idx] = signals.new_events.daily_series.missiles
        drones[idx] = signals.new_events.daily_series.drones
    ds["labels"] = labels
    ds["missiles"] = missiles
    ds["drones"] = drones
    ds["throughDate"] = signals.meta.date.isoformat()

    # ----- DAILY ROWS (append/replace today's full row) -----
    rows = out.setdefault("dailyRows", [])
    new_row = signals.new_events.daily_row
    if new_row is not None:
        row_dict = {
            "date": new_row.date,
            "missiles": new_row.missiles,
            "drones": new_row.drones,
            "primaryTargets": new_row.primary_targets,
            "capability": new_row.capability,
            "cost": new_row.cost,
            "assessment": new_row.assessment,
        }
        if rows and rows[-1].get("date") == new_row.date:
            rows[-1] = row_dict
        else:
            rows.append(row_dict)

    # ----- CEASEFIRE EVENTS -----
    if signals.new_events.violation is not None and signals.mode.ceasefire_status != "none":
        v = signals.new_events.violation
        viol = out.setdefault("ceasefireViolations", [])
        cf_day_val = signals.meta.cf_day or 0
        incident = {
            "type": v.type,
            "severity": v.severity,
            "actor": v.actor,
            "target": v.target,
            "description": v.description,
        }
        # Find or create today's day-group
        today_day_label = today_label
        existing_group = next((g for g in viol if g.get("day") == today_day_label), None)
        if existing_group:
            existing_group.setdefault("incidents", []).append(incident)
        else:
            viol.append({"day": today_day_label, "cfDay": cf_day_val, "incidents": [incident]})

    if signals.new_events.negotiation is not None and signals.mode.ceasefire_status != "none":
        n = signals.new_events.negotiation
        nego = out.setdefault("ceasefireNegotiations", [])
        nego.append(
            {
                "date": today_label,
                "status": n.status,
                "description": n.description,
            }
        )

    if signals.new_events.recovery_point is not None and signals.mode.ceasefire_status != "none":
        rp = signals.new_events.recovery_point
        rec = out.setdefault("ceasefireEconomicRecovery", {})
        rec_labels = rec.get("labels", [])
        hormuz_daily = rec.get("hormuzDaily", [])
        brent_daily = rec.get("brentDaily", [])
        ships_stranded = rec.get("shipsStranded", [])
        if today_label not in rec_labels:
            rec_labels.append(today_label)
            hormuz_daily.append(rp.hormuz_daily)
            brent_daily.append(rp.brent_daily)
            ships_stranded.append(rp.ships_stranded)
        else:
            idx = rec_labels.index(today_label)
            hormuz_daily[idx] = rp.hormuz_daily
            brent_daily[idx] = rp.brent_daily
            ships_stranded[idx] = rp.ships_stranded
        rec["labels"] = rec_labels
        rec["hormuzDaily"] = hormuz_daily
        rec["brentDaily"] = brent_daily
        rec["shipsStranded"] = ships_stranded
        rec["hormuzPreWar"] = int(signals.constants.pre_war_hormuz)

    # ----- CEASEFIRE DEADLINE -----
    cd = out.setdefault("ceasefireDeadline", {})
    cd["deadline"] = ceasefire_deadline(signals)
    cd["extensions"] = ceasefire_extensions_count(signals)

    # ----- DECISION ENGINE -----
    de = out.setdefault("decisionEngine", {})
    scores = all_condition_scores(signals.condition_inputs, signals.today_scalars.gas_price)

    # 4 conditions
    for k in ("dealAvailability", "usExitPressure", "iranAcceptance", "escalationProximity"):
        existing = de.get(k, {})
        existing["score"] = scores[k]
        de[k] = existing

    # outcome probabilities
    op = outcome_probabilities(scores, signals.today_scalars.coalition_cohesion_score)
    existing_op = de.get("outcomeProbabilities", {})
    existing_op.update(op)
    de["outcomeProbabilities"] = existing_op

    # confidence
    res = resolution_probability(scores)
    existing_conf = de.get("confidence", {})
    existing_conf["resolutionProbability"] = {
        "estimate": res["estimate"],
        "low": res["low"],
        "high": res["high"],
    }
    existing_conf["methodology"] = confidence_methodology(signals, scores)
    de["confidence"] = existing_conf

    # calibration prose
    existing_cal = de.get("calibration", {})
    if "historicalBaseRate" not in existing_cal:
        existing_cal["historicalBaseRate"] = {}
    existing_cal["historicalBaseRate"]["methodology"] = calibration_methodology(signals)
    de["calibration"] = existing_cal

    # scalar indicators
    indicators = derived_indicators(signals)
    indicators["launchRate7DMA"] = _rolling_7day_sum(missiles[-7:]) + _rolling_7day_sum(drones[-7:])
    if signals.constants.d1_missiles > 0:
        indicators["launchRateVsD1"] = round(
            indicators["launchRate7DMA"] / signals.constants.d1_missiles, 3
        )
    existing_ind = de.get("indicators", {})
    existing_ind.update(indicators)
    de["indicators"] = existing_ind

    # engine version stamp (for debugging + calibration spine)
    de["engineVersion"] = __version__

    out["decisionEngine"] = de

    # ----- DEEP DYNAMICS (the superintelligence layer) -----
    # All of this is NEW top-level data the dashboard's P5 visual phase will render.
    # Surfaced under deepDynamics.* so existing keys are untouched.
    deltas = psych_modifiers(signals, scores)
    modified_scores = apply_modifiers(scores, deltas)
    synthesis = synthesized_outcome_probabilities(signals, scores, modified_scores)
    fracture_p = regime_fracture_probability(signals)

    # Compute advanced layers
    alphas = alpha_signals(signals, synthesis)
    alphas_with_kelly = kelly_sizing_for_alphas(alphas)
    bayesian = bayesian_evidence_chain(signals, synthesis["outcome_dist"])
    monte_carlo = monte_carlo_simulation(signals)
    hazard = regime_hazard_curve(signals)
    multi_h = multi_horizon_forecast(signals)
    game_theory = game_theory_equilibrium(signals)
    decision_tree = trump_decision_tree(signals)
    cf_no_trump = counterfactual_no_trump(signals)
    cf_no_khamenei = counterfactual_no_khamenei_lock(signals)
    reflex = reflexivity_adjustment(synthesis["outcome_dist"])

    deep = {
        "engineVersion": __version__,
        # Layer 1: structural + psych
        "psychModifiers": deltas,
        "modifiedConditionScores": modified_scores,
        "regimeFractureProbability": fracture_p,
        # Layer 2: outcome synthesis
        "synthesizedOutcome": synthesis,
        "reflexivityAdjusted": reflex,
        # Layer 3: forward projections + horizons
        "forwardProjections": forward_projections(signals, modified_scores),
        "multiHorizonForecast": multi_h,
        # Layer 4: historical + analogs
        "historicalAnalogProjection": historical_analog_projection(signals),
        # Layer 5: stochastic
        "monteCarloSimulation": monte_carlo,
        "regimeHazardCurve": hazard,
        # Layer 6: bayesian
        "bayesianEvidenceChain": bayesian,
        # Layer 7: game theoretic
        "gameTheoryEquilibrium": game_theory,
        "trumpDecisionTree": decision_tree,
        # Layer 8: counterfactuals
        "counterfactuals": {
            "no_trump": cf_no_trump,
            "no_khamenei_lock": cf_no_khamenei,
        },
        # Layer 9: actionable signals
        "alphaSignals": alphas_with_kelly,
        "crystallizationTriggers": crystallization_triggers(signals),
        "tailRisks": tail_risks(signals, synthesis),
        "exoticTriggers": exotic_triggers(signals),
        "contrarianCheck": contrarian_check(signals, synthesis),
        "crossImpactMatrix": cross_impact_matrix(),
        # Layer 10: cascade scenarios
        "informationCascades": {
            "khamenei_dies": information_cascade("khamenei_dies"),
            "centcom_strike_grid": information_cascade("centcom_strike_grid"),
            "iran_accepts_deal": information_cascade("iran_accepts_deal"),
        },
        # Layer 11: narratives
        "deepRead": deep_read(signals, modified_scores, deltas),
        "predictiveFrameworkDoc": predictive_framework_doc(),
        # Echo input layers so dashboard can render them
        "stakeholders": signals.stakeholders.model_dump(),
        "iranRegimeDynamics": signals.iran_regime_dynamics.model_dump(),
        "usDynamics": signals.us_dynamics.model_dump(),
        "iranDeepDynamics": signals.iran_deep_dynamics.model_dump(),
        "worldDynamics": signals.world_dynamics.model_dump(),
        "historicalIdeology": signals.historical_ideology.model_dump(),
        "exoticSignals": signals.exotic_signals.model_dump(),
        "historicalAnalogs": signals.historical_analogs.model_dump(),
    }
    # Apex narrative needs the whole bag
    deep["ultraRead"] = ultraread(signals, deep)

    out["deepDynamics"] = deep

    # Calibration spine (P2)
    history_path = Path(__file__).resolve().parent.parent / "engine_history.json"
    actuals_path = Path(__file__).resolve().parent.parent / "actuals.yaml"
    history_loaded = load_history(history_path)
    actuals_loaded = load_actuals(actuals_path)
    out["calibrationSpine"] = build_calibration_spine(history_loaded, actuals_loaded)

    return out


def write_atomic(path: Path, data: dict[str, Any]) -> None:
    """Write JSON atomically (tmp + rename)."""
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(path)


def append_history_snapshot(history_path: Path, signals: Signals, computed: dict[str, Any]) -> None:
    """Append a calibration-spine snapshot. Idempotent: replaces today's entry if present."""
    history: list[dict[str, Any]] = []
    if history_path.exists():
        try:
            history = json.loads(history_path.read_text())
            if not isinstance(history, list):
                history = []
        except json.JSONDecodeError:
            history = []
    snapshot = {
        "date": signals.meta.date.isoformat(),
        "day": signals.meta.day,
        "engineVersion": __version__,
        "scores": {
            "dealAvailability": computed["decisionEngine"]["dealAvailability"]["score"],
            "usExitPressure": computed["decisionEngine"]["usExitPressure"]["score"],
            "iranAcceptance": computed["decisionEngine"]["iranAcceptance"]["score"],
            "escalationProximity": computed["decisionEngine"]["escalationProximity"]["score"],
        },
        "outcomeProbabilities": computed["decisionEngine"]["outcomeProbabilities"],
        "resolutionProbability": computed["decisionEngine"]["confidence"]["resolutionProbability"],
    }
    # Replace if today's snapshot already exists; else append
    existing_idx = next(
        (i for i, h in enumerate(history) if h.get("date") == snapshot["date"]), None
    )
    if existing_idx is not None:
        history[existing_idx] = snapshot
    else:
        history.append(snapshot)
    write_atomic(history_path, history)


def write_signal_snapshot(snapshot_dir: Path, signals: Signals) -> Path:
    """Write per-emit snapshot of signals.yaml for backtesting. Returns path written."""
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    path = snapshot_dir / f"{signals.meta.date.isoformat()}.yaml"
    # Pydantic dump -> dict -> yaml
    import yaml as _yaml
    data = signals.model_dump(mode="json")
    path.write_text(_yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")
    return path
