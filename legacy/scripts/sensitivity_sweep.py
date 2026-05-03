"""R9: Sensitivity sweep across the engine's magic-number coefficients.

Sweeps each coefficient ±50% around its nominal value and records which
outputs (synthesized outcome distribution + headline resolution probability)
move by more than 5pp. High-leverage coefficients need either citation or
interval-typed values that propagate uncertainty.

Output: docs/sensitivity-{engine_version}.json

Usage:
    python -m scripts.sensitivity_sweep
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

import yaml

from engine import __version__
from engine.compute import (
    all_condition_scores,
    apply_modifiers,
    outcome_probabilities,
    psych_modifiers,
    resolution_probability,
    synthesized_outcome_probabilities,
)
from engine.schema import Signals


REPO_ROOT = Path(__file__).resolve().parent.parent
SIGNALS_PATH = REPO_ROOT / "signals.yaml"
OUT_PATH = REPO_ROOT / "docs" / f"sensitivity-{__version__}.json"


def _baseline(s: Signals) -> dict:
    base = all_condition_scores(s.condition_inputs, s.today_scalars.gas_price)
    deltas = psych_modifiers(s, base)
    modified = apply_modifiers(base, deltas)
    syn = synthesized_outcome_probabilities(s, base, modified)
    res = resolution_probability(base)
    return {
        "outcome_dist": syn["outcome_dist"],
        "resolution_estimate": res["estimate"],
    }


def _delta(baseline: dict, perturbed: dict) -> dict:
    out = {"buckets_pp": {}, "resolution_pp": 0}
    for k, v in perturbed["outcome_dist"].items():
        out["buckets_pp"][k] = round((v - baseline["outcome_dist"].get(k, 0.0)) * 100, 1)
    out["resolution_pp"] = perturbed["resolution_estimate"] - baseline["resolution_estimate"]
    out["max_abs_pp"] = max(
        [abs(out["resolution_pp"])] + [abs(v) for v in out["buckets_pp"].values()]
    )
    return out


def sweep() -> dict:
    raw = yaml.safe_load(SIGNALS_PATH.read_text())
    signals = Signals(**raw)
    baseline = _baseline(signals)

    results = []

    # Sweep stakeholder fields that we know flow into psych_modifiers
    sweep_targets = [
        ("stakeholders.trump.ego_size", lambda s, v: setattr(s.stakeholders.trump, "ego_size", v)),
        ("stakeholders.trump.public_commitment", lambda s, v: setattr(s.stakeholders.trump, "public_commitment", v)),
        ("stakeholders.khamenei.religious_zeal", lambda s, v: setattr(s.stakeholders.khamenei, "religious_zeal", v)),
        ("stakeholders.khamenei.public_commitment", lambda s, v: setattr(s.stakeholders.khamenei, "public_commitment", v)),
        ("stakeholders.hegseth.risk_tolerance", lambda s, v: setattr(s.stakeholders.hegseth, "risk_tolerance", v)),
        ("us_dynamics.gas_price_pain_index", lambda s, v: setattr(s.us_dynamics, "gas_price_pain_index", v)),
        ("us_dynamics.midterms_proximity_days", lambda s, v: setattr(s.us_dynamics, "midterms_proximity_days", int(v))),
        ("us_dynamics.christian_nationalist_pressure", lambda s, v: setattr(s.us_dynamics, "christian_nationalist_pressure", v)),
        ("iran_regime_dynamics.regime_brittleness", lambda s, v: setattr(s.iran_regime_dynamics, "regime_brittleness", v)),
        ("iran_regime_dynamics.regime_grip_strength", lambda s, v: setattr(s.iran_regime_dynamics, "regime_grip_strength", v)),
        ("iran_deep_dynamics.oil_revenue_collapse_pct", lambda s, v: setattr(s.iran_deep_dynamics, "oil_revenue_collapse_pct", v)),
        ("iran_deep_dynamics.khamenei_health_concern", lambda s, v: setattr(s.iran_deep_dynamics, "khamenei_health_concern", v)),
        ("world_dynamics.gcc_realignment", lambda s, v: setattr(s.world_dynamics, "gcc_realignment", v)),
        ("world_dynamics.un_security_council_paralysis", lambda s, v: setattr(s.world_dynamics, "un_security_council_paralysis", v)),
        ("historical_ideology.trump_jcpoa_personal_animus", lambda s, v: setattr(s.historical_ideology, "trump_jcpoa_personal_animus", v)),
    ]

    for path, setter in sweep_targets:
        # Read current (nominal) value
        attr_path = path.split(".")
        cur = signals
        for p in attr_path[:-1]:
            cur = getattr(cur, p)
        nominal = getattr(cur, attr_path[-1])
        if isinstance(nominal, bool):
            continue

        # Sweep ±50%, but stay in [0, 1] for prob-typed fields and ≥1 for day-typed
        nominal_f = float(nominal)
        lo_v = max(0.0, nominal_f * 0.5)
        hi_v = min(1.0, nominal_f * 1.5) if nominal_f <= 1.0 else nominal_f * 1.5

        per_field = {"path": path, "nominal": nominal_f}
        for label, v in (("low_50pct", lo_v), ("high_150pct", hi_v)):
            s_alt = signals.model_copy(deep=True)
            setter(s_alt, v)
            try:
                perturbed = _baseline(s_alt)
                per_field[label] = _delta(baseline, perturbed)
            except Exception as e:
                per_field[label] = {"error": str(e)}
        # Mark high-leverage
        max_pp = max(
            per_field.get("low_50pct", {}).get("max_abs_pp", 0),
            per_field.get("high_150pct", {}).get("max_abs_pp", 0),
        )
        per_field["high_leverage"] = max_pp >= 5.0
        results.append(per_field)

    results.sort(key=lambda r: -max(r.get("low_50pct", {}).get("max_abs_pp", 0),
                                    r.get("high_150pct", {}).get("max_abs_pp", 0)))
    return {
        "engine_version": __version__,
        "baseline": baseline,
        "n_targets": len(results),
        "n_high_leverage": sum(1 for r in results if r.get("high_leverage")),
        "results": results,
    }


if __name__ == "__main__":
    out = sweep()
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(out, indent=2))
    print(f"sensitivity sweep written to {OUT_PATH}")
    print(f"  baseline outcome_dist: {out['baseline']['outcome_dist']}")
    print(f"  high-leverage targets: {out['n_high_leverage']} / {out['n_targets']}")
    for r in out["results"][:5]:
        print(f"    {r['path']:60s} max_pp={max(r.get('low_50pct', {}).get('max_abs_pp', 0), r.get('high_150pct', {}).get('max_abs_pp', 0)):.1f}")
