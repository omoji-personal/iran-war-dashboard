"""Unit tests for engine.compute — the math is the contract."""
from __future__ import annotations

from datetime import date

import pytest

from engine.compute import (
    apply_modifiers,
    all_condition_scores,
    deal_availability,
    escalation_proximity,
    historical_analog_projection,
    iran_acceptance,
    outcome_probabilities,
    psych_modifiers,
    regime_fracture_probability,
    resolution_probability,
    synthesized_outcome_probabilities,
    us_exit_pressure,
)
from engine.schema import (
    DealInputs,
    EscalationInputs,
    IranAcceptanceInputs,
    Meta,
    Mode,
    Signals,
    TodayScalars,
    UsExitInputs,
)


def _minimal_signals(**overrides) -> Signals:
    base = dict(
        meta=Meta(day=63, cf_day=24, date=date(2026, 5, 1), notes=["test"]),
        mode=Mode(ceasefire_status="hollow"),
        today_scalars=TodayScalars(brent=114.0, gas_price=4.30, hormuz_vessels=7,
                                   us_kia=15, us_wounded=520, us_aircraft_lost=7,
                                   lebanon_killed=2521, iran_civ_killed_hrana=3540,
                                   coalition_cohesion_score=2.5),
    )
    base.update(overrides)
    return Signals(**base)


# ---------- Condition scores ----------

def test_deal_availability_override_returns_override():
    assert deal_availability(DealInputs(score_override=0.42)) == 0.42


def test_deal_availability_baseline():
    score = deal_availability(DealInputs(iran_proposal_active=False, us_acceptance_signal=0.0, nuclear_gap_pp=0))
    assert 0.15 <= score <= 0.25


def test_deal_availability_iran_proposal_lifts():
    base = deal_availability(DealInputs(iran_proposal_active=False))
    boosted = deal_availability(DealInputs(iran_proposal_active=True))
    assert boosted > base


def test_us_exit_pressure_gas_threshold_lifts():
    low = us_exit_pressure(UsExitInputs(gas_pain_above_threshold=False), gas_price=3.50)
    high = us_exit_pressure(UsExitInputs(gas_pain_above_threshold=True), gas_price=4.30)
    assert high > low


def test_iran_acceptance_khamenei_vow_drags():
    high = iran_acceptance(IranAcceptanceInputs(khamenei_public_vow_against=False))
    low = iran_acceptance(IranAcceptanceInputs(khamenei_public_vow_against=True))
    assert high > low + 0.20


def test_escalation_proximity_centcom_lifts():
    low = escalation_proximity(EscalationInputs(centcom_briefed=False))
    high = escalation_proximity(EscalationInputs(centcom_briefed=True))
    assert high > low


def test_all_condition_scores_keys():
    s = _minimal_signals()
    scores = all_condition_scores(s.condition_inputs, s.today_scalars.gas_price)
    assert set(scores.keys()) == {
        "dealAvailability", "usExitPressure", "iranAcceptance", "escalationProximity"
    }


# ---------- Outcome probabilities ----------

def test_outcome_probabilities_sum_to_one():
    scores = {
        "dealAvailability": 0.42,
        "usExitPressure": 0.64,
        "iranAcceptance": 0.30,
        "escalationProximity": 0.42,
    }
    op = outcome_probabilities(scores)
    total = sum(op.values())
    assert abs(total - 1.0) < 0.01, f"outcomes sum to {total}, expected ~1.0"


def test_outcome_probabilities_high_deal_yields_high_negotiated():
    high = outcome_probabilities({"dealAvailability": 0.9, "usExitPressure": 0.9, "iranAcceptance": 0.9, "escalationProximity": 0.1})
    low = outcome_probabilities({"dealAvailability": 0.1, "usExitPressure": 0.1, "iranAcceptance": 0.1, "escalationProximity": 0.9})
    assert high["negotiatedResolution"] > low["negotiatedResolution"]
    assert low["escalationCatastrophe"] > high["escalationCatastrophe"]


def test_resolution_probability_in_bounds():
    res = resolution_probability({"dealAvailability": 0.5, "usExitPressure": 0.5, "iranAcceptance": 0.5, "escalationProximity": 0.5})
    assert 0 <= res["estimate"] <= 100
    assert res["low"] <= res["estimate"] <= res["high"]


# ---------- Psych modifiers ----------

def test_psych_modifiers_all_in_bounds():
    s = _minimal_signals()
    scores = all_condition_scores(s.condition_inputs, s.today_scalars.gas_price)
    deltas = psych_modifiers(s, scores)
    for k, v in deltas.items():
        assert -0.30 <= v <= 0.30, f"{k} delta {v} out of [-0.30, 0.30]"


def test_apply_modifiers_clamps_to_unit_interval():
    scores = {"dealAvailability": 0.9, "usExitPressure": 0.9, "iranAcceptance": 0.9, "escalationProximity": 0.9}
    deltas = {"dealAvailability": 0.5, "usExitPressure": -0.9, "iranAcceptance": 0.0, "escalationProximity": 0.5}
    adj = apply_modifiers(scores, deltas)
    assert all(0.0 <= v <= 1.0 for v in adj.values())


def test_psych_iran_acceptance_drops_under_khamenei_lock():
    s = _minimal_signals()
    base = all_condition_scores(s.condition_inputs, s.today_scalars.gas_price)
    deltas = psych_modifiers(s, base)
    # Default Khamenei profile has religious_zeal=0.95 + public_commitment=0.95 → strong negative
    assert deltas["iranAcceptance"] < 0


# ---------- Regime fracture ----------

def test_regime_fracture_probability_in_unit_interval():
    s = _minimal_signals()
    fp = regime_fracture_probability(s)
    assert 0.0 <= fp <= 1.0


def test_regime_fracture_increases_with_pressure():
    from engine.schema import IranRegimeDynamics
    low = _minimal_signals(iran_regime_dynamics=IranRegimeDynamics(
        population_restiveness=0.1, population_war_fatigue=0.1,
        economic_pain_index=0.1, regime_brittleness=0.1, regime_grip_strength=0.95
    ))
    high = _minimal_signals(iran_regime_dynamics=IranRegimeDynamics(
        population_restiveness=0.9, population_war_fatigue=0.9,
        economic_pain_index=0.9, regime_brittleness=0.9, regime_grip_strength=0.3
    ))
    assert regime_fracture_probability(high) > regime_fracture_probability(low) + 0.10


# ---------- Historical analog projection ----------

def test_historical_analog_projection_returns_distribution():
    s = _minimal_signals()
    proj = historical_analog_projection(s)
    assert "outcome_dist" in proj
    assert "median_resolution_days" in proj
    assert proj["top_analog"] is not None


# ---------- Synthesis ----------

def test_synthesized_outcome_returns_normalized_distribution():
    s = _minimal_signals()
    base = all_condition_scores(s.condition_inputs, s.today_scalars.gas_price)
    deltas = psych_modifiers(s, base)
    modified = apply_modifiers(base, deltas)
    syn = synthesized_outcome_probabilities(s, base, modified)
    total = sum(syn["outcome_dist"].values())
    assert 0.97 <= total <= 1.03, f"synth distribution sums to {total}, expected ~1.0"
    assert "confidence_score" in syn
    assert 0.0 <= syn["confidence_score"] <= 1.0
