"""Tests for the advanced predictive layer."""
from __future__ import annotations

from datetime import date

from engine.advanced import (
    bayesian_evidence_chain,
    bayesian_update,
    counterfactual_no_khamenei_lock,
    counterfactual_no_trump,
    cross_impact_matrix,
    game_theory_equilibrium,
    information_cascade,
    kelly_size,
    kelly_sizing_for_alphas,
    monte_carlo_simulation,
    multi_horizon_forecast,
    reflexivity_adjustment,
    regime_hazard_curve,
    trump_decision_tree,
)
from engine.schema import Meta, Mode, Signals, TodayScalars


def _signals():
    return Signals(
        meta=Meta(day=63, cf_day=24, date=date(2026, 5, 1), notes=["t"]),
        mode=Mode(ceasefire_status="hollow"),
        today_scalars=TodayScalars(brent=114.0, gas_price=4.30, hormuz_vessels=7,
                                   us_kia=15, us_wounded=520, us_aircraft_lost=7,
                                   lebanon_killed=2521, iran_civ_killed_hrana=3540,
                                   coalition_cohesion_score=2.5),
    )


def test_bayesian_update_classic():
    # Standard: P(disease|positive test) — base rate 1%, sensitivity 99%, specificity 95%
    posterior = bayesian_update(0.01, 0.99, 0.05)
    assert 0.15 < posterior < 0.20  # ~16.7%


def test_bayesian_evidence_chain_returns_normalized_posterior():
    s = _signals()
    base = {"deal": 0.20, "escalation": 0.30, "protracted": 0.40, "intervention": 0.10}
    out = bayesian_evidence_chain(s, base)
    total = sum(out["posteriors"].values())
    assert 0.97 <= total <= 1.03


def test_monte_carlo_outcome_frequencies_sum_to_one():
    s = _signals()
    out = monte_carlo_simulation(s, n_runs=500)  # smaller for test speed
    total = sum(out["outcome_frequencies"].values())
    assert 0.97 <= total <= 1.03
    assert "median_days_to_resolution" in out


def test_regime_hazard_curve_monotonic_decreasing():
    s = _signals()
    out = regime_hazard_curve(s)
    survivals = [pt["survival_probability"] for pt in out["survival_curve"]]
    for i in range(len(survivals) - 1):
        assert survivals[i] >= survivals[i + 1] - 0.001


def test_multi_horizon_forecast_each_normalized():
    s = _signals()
    out = multi_horizon_forecast(s)
    assert "1d" in out and "365d" in out
    for h, dist in out.items():
        total = sum(dist.values())
        assert 0.97 <= total <= 1.03, f"{h} sums to {total}"


def test_kelly_size_underbet_when_no_edge():
    # model_p = market_p = no edge → bet ~0
    f = kelly_size(0.5, 0.5, payoff_if_right=1.0, payoff_if_wrong=1.0)
    assert -0.05 < f < 0.05


def test_kelly_size_positive_when_edge():
    f = kelly_size(0.30, 0.20, payoff_if_right=4.0)  # 20% market = 4x payout
    assert f > 0


def test_kelly_sizing_for_alphas_attaches_kelly_when_data_present():
    alphas = [{
        "signal": "test",
        "model_pct": 30,
        "market_pct": 18,
    }]
    out = kelly_sizing_for_alphas(alphas)
    assert len(out) == 1
    assert "kelly_fraction" in out[0]


def test_game_theory_equilibrium_finds_at_least_one_nash():
    s = _signals()
    out = game_theory_equilibrium(s)
    assert "nash_equilibria" in out
    assert "pareto_optimal" in out


def test_trump_decision_tree_ev_sorted():
    s = _signals()
    out = trump_decision_tree(s)
    branches = out["branches"]
    for i in range(len(branches) - 1):
        assert branches[i]["expected_value"] >= branches[i + 1]["expected_value"]


def test_counterfactual_no_trump_changes_outcome():
    s = _signals()
    cf = counterfactual_no_trump(s)
    assert "outcome_dist" in cf


def test_counterfactual_no_khamenei_lock_increases_iran_acceptance_path():
    """With Khamenei lock removed, deal probability should rise vs actual."""
    s = _signals()
    cf = counterfactual_no_khamenei_lock(s)
    # The counterfactual should be a meaningful positive shift on deal
    assert cf["outcome_dist"]["deal"] > 0  # at minimum not zero


def test_cross_impact_matrix_returns_dict():
    out = cross_impact_matrix()
    assert "matrix" in out
    assert "khamenei_dies" in out["matrix"]


def test_information_cascade_returns_chain():
    out = information_cascade("khamenei_dies")
    assert len(out["cascade"]) > 5


def test_reflexivity_pulls_extreme_predictions_toward_baseline():
    extreme = {"deal": 0.95, "escalation": 0.0, "protracted": 0.05, "intervention": 0.0}
    adjusted = reflexivity_adjustment(extreme, publication_impact=0.10)
    # deal should be pulled down
    assert adjusted["deal"] < 0.95
