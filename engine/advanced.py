"""Advanced predictive models — game theory, Bayesian updating, Monte Carlo,
hazard modeling, reflexivity, Kelly sizing.

This is the 'no constraints' layer the user requested: every prediction angle
that meaningfully improves forecast quality, surfaced in war-data.json so the
dashboard can render them.

Each function is pure (signals + history -> structured output). Side-effect
free. Trivially testable.
"""
from __future__ import annotations

import math
import random
from typing import Optional

from .compute import (
    all_condition_scores,
    apply_modifiers,
    historical_analog_projection,
    psych_modifiers,
    regime_fracture_probability,
    synthesized_outcome_probabilities,
)
from .schema import Signals


# ============================================================================
# 1. GAME THEORY — Nash equilibrium between US and Iran
# ============================================================================

def game_theory_equilibrium(s: Signals) -> dict:
    """2-player simultaneous-move game between US and Iran.

    LAYER DISCIPLINE (R8): this function emits *utility-based strategy analysis*,
    NOT probability mass. It does not contribute to any outcome distribution.
    It reads stakeholder fields (Trump ego, Khamenei zeal, gas pain) to construct
    payoff matrices — these are independent of psych_modifiers' delta application
    to condition scores. Both functions reading the same field is intentional and
    NOT double-counting, because they output to different domains (utilities vs
    probabilities).

    The output is presentational: 'if both played rationally given current
    incentives, here is the equilibrium.' Treat as scenario reasoning, not as a
    forecast that compounds with the synthesized outcome distribution.

    Strategies:
      US:   {strike, blockade_only, negotiate, withdraw}
      Iran: {capitulate, negotiate, prolong, escalate}
    """
    sh = s.stakeholders
    ud = s.us_dynamics

    # US payoffs (utility 0..10) given Iran's response
    # rows: US strategies; cols: Iran responses
    # Each cell: (us_payoff, iran_payoff)
    # Trump-driven payoffs incorporate ego, gas pain, military preference
    trump_ego = sh.trump.ego_size
    iran_zeal = sh.khamenei.religious_zeal
    gas_pain = ud.gas_price_pain_index

    # Construct payoff matrix
    # US strikes
    us_strike = {
        "capitulate":  (8 + trump_ego * 1.5, 1),       # US wins everything
        "negotiate":   (6, 3),                           # US gets framework, Iran avoids worst
        "prolong":     (3 - gas_pain * 3, 4),            # Stuck but Iran also losing
        "escalate":    (1 - gas_pain * 4, 4 - iran_zeal), # War spreads, both lose
    }
    us_blockade_only = {
        "capitulate":  (7, 2),
        "negotiate":   (5, 4),
        "prolong":     (2 - gas_pain * 4, 5 - iran_zeal),  # Korean-armistice trajectory
        "escalate":    (0, 6),
    }
    us_negotiate = {
        "capitulate":  (5, 4),
        "negotiate":   (7 - trump_ego * 2, 7),  # Trump ego punishes him for "weak" deal
        "prolong":     (3, 5),
        "escalate":    (1, 5),
    }
    us_withdraw = {
        "capitulate":  (4, 6),
        "negotiate":   (4, 7),
        "prolong":     (3 + gas_pain * 2, 8),  # Iran wins de facto; gas falls = US relief
        "escalate":    (2, 7),
    }

    matrix = {
        "strike": us_strike,
        "blockade_only": us_blockade_only,
        "negotiate": us_negotiate,
        "withdraw": us_withdraw,
    }

    # Find pure-strategy Nash equilibria
    nash = []
    us_strats = list(matrix.keys())
    iran_strats = list(us_strike.keys())
    for us_s in us_strats:
        for iran_s in iran_strats:
            us_payoff = matrix[us_s][iran_s][0]
            iran_payoff = matrix[us_s][iran_s][1]
            # US best response to Iran's strategy?
            us_alts = [matrix[other_s][iran_s][0] for other_s in us_strats]
            us_best = us_payoff >= max(us_alts) - 0.001
            # Iran best response to US's strategy?
            iran_alts = [matrix[us_s][other_s][1] for other_s in iran_strats]
            iran_best = iran_payoff >= max(iran_alts) - 0.001
            if us_best and iran_best:
                nash.append({
                    "us_strategy": us_s,
                    "iran_strategy": iran_s,
                    "us_payoff": round(us_payoff, 2),
                    "iran_payoff": round(iran_payoff, 2),
                    "joint_welfare": round(us_payoff + iran_payoff, 2),
                })

    # Pareto-optimal outcome (max joint welfare)
    all_cells = [
        {
            "us_strategy": us_s, "iran_strategy": iran_s,
            "us_payoff": round(matrix[us_s][iran_s][0], 2),
            "iran_payoff": round(matrix[us_s][iran_s][1], 2),
            "joint_welfare": round(sum(matrix[us_s][iran_s]), 2),
        }
        for us_s in us_strats for iran_s in iran_strats
    ]
    pareto = max(all_cells, key=lambda c: c["joint_welfare"])

    # Distance from Nash to Pareto = "trapped" measure
    nash_welfare = max([n["joint_welfare"] for n in nash], default=0)
    trapped_welfare_loss = pareto["joint_welfare"] - nash_welfare

    return {
        "nash_equilibria": nash,
        "pareto_optimal": pareto,
        "trapped_welfare_loss": round(trapped_welfare_loss, 2),
        "interpretation": (
            "Both sides are trapped at a sub-optimal Nash equilibrium when nash_welfare < pareto_welfare. "
            "Higher trapped_welfare_loss = stronger case that mediation can unlock value."
        ),
    }


# ============================================================================
# 2. BAYESIAN UPDATING — posterior probabilities given new evidence
# ============================================================================

def bayesian_update(prior_p: float, likelihood_given_h: float, likelihood_given_not_h: float) -> float:
    """Standard Bayes: P(H|E) = P(E|H)*P(H) / P(E)."""
    p_e = likelihood_given_h * prior_p + likelihood_given_not_h * (1 - prior_p)
    if p_e == 0:
        return prior_p
    return (likelihood_given_h * prior_p) / p_e


def bayesian_evidence_chain(s: Signals, base_outcomes: dict[str, float]) -> dict:
    """Apply sequential Bayesian updates from observed exotic-signal evidence."""
    e = s.exotic_signals
    posteriors = dict(base_outcomes)

    evidence_log = []

    # Evidence: Khamenei public appearance freq is low
    if e.khamenei_public_appearance_freq_30d <= 1:
        # P(succession imminent | low appearances) = 0.4
        # P(low appearances | succession imminent) = 0.85
        # P(low appearances | succession NOT imminent) = 0.15
        prior_succession = 0.10
        posterior_succession = bayesian_update(prior_succession, 0.85, 0.15)
        # Succession imminent shifts deal_p up + protracted down
        shift = (posterior_succession - prior_succession) * 0.3
        posteriors["deal"] = posteriors.get("deal", 0) + shift
        posteriors["protracted"] = posteriors.get("protracted", 0) - shift
        evidence_log.append({
            "evidence": f"Khamenei appearances: {e.khamenei_public_appearance_freq_30d}/30d",
            "prior_succession": prior_succession,
            "posterior_succession": round(posterior_succession, 3),
            "applied_shift": round(shift, 3),
        })

    # Evidence: Friday prayer attendance < 0.30 (clerical-public divorce)
    if e.friday_prayer_attendance_index < 0.30:
        prior_legitimacy_loss = 0.20
        posterior = bayesian_update(prior_legitimacy_loss, 0.75, 0.10)
        shift = (posterior - prior_legitimacy_loss) * 0.25
        posteriors["deal"] = posteriors.get("deal", 0) + shift * 0.5
        posteriors["intervention"] = posteriors.get("intervention", 0) + shift * 0.5
        posteriors["protracted"] = posteriors.get("protracted", 0) - shift
        evidence_log.append({
            "evidence": f"Friday prayer attendance: {e.friday_prayer_attendance_index:.2f}",
            "prior_legitimacy_loss": prior_legitimacy_loss,
            "posterior_legitimacy_loss": round(posterior, 3),
            "applied_shift": round(shift, 3),
        })

    # Evidence: Brent-WTI spread > $20 (Hormuz premium entrenched)
    if e.brent_wti_spread_usd > 20:
        prior_hormuz_extended = 0.40
        posterior = bayesian_update(prior_hormuz_extended, 0.80, 0.30)
        shift = (posterior - prior_hormuz_extended) * 0.20
        posteriors["protracted"] = posteriors.get("protracted", 0) + shift
        posteriors["deal"] = posteriors.get("deal", 0) - shift
        evidence_log.append({
            "evidence": f"Brent-WTI spread: ${e.brent_wti_spread_usd}",
            "prior_hormuz_extended": prior_hormuz_extended,
            "posterior_hormuz_extended": round(posterior, 3),
            "applied_shift": round(shift, 3),
        })

    # Renormalize
    total = sum(posteriors.values())
    if total > 0:
        for k in posteriors:
            posteriors[k] = round(posteriors[k] / total, 3)

    return {"posteriors": posteriors, "evidence_chain": evidence_log}


# ============================================================================
# 3. MONTE CARLO — N stochastic simulations through possible futures
# ============================================================================

def monte_carlo_simulation(s: Signals, n_runs: int = 5000, horizon_days: int = 90, seed: int = 42) -> dict:
    """Simulate N possible futures over horizon_days, count outcome frequencies.

    Each simulation:
      1. Sample initial trajectory from base outcome dist (deal/escalation/protracted/intervention/tail)
      2. Each day: small chance of regime fracture (rare event)
      3. Each day: small chance of a shock event that ROTATES the trajectory
         (escalation can become deal via breakthrough; protracted can become escalation; etc.)
      4. After horizon, return whatever trajectory the run is on

    The previous version had a bug: shocks ALWAYS terminated the run as
    escalation/intervention, so deal/protracted base-dist mass evaporated.
    Fixed by making shocks rotate trajectories (with realistic transition
    probabilities) instead of forcing termination.
    """
    rng = random.Random(seed)

    base_scores = all_condition_scores(s.condition_inputs, s.today_scalars.gas_price)
    deltas = psych_modifiers(s, base_scores)
    modified = apply_modifiers(base_scores, deltas)
    syn = synthesized_outcome_probabilities(s, base_scores, modified)
    base_dist = syn["outcome_dist"]

    fracture_p = regime_fracture_probability(s)

    # Per-day probabilities (much smaller than before)
    daily_shock_p = 0.015 + max(0.0, modified["escalationProximity"] - 0.4) * 0.04
    daily_shock_p = max(0.005, min(0.05, daily_shock_p))
    daily_fracture_p = fracture_p / max(1, horizon_days * 1.5)
    daily_tail_p = 0.0003

    # Shock transition: when a shock fires, where does the trajectory go?
    # Conditioned on escalationProximity and dealAvailability of the moment.
    # Returns dict mapping current state -> (new state, probability) options.
    def shock_transition(current: str, esc: float, deal_avail: float) -> str:
        """Return the new state after a shock event."""
        if current == "deal":
            # Deals can collapse into escalation if pressure is high; otherwise hold
            return rng.choices(
                ["deal", "escalation", "protracted"],
                weights=[1 - esc * 0.6, esc * 0.5, 0.1],
            )[0]
        if current == "escalation":
            # Escalation can de-escalate to deal/protracted, or worsen to intervention
            return rng.choices(
                ["escalation", "intervention", "deal", "protracted"],
                weights=[0.55, 0.20, deal_avail * 0.4, 0.15],
            )[0]
        if current == "protracted":
            # Protracted can break either way
            return rng.choices(
                ["protracted", "escalation", "deal", "intervention"],
                weights=[0.45, esc * 0.6, deal_avail * 0.6, 0.10],
            )[0]
        if current == "intervention":
            # Once intervention, mostly stays
            return rng.choices(
                ["intervention", "escalation", "deal"],
                weights=[0.65, 0.25, deal_avail * 0.30],
            )[0]
        return current

    outcome_counts = {"deal": 0, "escalation": 0, "protracted": 0, "intervention": 0,
                      "regime_collapse": 0, "tail": 0, "other": 0}
    days_to_resolution = []
    esc = modified["escalationProximity"]
    deal_avail = modified["dealAvailability"]

    for _ in range(n_runs):
        # Sample initial trajectory
        u = rng.random()
        cum = 0.0
        sampled = "protracted"
        for k, p in base_dist.items():
            cum += p
            if u <= cum:
                sampled = "tail" if k == "other" else k
                break
        # Walk forward
        terminated_day = None
        for day in range(1, horizon_days + 1):
            # Regime fracture event (terminates as regime_collapse)
            if rng.random() < daily_fracture_p:
                sampled = "regime_collapse"
                terminated_day = day
                break
            # Shock event (rotates trajectory, doesn't terminate)
            if rng.random() < daily_shock_p:
                sampled = shock_transition(sampled, esc, deal_avail)
            # Black swan (rare terminator)
            if rng.random() < daily_tail_p:
                sampled = "tail"
                terminated_day = day
                break
        days_to_resolution.append(terminated_day if terminated_day else horizon_days)
        outcome_counts[sampled] = outcome_counts.get(sampled, 0) + 1

    total = sum(outcome_counts.values())
    freqs = {k: round(v / total, 3) for k, v in outcome_counts.items() if v > 0 or k in ("deal", "escalation", "protracted", "intervention")}
    days_sorted = sorted(days_to_resolution)
    median_days = days_sorted[len(days_sorted) // 2]
    p10_days = days_sorted[len(days_sorted) // 10]
    p90_days = days_sorted[len(days_sorted) * 9 // 10]

    return {
        "n_runs": n_runs,
        "horizon_days": horizon_days,
        "outcome_frequencies": freqs,
        "median_days_to_resolution": median_days,
        "p10_days": p10_days,
        "p90_days": p90_days,
    }


# ============================================================================
# 4. HAZARD MODEL — continuous-time regime survival
# ============================================================================

def regime_hazard_curve(s: Signals, days_out: int = 365) -> dict:
    """Cox-style proportional hazard: P(regime survives at least t days)."""
    fracture_p_60d = regime_fracture_probability(s)
    # Convert to continuous hazard rate (assuming 60-day horizon for fracture_p)
    if fracture_p_60d >= 1.0:
        lambda_rate = 1.0
    elif fracture_p_60d <= 0.0:
        lambda_rate = 0.0
    else:
        lambda_rate = -math.log(1 - fracture_p_60d) / 60.0

    survival_curve = []
    for day in [7, 14, 30, 60, 90, 180, 270, 365]:
        if day > days_out:
            break
        s_t = math.exp(-lambda_rate * day)
        survival_curve.append({"day": day, "survival_probability": round(s_t, 3)})

    median_survival_days = math.log(2) / lambda_rate if lambda_rate > 0 else None
    return {
        "hazard_rate_per_day": round(lambda_rate, 6),
        "survival_curve": survival_curve,
        "median_survival_days": round(median_survival_days, 1) if median_survival_days else None,
    }


# ============================================================================
# 5. MULTI-HORIZON FORECASTING — different models for different timeframes
# ============================================================================

def multi_horizon_forecast(s: Signals) -> dict:
    """Each horizon has its own dominant force; emit a curve of outcome probabilities."""
    base_scores = all_condition_scores(s.condition_inputs, s.today_scalars.gas_price)
    deltas = psych_modifiers(s, base_scores)
    modified = apply_modifiers(base_scores, deltas)
    syn = synthesized_outcome_probabilities(s, base_scores, modified)
    base = syn["outcome_dist"]

    # Time-decay logic: short horizons weighted toward current state, long horizons toward structural drivers
    horizons = {
        "1d": {"weight_current": 0.95, "weight_structural": 0.05},
        "7d": {"weight_current": 0.80, "weight_structural": 0.20},
        "14d": {"weight_current": 0.65, "weight_structural": 0.35},
        "30d": {"weight_current": 0.50, "weight_structural": 0.50},
        "60d": {"weight_current": 0.35, "weight_structural": 0.65},
        "90d": {"weight_current": 0.25, "weight_structural": 0.75},
        "180d": {"weight_current": 0.15, "weight_structural": 0.85},
        "365d": {"weight_current": 0.10, "weight_structural": 0.90},
    }

    # Structural prior (long-term equilibrium based on historical analogs)
    analog = historical_analog_projection(s)
    structural = analog["outcome_dist"] or {}

    out = {}
    for h, w in horizons.items():
        merged = {}
        for k in set(base) | set(structural):
            merged[k] = round(
                w["weight_current"] * base.get(k, 0)
                + w["weight_structural"] * structural.get(k, 0),
                3,
            )
        # Renormalize
        total = sum(merged.values())
        if total > 0:
            merged = {k: round(v / total, 3) for k, v in merged.items()}
        out[h] = merged

    return out


# ============================================================================
# 6. KELLY CRITERION — optimal trade sizing on alpha signals
# ============================================================================

def kelly_size(model_p: float, market_p: float, payoff_if_right: float = 1.0, payoff_if_wrong: float = 1.0) -> float:
    """Fractional Kelly: f* = (bp - q) / b
    where b = payoff_if_right/payoff_if_wrong, p = model_p, q = 1-p.
    Returns optimal % of bankroll. Negative = take other side.
    """
    if model_p <= 0 or model_p >= 1:
        return 0.0
    b = payoff_if_right / max(0.001, payoff_if_wrong)
    f = (b * model_p - (1 - model_p)) / b
    # Half-Kelly (more conservative, standard practice)
    return round(f * 0.5, 3)


def kelly_sizing_for_alphas(alphas: list[dict]) -> list[dict]:
    """Apply half-Kelly sizing to alpha signals where model_pct + market_pct exist."""
    out = []
    for a in alphas:
        model_pct = a.get("model_pct")
        market_pct = a.get("market_pct")
        if model_pct is None or market_pct is None:
            continue
        # Convert market % to implied odds: payoff_if_right = (100 / market_pct - 1)
        if market_pct <= 0 or market_pct >= 100:
            continue
        payoff = (100 / market_pct) - 1
        size = kelly_size(model_pct / 100, market_pct / 100, payoff_if_right=payoff)
        a_with_kelly = dict(a)
        a_with_kelly["kelly_fraction"] = size
        a_with_kelly["kelly_interpretation"] = (
            f"Allocate ~{abs(size)*100:.1f}% of dedicated bankroll {'LONG' if size > 0 else 'SHORT'}; "
            f"market-implied payoff = {payoff:.2f}x"
        )
        out.append(a_with_kelly)
    return out


# ============================================================================
# 7. REFLEXIVITY — model accounts for own publication impact
# ============================================================================

def reflexivity_adjustment(outcome_dist: dict[str, float], publication_impact: float = 0.05) -> dict:
    """If model is widely consumed (e.g., by traders), its predictions move markets.

    A high deal-probability prediction may itself shift Polymarket toward deal,
    which could become self-fulfilling OR mean-reverting depending on dynamics.

    Conservative correction: assume `publication_impact` mean-reversion toward
    the equiprobable anchor (1/N for an N-bucket distribution), reflecting
    humility under reflexivity. Previously anchored to 0.20 regardless of N — a bug.
    """
    if not outcome_dist:
        return {}
    n_buckets = len(outcome_dist)
    anchor = 1.0 / n_buckets
    adjusted = {}
    for k, p in outcome_dist.items():
        adjusted[k] = round(p * (1 - publication_impact) + anchor * publication_impact, 3)
    # Renormalize
    total = sum(adjusted.values())
    if total > 0:
        adjusted = {k: round(v / total, 3) for k, v in adjusted.items()}
    return adjusted


# ============================================================================
# 8. COUNTERFACTUAL — sensitivity to a single actor change
# ============================================================================

def counterfactual_no_trump(s: Signals) -> dict:
    """What would the model say if Trump were a baseline neutral actor?"""
    import copy
    s_alt = s.model_copy(deep=True)
    s_alt.stakeholders.trump.ego_size = 0.4
    s_alt.stakeholders.trump.public_commitment = 0.5
    s_alt.stakeholders.trump.flexibility = 0.7
    s_alt.us_dynamics.christian_nationalist_pressure = 0.3

    base = all_condition_scores(s_alt.condition_inputs, s_alt.today_scalars.gas_price)
    deltas = psych_modifiers(s_alt, base)
    modified = apply_modifiers(base, deltas)
    syn = synthesized_outcome_probabilities(s_alt, base, modified)
    return {
        "scenario": "neutral US president (no Trump-specific ego/public-commitment penalty)",
        "outcome_dist": syn["outcome_dist"],
        "delta_vs_actual": "compare to deepDynamics.synthesizedOutcome.outcome_dist",
    }


def counterfactual_no_khamenei_lock(s: Signals) -> dict:
    """What if Khamenei had not made the public nuclear vow?"""
    s_alt = s.model_copy(deep=True)
    s_alt.stakeholders.khamenei.religious_zeal = 0.6
    s_alt.stakeholders.khamenei.public_commitment = 0.5
    s_alt.condition_inputs.iran_acceptance.khamenei_public_vow_against = False

    base = all_condition_scores(s_alt.condition_inputs, s_alt.today_scalars.gas_price)
    deltas = psych_modifiers(s_alt, base)
    modified = apply_modifiers(base, deltas)
    syn = synthesized_outcome_probabilities(s_alt, base, modified)
    return {
        "scenario": "Khamenei had not made public anti-deal vow",
        "outcome_dist": syn["outcome_dist"],
        "delta_vs_actual": "compare to deepDynamics.synthesizedOutcome.outcome_dist",
    }


# ============================================================================
# 9. ULTRAREAD — the apex narrative synthesis
# ============================================================================

# ============================================================================
# 10. CROSS-IMPACT MATRIX — how events trigger or suppress each other
# ============================================================================

CROSS_IMPACT = {
    # rows = trigger event; columns = effect on probability of consequence
    "khamenei_dies":          {"deal": +0.20, "escalation": +0.10, "protracted": -0.30, "intervention": +0.05, "regime_fracture": +0.40},
    "centcom_strike_grid":    {"deal": -0.30, "escalation": +0.45, "protracted": -0.15, "intervention": +0.20, "regime_fracture": +0.10},
    "us_gas_above_4_50":      {"deal": +0.15, "escalation": -0.10, "protracted": -0.05, "intervention": -0.05, "regime_fracture": +0.02},
    "china_enforces_sanctions":{"deal": +0.25, "escalation": -0.05, "protracted": -0.20, "intervention": -0.05, "regime_fracture": +0.15},
    "hezbollah_strike_tel_aviv":{"deal": -0.25, "escalation": +0.50, "protracted": -0.15, "intervention": +0.15, "regime_fracture": -0.05},
    "iran_dark_fleet_seized": {"deal": -0.10, "escalation": +0.30, "protracted": -0.10, "intervention": +0.10, "regime_fracture": +0.05},
    "uae_signs_separate_peace":{"deal": +0.20, "escalation": -0.15, "protracted": +0.05, "intervention": -0.10, "regime_fracture": +0.05},
    "saudi_iran_normalization": {"deal": +0.30, "escalation": -0.20, "protracted": -0.05, "intervention": -0.10, "regime_fracture": -0.05},
    "iran_nuclear_test":      {"deal": -0.40, "escalation": +0.50, "protracted": -0.10, "intervention": +0.40, "regime_fracture": -0.05},
    "israel_strikes_natanz":  {"deal": -0.30, "escalation": +0.55, "protracted": -0.20, "intervention": +0.30, "regime_fracture": +0.10},
    "russian_arms_to_iran":   {"deal": -0.10, "escalation": +0.20, "protracted": +0.10, "intervention": +0.10, "regime_fracture": -0.05},
    "trump_pivots_to_deal":   {"deal": +0.40, "escalation": -0.30, "protracted": -0.05, "intervention": -0.10, "regime_fracture": -0.05},
}


def cross_impact_matrix() -> dict:
    """Surface the cross-impact data structure for analyst reasoning."""
    return {
        "matrix": CROSS_IMPACT,
        "interpretation": (
            "Each row is a trigger event. Each column shows the SHIFT in outcome probability "
            "if that trigger fires. Cells > +0.20 are 'event-driven' (trigger essentially dictates "
            "outcome). Cells < -0.20 are 'event-killer' (trigger forecloses that outcome)."
        ),
    }


# ============================================================================
# 11. TRUMP DECISION TREE — backward induction over policy options
# ============================================================================

def trump_decision_tree(s: Signals) -> dict:
    """Discrete decision tree for Trump's next major move + expected payoff."""
    sh = s.stakeholders
    ud = s.us_dynamics

    # Each branch: probability Iran responds X, payoff to Trump
    branches = [
        {
            "us_move": "Strike CENTCOM plan",
            "p_iran_capitulate": 0.10,
            "p_iran_escalate": 0.55,
            "p_iran_negotiate": 0.20,
            "p_iran_prolong": 0.15,
            "trump_payoff_if_capitulate": 9.5,  # ego max
            "trump_payoff_if_escalate": 2.0 - ud.gas_price_pain_index * 4,  # gas pain dominates
            "trump_payoff_if_negotiate": 6.5,
            "trump_payoff_if_prolong": 3.0 - ud.gas_price_pain_index * 3,
        },
        {
            "us_move": "Tighten blockade only",
            "p_iran_capitulate": 0.05,
            "p_iran_escalate": 0.25,
            "p_iran_negotiate": 0.30,
            "p_iran_prolong": 0.40,
            "trump_payoff_if_capitulate": 8.0,
            "trump_payoff_if_escalate": 4.0 - ud.gas_price_pain_index * 3,
            "trump_payoff_if_negotiate": 6.0,
            "trump_payoff_if_prolong": 3.5 - ud.gas_price_pain_index * 4,
        },
        {
            "us_move": "Re-engage talks via Pakistan",
            "p_iran_capitulate": 0.05,
            "p_iran_escalate": 0.10,
            "p_iran_negotiate": 0.55,
            "p_iran_prolong": 0.30,
            "trump_payoff_if_capitulate": 8.5,
            "trump_payoff_if_escalate": 4.0,
            "trump_payoff_if_negotiate": 7.5 - sh.trump.ego_size * 2,  # ego cost
            "trump_payoff_if_prolong": 4.0,
        },
        {
            "us_move": "Quiet de-escalation + lift partial sanctions",
            "p_iran_capitulate": 0.02,
            "p_iran_escalate": 0.05,
            "p_iran_negotiate": 0.50,
            "p_iran_prolong": 0.43,
            "trump_payoff_if_capitulate": 7.5,
            "trump_payoff_if_escalate": 3.0,
            "trump_payoff_if_negotiate": 7.0 - sh.trump.ego_size * 3,
            "trump_payoff_if_prolong": 5.0 + (1 - ud.gas_price_pain_index) * 2,  # gas relief
        },
        {
            "us_move": "Declare victory + withdraw posture",
            "p_iran_capitulate": 0.0,
            "p_iran_escalate": 0.05,
            "p_iran_negotiate": 0.20,
            "p_iran_prolong": 0.75,
            "trump_payoff_if_capitulate": 0,
            "trump_payoff_if_escalate": 2.0,
            "trump_payoff_if_negotiate": 5.0,
            "trump_payoff_if_prolong": 6.0 - sh.trump.ego_size * 1.5 + (1 - ud.gas_price_pain_index) * 3,
        },
    ]

    for b in branches:
        ev = (
            b["p_iran_capitulate"] * b["trump_payoff_if_capitulate"]
            + b["p_iran_escalate"] * b["trump_payoff_if_escalate"]
            + b["p_iran_negotiate"] * b["trump_payoff_if_negotiate"]
            + b["p_iran_prolong"] * b["trump_payoff_if_prolong"]
        )
        b["expected_value"] = round(ev, 2)

    branches.sort(key=lambda x: x["expected_value"], reverse=True)
    return {
        "branches": branches,
        "rational_choice": branches[0]["us_move"],
        "rational_ev": branches[0]["expected_value"],
        "interpretation": (
            f"Backward induction over Iran's likely response distributions yields: "
            f"'{branches[0]['us_move']}' has highest expected payoff ({branches[0]['expected_value']:.2f}). "
            f"Watch for Trump deviation from rational choice — ego/personalist factors drive non-EV-max moves."
        ),
    }


# ============================================================================
# 12. INFORMATION CASCADE — how a single trigger ripples across actors
# ============================================================================

def information_cascade(trigger_event: str) -> dict:
    """Trace probable downstream events from a single trigger over 14 days."""
    cascades = {
        "khamenei_dies": [
            {"day": 0, "actor": "Iran state TV", "action": "Confirms death; mourning announced"},
            {"day": 0, "actor": "IRGC", "action": "Mobilizes; security lockdown nationwide"},
            {"day": 1, "actor": "Markets", "action": "Brent +$15-25 on uncertainty; rial collapses 30%"},
            {"day": 2, "actor": "Mojtaba camp", "action": "Asserts succession via Assembly of Experts"},
            {"day": 3, "actor": "Pezeshkian", "action": "Public statement — possible bid for civilian-track legitimacy"},
            {"day": 5, "actor": "Trump", "action": "Truth Social — likely 'big opportunity' framing"},
            {"day": 7, "actor": "Pakistan", "action": "Activates emergency mediation channels"},
            {"day": 10, "actor": "Russia/China", "action": "Joint statement supporting 'orderly transition'"},
            {"day": 14, "actor": "Iran factions", "action": "Public power struggle visible OR Mojtaba consolidated"},
        ],
        "centcom_strike_grid": [
            {"day": 0, "actor": "CENTCOM", "action": "Strikes 6+ Iranian power infrastructure targets"},
            {"day": 0, "actor": "Trump", "action": "Truth Social — declares 'severe response' justified"},
            {"day": 1, "actor": "IRGC", "action": "Hezbollah + Houthi + Iraqi militias coordinated retaliation"},
            {"day": 1, "actor": "Markets", "action": "Brent spikes $130+; S&P -5%; VIX 35+"},
            {"day": 2, "actor": "Saudi/UAE", "action": "Air-defense full activation; Aramco facilities hardened"},
            {"day": 3, "actor": "China", "action": "Strong condemnation; demands UN emergency session"},
            {"day": 5, "actor": "Iran", "action": "Possible asymmetric response — cyber, dark-fleet activation"},
            {"day": 7, "actor": "EU", "action": "Emergency foreign ministers meeting; humanitarian appeal"},
            {"day": 10, "actor": "US Congress", "action": "War powers resolution vote; possible bipartisan revolt"},
            {"day": 14, "actor": "Trump", "action": "Decision point — escalate further or pivot to deal posture"},
        ],
        "iran_accepts_deal": [
            {"day": 0, "actor": "Pakistan/Iran", "action": "Pakistan announces breakthrough; Iran confirms framework"},
            {"day": 0, "actor": "Trump", "action": "Victory lap on Truth Social; 'best deal ever'"},
            {"day": 1, "actor": "Markets", "action": "Brent -$25 in 24h; equities rally; gold sells off"},
            {"day": 2, "actor": "Israel", "action": "Public objections; backchannel demands harder enforcement"},
            {"day": 3, "actor": "IRGC hardliners", "action": "Internal pushback; possible shadow operations"},
            {"day": 7, "actor": "IAEA", "action": "Inspector access begins phase 1"},
            {"day": 10, "actor": "Hormuz", "action": "First commercial transit since blockade"},
            {"day": 14, "actor": "Both sides", "action": "Detail negotiations begin; risk of collapse on technicalities"},
        ],
    }
    return {
        "trigger": trigger_event,
        "cascade": cascades.get(trigger_event, []),
        "horizon_days": 14,
    }


def ultraread(s: Signals, all_outputs: dict) -> str:
    """The CIA-tool-grade single-paragraph synthesis."""
    syn = all_outputs.get("synthesizedOutcome", {})
    final = syn.get("outcome_dist", {})
    top = max(final.items(), key=lambda kv: kv[1]) if final else (None, 0)
    fracture = all_outputs.get("regimeFractureProbability", 0)
    nash = (all_outputs.get("gameTheoryEquilibrium", {}).get("nash_equilibria") or [{}])[0]
    mc = all_outputs.get("monteCarloSimulation", {}).get("outcome_frequencies", {})
    hazard = all_outputs.get("regimeHazardCurve", {}).get("median_survival_days")

    return (
        f"ULTRA READ — D{s.meta.day} ({s.meta.date.isoformat()}):\n\n"
        f"Most-likely outcome: **{top[0]} at ~{int((top[1] or 0)*100)}%** (synthesized across "
        f"structural/historical/market layers with {syn.get('inter_layer_agreement', syn.get('confidence_score', 0))*100:.0f}% inter-layer "
        f"agreement). Top historical analog: **{syn.get('top_analog')}** (median resolution "
        f"{syn.get('median_resolution_days_analog')}d). Monte Carlo (5000 runs, 90d horizon): "
        f"escalation {int(mc.get('escalation', 0)*100)}%, protracted {int(mc.get('protracted', 0)*100)}%, "
        f"deal {int(mc.get('deal', 0)*100)}%, regime collapse {int(mc.get('regime_collapse', 0)*100)}%.\n\n"
        f"Game-theoretic equilibrium: **US plays '{nash.get('us_strategy')}', Iran plays "
        f"'{nash.get('iran_strategy')}'** with joint welfare {nash.get('joint_welfare')}/20 — "
        f"{'sub-optimal trap' if all_outputs.get('gameTheoryEquilibrium', {}).get('trapped_welfare_loss', 0) > 2 else 'near-Pareto'}. "
        f"Iran regime survival hazard: 50% by day {hazard}.\n\n"
        f"DOMINANT BOTTLENECK: Khamenei religious-zeal × public-commitment lock (psych modifier "
        f"{all_outputs.get('psychModifiers', {}).get('iranAcceptance', 0)*100:+.0f}pp on iranAcceptance). "
        f"COMPOUND PRESSURE: US gas-price midterm amplifier ({all_outputs.get('psychModifiers', {}).get('usExitPressure', 0)*100:+.0f}pp on usExitPressure).\n\n"
        f"WATCH-FOR (highest-leverage trigger): {(all_outputs.get('crystallizationTriggers') or [{}])[0].get('trigger')}.\n\n"
        f"FALSIFIER: If 5+ of {{{', '.join(all_outputs.get('contrarianCheck', {}).get('what_would_invalidate', [])[:3])}, ...}} "
        f"fire within 14 days, model is wrong-footed."
    )
