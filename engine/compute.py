"""Pure-function engine: signals -> derived scores, outcomes, indicators, narrative.

All functions take Signals (and optionally history) and return primitives or dicts.
No I/O. No side effects. Trivially testable.

Scoring methodology mirrors the rationale documented in the original
decisionEngine prose: each condition is a weighted sum of binary/scalar inputs,
clamped to [0, 1]. Score overrides bypass computation when set.
"""
from __future__ import annotations

from typing import Optional

from .schema import (
    ConditionInputs,
    DealInputs,
    EscalationInputs,
    IranAcceptanceInputs,
    Signals,
    TodayScalars,
    UsExitInputs,
)


def _clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))


# ---------------------------------------------------------------------------
# Condition scores (4): probabilities each independent precondition is met
# ---------------------------------------------------------------------------

def deal_availability(d: DealInputs) -> float:
    """P(a viable deal exists between the two sides this week)."""
    if d.score_override is not None:
        return d.score_override
    base = 0.20  # any deal is plausible
    if d.iran_proposal_active:
        base += 0.25
    base += 0.30 * d.us_acceptance_signal
    # Each year of nuclear gap subtracts confidence (cap penalty at 0.20)
    base -= min(0.20, d.nuclear_gap_pp * 0.013)
    return round(_clamp(base), 2)


def us_exit_pressure(u: UsExitInputs, gas_price: float) -> float:
    """P(US is willing to take a deal — domestic + military pressure)."""
    if u.score_override is not None:
        return u.score_override
    base = 0.30
    if u.gas_pain_above_threshold:
        base += 0.20
    if u.war_powers_passed:
        base += 0.10
    if u.centcom_strike_plan_briefed:
        # Strike-plan briefed = US prefers military option over diplomatic exit
        base -= 0.05
    # Direct gas-price pressure: each $0.10 over $4.00 adds 0.02
    if gas_price > 4.00:
        base += min(0.20, (gas_price - 4.00) * 0.20)
    return round(_clamp(base), 2)


def iran_acceptance(i: IranAcceptanceInputs) -> float:
    """P(Iran agrees to terms — leadership willingness to settle)."""
    if i.score_override is not None:
        return i.score_override
    base = 0.50
    if i.khamenei_public_vow_against:
        base -= 0.25  # Supreme Leader public vow forecloses key US demands
    if i.irgc_in_charge:
        base -= 0.10  # IRGC ascendancy over civilian FM track
    base -= min(0.15, i.formal_proposals_rejected * 0.05)
    return round(_clamp(base), 2)


def escalation_proximity(e: EscalationInputs) -> float:
    """P(escalation is imminent — military-pathway pressure)."""
    if e.score_override is not None:
        return e.score_override
    base = 0.20
    if e.centcom_briefed:
        base += 0.15
    if e.hezbollah_action_recent:
        base += 0.10
    if e.new_blockade_action:
        base += 0.10
    return round(_clamp(base), 2)


def all_condition_scores(c: ConditionInputs, gas_price: float) -> dict[str, float]:
    return {
        "dealAvailability": deal_availability(c.deal),
        "usExitPressure": us_exit_pressure(c.us_exit, gas_price),
        "iranAcceptance": iran_acceptance(c.iran_acceptance),
        "escalationProximity": escalation_proximity(c.escalation),
    }


# ---------------------------------------------------------------------------
# Outcome probabilities (5 buckets, sum to 1.0)
# ---------------------------------------------------------------------------

def outcome_probabilities(
    scores: dict[str, float],
    coalition_cohesion: float = 5.0,
) -> dict[str, float]:
    """Derive 5-bucket outcome distribution from condition scores."""
    deal = scores["dealAvailability"]
    us = scores["usExitPressure"]
    iran = scores["iranAcceptance"]
    esc = scores["escalationProximity"]

    # Negotiated resolution = three-condition AND (multiplicative)
    negotiated = deal * us * iran

    # Escalation catastrophe: high escalation pressure × low deal availability
    escalation = esc * (1.0 - deal) * 0.85

    # International intervention: scales with escalation when coalition fractures
    coalition_fragility = max(0.0, 1.0 - coalition_cohesion / 10.0)
    intervention = esc * coalition_fragility * 0.45

    # Other / regime fracture / declared victory: small residual buckets
    other = 0.05 + (1.0 - deal) * 0.04

    # Protracted continuation = whatever's left (always non-negative)
    protracted = max(0.0, 1.0 - negotiated - escalation - intervention - other)

    # Re-normalize to handle float drift
    total = negotiated + escalation + protracted + intervention + other
    if total > 0:
        f = 1.0 / total
        negotiated *= f
        escalation *= f
        protracted *= f
        intervention *= f
        other *= f

    return {
        "negotiatedResolution": round(negotiated, 3),
        "escalationCatastrophe": round(escalation, 3),
        "protractedContinuation": round(protracted, 3),
        "internationalIntervention": round(intervention, 3),
        "other": round(other, 3),
    }


def resolution_probability(scores: dict[str, float], polymarket: int = 18, base_rate: int = 35) -> dict:
    """Top-line ensemble: model + market + base rate."""
    model_pct = round(
        scores["dealAvailability"] * scores["usExitPressure"] * scores["iranAcceptance"] * 100
    )
    # Weighted ensemble (model 0.4, market 0.4, base rate 0.2)
    estimate = round(model_pct * 0.4 + polymarket * 0.4 + base_rate * 0.2)
    # Confidence band: ±10pp baseline, widens when model-market disagree
    spread = max(10, abs(model_pct - polymarket))
    return {
        "model_pct": model_pct,
        "polymarket_pct": polymarket,
        "base_rate_pct": base_rate,
        "estimate": estimate,
        "low": max(0, estimate - spread // 2),
        "high": min(100, estimate + spread // 2),
    }


# ---------------------------------------------------------------------------
# Scalar indicators (28 fields)
# ---------------------------------------------------------------------------

def derived_indicators(s: Signals) -> dict:
    ts = s.today_scalars
    cn = s.constants
    m = s.meta

    brent_shock = round((ts.brent - cn.pre_war_brent) / cn.pre_war_brent, 2)
    hormuz_recovery = round(ts.hormuz_vessels / cn.pre_war_hormuz, 2)
    gas_shock = round((ts.gas_price - cn.pre_war_gas) / cn.pre_war_gas, 2)

    # Days to original ceasefire deadline (Apr 21, day 53)
    cf_deadline_day = cn.ceasefire_original_deadline_day
    days_to_deadline = cf_deadline_day - m.day
    days_to_deadline_val = days_to_deadline if days_to_deadline > 0 else None

    return {
        "launchRate7DMA": 0.0,  # filled by emit.py from history
        "launchRateVsD1": 0.0,  # filled by emit.py from history
        "brentShock": brent_shock,
        "hormuzRecovery": hormuz_recovery,
        "gasShock": gas_shock,
        "gasPrice": ts.gas_price,
        "usKIA": ts.us_kia,
        "usWounded": ts.us_wounded,
        "usAircraftLost": ts.us_aircraft_lost,
        "warDays": m.day,
        "daysToDeadline": days_to_deadline_val,
        "iranCivKilled_HRANA": ts.iran_civ_killed_hrana,
        "iranCivKilled_AJ": ts.iran_civ_killed_aj,
        "lebanonKilled": ts.lebanon_killed,
        "coalitionCohesionScore": ts.coalition_cohesion_score,
        "daysWithoutMissile": ts.zero_attack_streak_days,
        "irgcStatementsEscalatory": s.condition_inputs.escalation.centcom_briefed
        or s.condition_inputs.escalation.new_blockade_action,
        "iranRejectedCeasefire": s.condition_inputs.iran_acceptance.formal_proposals_rejected > 0,
        "hormuzTollOperational": ts.hormuz_vessels < cn.pre_war_hormuz * 0.2,
    }


# ---------------------------------------------------------------------------
# Mode + deadline derivation
# ---------------------------------------------------------------------------

def ceasefire_mode_enabled(s: Signals) -> bool:
    return s.mode.ceasefire_status in ("active", "hollow", "extended_indef")


def ceasefire_deadline(s: Signals) -> Optional[str]:
    """ISO date for original deadline; null when extended_indef or collapsed."""
    if s.mode.ceasefire_status == "extended_indef":
        return None
    if s.mode.ceasefire_status == "collapsed":
        return None
    # Original deadline = 2026-04-21T20:00 ET (matches existing data)
    return "2026-04-21T20:00:00-04:00"


def ceasefire_extensions_count(s: Signals) -> int:
    """Counts known status transitions to extended_indef."""
    return 1 if s.mode.ceasefire_status == "extended_indef" else 0


# ---------------------------------------------------------------------------
# Narrative templating (replaces hand-typed methodology prose)
# ---------------------------------------------------------------------------

def confidence_methodology(s: Signals, scores: dict[str, float]) -> str:
    """Templated, today-aware methodology string."""
    parts = [
        f"D{s.meta.day} ensemble:",
        f"model {round(scores['dealAvailability'] * scores['usExitPressure'] * scores['iranAcceptance'] * 100)}%",
        f"× market signal × base rate.",
    ]
    if s.mode.ceasefire_status == "hollow":
        parts.append("Ceasefire formally extended but blockade + IRGC seizures = hollow.")
    elif s.mode.ceasefire_status == "collapsed":
        parts.append("Ceasefire collapsed — back to active conflict.")
    elif s.mode.ceasefire_status == "extended_indef":
        parts.append("Indefinite extension — buys time, resolves nothing.")
    if s.condition_inputs.iran_acceptance.khamenei_public_vow_against:
        parts.append("Khamenei public vow against US demands = bottleneck on Iran acceptance.")
    return " ".join(parts)


def calibration_methodology(s: Signals) -> str:
    return (
        f"D{s.meta.day}: model derived from {len(s.meta.notes)} narrative bullets + "
        f"{sum(1 for v in s.condition_inputs.model_dump().values() if isinstance(v, dict))} "
        "condition input groups. Polymarket + historical base rate weighted in ensemble."
    )


# ---------------------------------------------------------------------------
# Psychological / structural modifiers (the "superintelligence" layer)
# ---------------------------------------------------------------------------
# These take stakeholder + dynamics + history and adjust the 4 condition scores
# AFTER they're computed from condition_inputs. Each modifier returns a delta
# in [-0.30, +0.30] so the final score remains interpretable.

def _ego_lock_penalty(p) -> float:
    """When ego × public commitment is very high, climbdown becomes ego-impossible."""
    return p.ego_size * p.public_commitment * 0.25


def _religious_zeal_lock(p) -> float:
    """Religious zeal × public commitment → near-zero acceptance of any compromise."""
    return p.religious_zeal * p.public_commitment * 0.30


def _succession_distortion(p) -> float:
    """High succession anxiety + ideological style → defaults to hardline (no risk to legacy)."""
    if p.decision_style == "ideological":
        return p.succession_anxiety * 0.20
    return p.succession_anxiety * 0.10


def _short_horizon_pressure(p) -> float:
    """Very short time horizon (<30 days) compresses decision space → action-bias."""
    if p.time_horizon_days < 30:
        return 0.15
    if p.time_horizon_days < 90:
        return 0.05
    return 0.0


def psych_modifiers(s: Signals, scores: dict[str, float]) -> dict[str, float]:
    """Compute deltas to the 4 condition scores from psych + dynamics + history layers.

    Returns deltas (signed). Apply by: adjusted = clamp(score + delta).
    """
    sh = s.stakeholders
    rd = s.iran_regime_dynamics
    ud = s.us_dynamics
    idd = s.iran_deep_dynamics
    wd = s.world_dynamics
    hi = s.historical_ideology

    deltas = {
        "dealAvailability": 0.0,
        "usExitPressure": 0.0,
        "iranAcceptance": 0.0,
        "escalationProximity": 0.0,
    }

    # ----- DEAL AVAILABILITY -----
    # Trump ego-lock: when his ego × public commitment is high, deal must look like HIS win
    deltas["dealAvailability"] -= _ego_lock_penalty(sh.trump) * 0.6
    # JCPOA personal animus reduces deal viability (Trump rejects anything resembling Obama's deal)
    deltas["dealAvailability"] -= hi.trump_jcpoa_personal_animus * 0.10
    # Mediator quality (Munir flexibility + Putin leverage) raises deal feasibility
    deltas["dealAvailability"] += sh.munir.flexibility * 0.08
    deltas["dealAvailability"] += sh.putin.flexibility * wd.russia_leverage_seeking * 0.05
    # Nuclear taboo strength raises deal urgency on US side
    deltas["dealAvailability"] += hi.nuclear_taboo_strength * 0.05
    # JCPOA collapse memory undercuts Iran's faith in any deal
    deltas["dealAvailability"] -= hi.jcpoa_collapse_iran_lens * 0.08

    # ----- US EXIT PRESSURE -----
    # Gas pain rises sharply near midterms (electoral feedback loop)
    midterm_amplifier = max(0.5, 1.0 - ud.midterms_proximity_days / 730)
    deltas["usExitPressure"] += ud.gas_price_pain_index * midterm_amplifier * 0.20
    # Iraq war fatigue + isolationism push for exit
    deltas["usExitPressure"] += hi.us_iraq_war_fatigue * 0.10
    deltas["usExitPressure"] += ud.isolationist_resurgence * 0.10
    # Christian-nationalist + Hegseth axis pushes AGAINST exit (wants strikes)
    deltas["usExitPressure"] -= ud.christian_nationalist_pressure * sh.hegseth.risk_tolerance * 0.10
    # Approval rating on war: low approval = exit pressure
    deltas["usExitPressure"] += (1.0 - ud.approval_rating_war) * 0.10
    # Deep state misalignment reduces ability to exit cleanly
    deltas["usExitPressure"] -= (1.0 - ud.deep_state_alignment) * 0.05
    # Market recession risk: exit pressure rises sharply
    deltas["usExitPressure"] += ud.market_recession_prob * 0.10

    # ----- IRAN ACCEPTANCE -----
    # Khamenei religious-zeal lock dominates (he's the decider)
    deltas["iranAcceptance"] -= _religious_zeal_lock(sh.khamenei) * 0.7
    # Khamenei succession anxiety: if Mojtaba succession is locked, K won't risk regime stability on a deal
    deltas["iranAcceptance"] -= idd.khamenei_health_concern * idd.mojtaba_succession_lock * 0.10
    # IRGC ascendancy: blocks acceptance independent of Khamenei
    deltas["iranAcceptance"] -= sh.irgc.public_commitment * idd.clerical_irgc_alignment * 0.15
    # Population restiveness: pulls regime toward acceptance (loss aversion spike)
    pop_pressure = rd.population_restiveness * rd.population_war_fatigue * idd.oil_revenue_collapse_pct
    deltas["iranAcceptance"] += pop_pressure * 0.20
    # Iran-Iraq war trauma: nuclear non-negotiable ('never again unprepared')
    deltas["iranAcceptance"] -= hi.iran_iraq_war_trauma * 0.10
    # 1979 revolution legacy: anti-imperial frame makes US deals ideologically costly
    deltas["iranAcceptance"] -= hi.iran_1979_revolution_legacy * 0.05
    # Soleimani memory: blood-debt frame raises rejection threshold
    deltas["iranAcceptance"] -= hi.soleimani_assassination_iran_lens * 0.05
    # Qom seminary dissent: clerical pushback pulls toward acceptance
    deltas["iranAcceptance"] += idd.qom_seminary_dissent * 0.10
    # Pezeshkian flexibility (civilian track) — but only weighted by his actual decision power
    deltas["iranAcceptance"] += sh.pezeshkian.flexibility * (1.0 - sh.pezeshkian.coalition_dependency) * 0.05

    # ----- ESCALATION PROXIMITY -----
    # IRGC risk tolerance × ascendancy raises escalation risk
    deltas["escalationProximity"] += sh.irgc.risk_tolerance * idd.clerical_irgc_alignment * 0.10
    # Hegseth + military preference: short-horizon action bias
    deltas["escalationProximity"] += _short_horizon_pressure(sh.hegseth) * sh.hegseth.risk_tolerance * 0.15
    # Trump short horizon (14 days) + ego: snap-decisions risk
    deltas["escalationProximity"] += _short_horizon_pressure(sh.trump) * 0.10
    # Israel independence (Lebanon front) pulls escalation
    deltas["escalationProximity"] += wd.israel_independence_score * sh.netanyahu.public_commitment * 0.10
    # Hezbollah loss aversion + recent action = retaliation cycle risk
    deltas["escalationProximity"] += sh.hezbollah.loss_aversion * sh.hezbollah.public_commitment * 0.05
    # UN paralysis removes off-ramps
    deltas["escalationProximity"] += wd.un_security_council_paralysis * 0.05
    # Ethnic unrest creates Iran internal pressure that could be released externally
    ethnic_total = (idd.kurd_unrest + idd.baluch_unrest + idd.arab_minority_unrest) / 3
    deltas["escalationProximity"] += ethnic_total * 0.05
    # Mediator engagement reduces escalation
    deltas["escalationProximity"] -= sh.munir.flexibility * 0.05
    # GCC realignment: Gulf states seeking de-escalation reduces escalation
    deltas["escalationProximity"] -= wd.gcc_realignment * 0.05

    # Clamp every delta to [-0.30, +0.30]
    for k in deltas:
        deltas[k] = round(max(-0.30, min(0.30, deltas[k])), 3)
    return deltas


def apply_modifiers(scores: dict[str, float], deltas: dict[str, float]) -> dict[str, float]:
    """Apply psych deltas to base scores. Returns new clamped scores."""
    return {k: round(_clamp(scores[k] + deltas.get(k, 0.0)), 3) for k in scores}


# ---------------------------------------------------------------------------
# Regime fracture probability — derived as a first-class output, not residual
# ---------------------------------------------------------------------------

def regime_fracture_probability(s: Signals) -> float:
    """P(Iran regime cracks open in next 60 days) — function of internal pressure."""
    rd = s.iran_regime_dynamics
    idd = s.iran_deep_dynamics

    # Pressure stack
    pressure = (
        rd.population_restiveness * 0.25
        + rd.population_war_fatigue * 0.15
        + rd.economic_pain_index * 0.20
        + idd.oil_revenue_collapse_pct * 0.15
        + idd.qom_seminary_dissent * 0.10
        + ((idd.kurd_unrest + idd.baluch_unrest + idd.arab_minority_unrest) / 3) * 0.10
        + idd.diaspora_mobilization * 0.05
    )
    # Brittleness multiplier
    fracture_p = pressure * rd.regime_brittleness
    # Grip strength dampens
    fracture_p *= (1.0 - rd.regime_grip_strength * 0.7)
    # Succession-anxiety amplifier (transition windows = fracture windows)
    fracture_p *= (1.0 + idd.khamenei_health_concern * 0.5)
    return round(_clamp(fracture_p), 3)


# ---------------------------------------------------------------------------
# Forward projections (predict trajectories, not just current state)
# ---------------------------------------------------------------------------

def forward_projections(s: Signals, scores: dict[str, float]) -> dict[str, dict]:
    """Produce 7/14/30-day directional forecasts for each condition score.

    For each horizon, return:
      - direction: 'rising' | 'flat' | 'falling'
      - magnitude_pp: signed percentage-point shift expected
      - driver: one-sentence reason
    """
    sh = s.stakeholders
    rd = s.iran_regime_dynamics
    ud = s.us_dynamics
    idd = s.iran_deep_dynamics

    # 7-day: dominated by short-horizon actors
    short_horizon_force = _short_horizon_pressure(sh.trump) + _short_horizon_pressure(sh.hegseth)
    midterm_amplifier = max(0.5, 1.0 - ud.midterms_proximity_days / 730)

    # 30-day: dominated by structural pressures (succession, oil, population)
    structural_iran_pressure = (
        rd.population_war_fatigue * idd.oil_revenue_collapse_pct
        - sh.khamenei.religious_zeal * sh.khamenei.public_commitment
    )
    structural_us_pressure = ud.gas_price_pain_index * midterm_amplifier - ud.christian_nationalist_pressure * 0.5

    return {
        "h7": {
            "deal": {"direction": "flat", "magnitude_pp": 0,
                     "driver": "Trump ego-lock + Khamenei vow → no deal in 7 days"},
            "escalation": {"direction": "rising" if short_horizon_force > 0.15 else "flat",
                           "magnitude_pp": round(short_horizon_force * 30),
                           "driver": "Short-horizon decisioners + CENTCOM plan briefed"},
        },
        "h14": {
            "deal": {"direction": "rising" if structural_iran_pressure > 0.2 else "falling",
                     "magnitude_pp": round(structural_iran_pressure * 20),
                     "driver": "Iran population pressure + oil revenue collapse vs Khamenei religious lock"},
            "escalation": {"direction": "rising" if scores["escalationProximity"] > 0.5 else "flat",
                           "magnitude_pp": round(scores["escalationProximity"] * 20 - 5),
                           "driver": "Sustained CENTCOM signaling + IRGC ascendancy"},
        },
        "h30": {
            "deal": {"direction": "rising" if structural_iran_pressure + structural_us_pressure > 0.3 else "flat",
                     "magnitude_pp": round((structural_iran_pressure + structural_us_pressure) * 15),
                     "driver": "Compound: Iran economic + US electoral pressure both rising"},
            "regime_fracture": {"direction": "rising" if regime_fracture_probability(s) > 0.15 else "flat",
                                "magnitude_pp": round(regime_fracture_probability(s) * 100),
                                "driver": "Population × restiveness × brittleness ramp"},
        },
    }


# ---------------------------------------------------------------------------
# The "superintelligence read" — analytical narrative synthesis
# ---------------------------------------------------------------------------

def deep_read(s: Signals, scores: dict[str, float], deltas: dict[str, float]) -> str:
    """Generate an analytical paragraph synthesizing the deep layers.

    This is the 'what an AI looking at all this would say' output — surfaces
    non-obvious patterns from the cross-product of psych + dynamics + history.
    """
    sh = s.stakeholders
    rd = s.iran_regime_dynamics
    ud = s.us_dynamics
    idd = s.iran_deep_dynamics

    bullets = []

    # The structural deadlock
    if sh.khamenei.religious_zeal > 0.85 and sh.khamenei.public_commitment > 0.85:
        bullets.append(
            "**Khamenei lock**: religious zeal × public commitment is at ego-impossible levels — "
            "his nuclear/missile vow forecloses any near-term concession path. Iran acceptance is "
            "structurally capped regardless of population pressure or sanctions."
        )
    if sh.trump.ego_size > 0.9 and sh.trump.public_commitment > 0.8:
        bullets.append(
            "**Trump lock**: ego × public commitment means the deal must look like HIS personal win. "
            "JCPOA-shaped deals are personally rejected on principle. The deal-shape Iran will accept "
            "and the deal-shape Trump will accept have near-zero overlap right now."
        )

    # The regime-population disjoint
    if rd.regime_public_support_pct < 25 and rd.regime_grip_strength > 0.7:
        bullets.append(
            f"**Iran's 10/90 split is the dashboard's most underweighted factor**: "
            f"~{rd.regime_public_support_pct:.0f}% population supports the regime, ~"
            f"{rd.population_war_fatigue*100:.0f}% war-fatigued, ~"
            f"{rd.economic_pain_index*100:.0f}% economic pain — but the regime is armed and willing to shoot. "
            f"This means the population's preference (deal at any cost) does NOT translate to regime "
            f"behavior unless restiveness ({rd.population_restiveness*100:.0f}%) crosses the brittleness threshold "
            f"({rd.regime_brittleness*100:.0f}%). Watch for: ethnic unrest spikes, IRGC defections, "
            f"clerical Qom dissent ({idd.qom_seminary_dissent*100:.0f}%)."
        )

    # The US electoral feedback loop
    if ud.midterms_proximity_days < 600 and ud.gas_price_pain_index > 0.5:
        bullets.append(
            f"**US electoral feedback is approaching**: midterms in ~{ud.midterms_proximity_days} days, "
            f"gas-pain at {ud.gas_price_pain_index*100:.0f}%. Trump's risk calculus shifts sharply when "
            f"polling shows war-handling approval below 35% sustained for 2+ weeks. The midterm-amplifier "
            f"in `us_exit_pressure` will compound non-linearly past day-{ud.midterms_proximity_days - 90}."
        )

    # The succession overhang
    if idd.khamenei_health_concern > 0.4 and idd.mojtaba_succession_lock > 0.5:
        bullets.append(
            "**Succession overhang**: Khamenei is 86. Mojtaba succession lock + ideological style = "
            "regime cannot afford to look weak during transition window. This makes the 30–60 day forecast "
            "MORE escalation-prone, not less, even as economic pain compounds."
        )

    # World dynamics shifts
    if s.world_dynamics.gcc_realignment > 0.6:
        bullets.append(
            "**GCC realignment is structural**: UAE OPEC exit signals Gulf states are pricing in a "
            "post-American security architecture. This raises Iran's leverage (more oil-buyer optionality) "
            "and erodes US coalition cohesion — feeds intervention probability AND regime survivability."
        )

    # The dominant delta this turn
    if deltas:
        max_pos = max(deltas.items(), key=lambda kv: kv[1])
        max_neg = min(deltas.items(), key=lambda kv: kv[1])
        if max_pos[1] > 0.05:
            bullets.append(
                f"**Largest psych boost this turn**: {max_pos[0]} +{max_pos[1]*100:.1f}pp from "
                f"stakeholder/dynamics layer."
            )
        if max_neg[1] < -0.05:
            bullets.append(
                f"**Largest psych drag this turn**: {max_neg[0]} {max_neg[1]*100:+.1f}pp from "
                f"stakeholder/dynamics layer."
            )

    if not bullets:
        bullets.append("No high-salience deep-layer signals dominating this turn.")

    return "\n\n".join(bullets)


# ---------------------------------------------------------------------------
# Exotic-signal triggers — out-of-band leading indicators
# ---------------------------------------------------------------------------
# Each trigger checks for a SPECIFIC signal pattern that historically precedes
# a specific outcome. These are "what an analyst watches for" — encoded.

def exotic_triggers(s: Signals) -> dict[str, dict]:
    """Detect specific exotic-signal patterns + what each implies."""
    e = s.exotic_signals
    triggers = {}

    # ===== Regime collapse leading indicators =====
    if e.rial_official_per_usd and e.rial_black_market_per_usd:
        gap_pct = (e.rial_black_market_per_usd / e.rial_official_per_usd - 1) * 100
        if gap_pct > 100:
            triggers["rial_dual_rate_collapse"] = {
                "fired": True,
                "value_pct": round(gap_pct, 1),
                "implies": "regime_fracture +5pp; iran_acceptance +3pp (currency surrender)",
                "source_pattern": "Venezuela 2018 / Lebanon 2019 / Iran 1979",
            }

    # Friday prayer attendance < 30% sustained = clerical-public divorce
    if e.friday_prayer_attendance_index < 0.30:
        triggers["clerical_public_divorce"] = {
            "fired": True,
            "value": e.friday_prayer_attendance_index,
            "implies": "regime_fracture +3pp; ideological_legitimacy_erosion",
            "source_pattern": "Iranian Green Movement 2009; Soviet 1989",
        }

    # Khamenei public appearances < 1/30d = succession imminent
    if e.khamenei_public_appearance_freq_30d < 1:
        triggers["khamenei_succession_imminent"] = {
            "fired": True,
            "value": e.khamenei_public_appearance_freq_30d,
            "implies": "regime_brittleness +20pp; deal probability resets — Mojtaba unknown commodity",
            "source_pattern": "Andropov 1983-84, Brezhnev 1981-82",
        }

    # IRGC promotion velocity > 0.8 = consolidation phase (about to act)
    if e.irgc_promotion_velocity > 0.8:
        triggers["irgc_consolidation"] = {
            "fired": True,
            "value": e.irgc_promotion_velocity,
            "implies": "escalation +5pp; civilian-track marginalization complete",
            "source_pattern": "IRGC ascendancy 2009 post-Green; Soleimani-era 2016-19",
        }

    # ===== US side =====
    # Brent-WTI spread > $20 = Hormuz premium isolated and entrenched
    if e.brent_wti_spread_usd > 20:
        triggers["hormuz_premium_isolation"] = {
            "fired": True,
            "value_usd": e.brent_wti_spread_usd,
            "implies": "us_exit_pressure +5pp; market pricing in extended Hormuz disruption",
            "source_pattern": "Iran-Iraq 'tanker war' 1984-88",
        }

    # Polymarket-vs-model divergence = arbitrage signal
    poly = e.polymarket_ceasefire_holds_pct
    if poly is not None:
        # If model says 30%+ and market says < 15%, big divergence
        triggers["polymarket_divergence"] = {
            "fired": False,
            "value_pct": poly,
            "implies": "calibration check — see ensemble methodology",
            "source_pattern": "always check market disagreement",
        }

    # Houthi attacks 7d > 5 = proxy network coherence holding
    if e.houthi_attacks_red_sea_7d > 5:
        triggers["proxy_network_active"] = {
            "fired": True,
            "value": e.houthi_attacks_red_sea_7d,
            "implies": "intervention +3pp; multi-front sustained",
            "source_pattern": "Iran proxy doctrine 2019-present",
        }

    # Iranian dark fleet > 100 = sanctions evasion ramp = regime can sustain longer
    if e.iranian_dark_fleet_active_tankers and e.iranian_dark_fleet_active_tankers > 100:
        triggers["dark_fleet_sustaining"] = {
            "fired": True,
            "value": e.iranian_dark_fleet_active_tankers,
            "implies": "protracted_continuation +5pp; regime_survival improved",
            "source_pattern": "Russian shadow fleet 2022-present",
        }

    # Starlink terminals > 100k = independent comms layer = restiveness can coordinate
    if e.starlink_terminals_estimated > 100_000:
        triggers["independent_comms_layer"] = {
            "fired": True,
            "value": e.starlink_terminals_estimated,
            "implies": "regime_grip -3pp; population restiveness can coordinate",
            "source_pattern": "Ukrainian use 2022; Iranian protests 2022-23",
        }

    # IAEA access < 0.2 = total opacity = nuclear weaponization risk
    if e.iaea_inspector_access_score < 0.2:
        triggers["nuclear_opacity_critical"] = {
            "fired": True,
            "value": e.iaea_inspector_access_score,
            "implies": "escalation +8pp; Israel/US strike calculus changes",
            "source_pattern": "North Korea 2003 expulsion",
        }

    return triggers


# ---------------------------------------------------------------------------
# Historical-analog projection — "what happened in similar past situations"
# ---------------------------------------------------------------------------

# Each analog has a structured outcome distribution + median resolution time
ANALOG_OUTCOMES = {
    "cuban_missile_crisis_1962": {
        "median_resolution_days": 13,
        "outcome_dist": {"deal": 0.95, "escalation": 0.05, "protracted": 0.0, "intervention": 0.0},
        "lesson": "Back-channel + face-saving formula = rapid de-escalation. Trump-Khamenei lacks back-channel; lesson = build one.",
    },
    "iran_iraq_war_endgame_1988": {
        "median_resolution_days": 540,  # economic exhaustion path
        "outcome_dist": {"deal": 0.6, "escalation": 0.05, "protracted": 0.3, "intervention": 0.05},
        "lesson": "Iran accepts deal only when economic capacity definitively breaks. Khomeini: 'drank poison.' Watch oil revenue collapse + IRGC authorization.",
    },
    "yom_kippur_war_1973": {
        "median_resolution_days": 19,
        "outcome_dist": {"deal": 0.7, "escalation": 0.15, "protracted": 0.1, "intervention": 0.05},
        "lesson": "Superpower brinksmanship → US-Soviet (now US-China/Russia) negotiate the framework over the heads of belligerents.",
    },
    "kuwait_invasion_1990_91": {
        "median_resolution_days": 200,
        "outcome_dist": {"deal": 0.05, "escalation": 0.25, "protracted": 0.05, "intervention": 0.65},
        "lesson": "Decisive coalition military action — but coalition cohesion required. Current GCC realignment makes this harder.",
    },
    "kosovo_intervention_1999":  {
        "median_resolution_days": 78,
        "outcome_dist": {"deal": 0.7, "escalation": 0.05, "protracted": 0.0, "intervention": 0.25},
        "lesson": "Air-only campaign + diplomatic pressure → political settlement. Restraints mirror current Trump preferences.",
    },
    "syria_civil_war_2011_present": {
        "median_resolution_days": 5000,  # 14 years and counting
        "outcome_dist": {"deal": 0.05, "escalation": 0.15, "protracted": 0.7, "intervention": 0.1},
        "lesson": "Multi-actor stalemate with proxy wars → 14+ years and counting. Avoid this trajectory if possible.",
    },
    "jcpoa_negotiation_2013_15": {
        "median_resolution_days": 800,
        "outcome_dist": {"deal": 0.85, "escalation": 0.0, "protracted": 0.1, "intervention": 0.05},
        "lesson": "Years-long indirect channels → comprehensive framework. Pakistan parallel = current Munir track.",
    },
    "korean_war_armistice_1953": {
        "median_resolution_days": 1100,
        "outcome_dist": {"deal": 0.4, "escalation": 0.0, "protracted": 0.6, "intervention": 0.0},
        "lesson": "Ceasefire-without-peace → frozen conflict for 70+ years. The 'extended_indef' mode current Iran-US is in.",
    },
    "october_war_aftermath_1973_75": {
        "median_resolution_days": 700,
        "outcome_dist": {"deal": 0.85, "escalation": 0.0, "protracted": 0.1, "intervention": 0.05},
        "lesson": "Kissinger shuttle diplomacy across multiple capitals — Munir/Pakistan currently filling this role.",
    },
    "suez_crisis_1956": {
        "median_resolution_days": 130,
        "outcome_dist": {"deal": 0.6, "escalation": 0.0, "protracted": 0.0, "intervention": 0.4},
        "lesson": "External pressure (Eisenhower threats) forces withdrawal. Current US is the actor IN the conflict, not the moderator.",
    },
}


def historical_analog_projection(s: Signals) -> dict:
    """Use weighted historical analogs to project outcome probabilities."""
    h = s.historical_analogs
    weights = h.model_dump()
    weights.pop("notes", None)
    total_w = sum(weights.values())
    if total_w == 0:
        return {"outcome_dist": {}, "median_resolution_days": None, "top_analog": None, "top_lesson": ""}

    # Weighted average outcome distribution across analogs
    aggregated = {"deal": 0.0, "escalation": 0.0, "protracted": 0.0, "intervention": 0.0}
    weighted_days = 0.0
    for name, weight in weights.items():
        if weight == 0 or name not in ANALOG_OUTCOMES:
            continue
        a = ANALOG_OUTCOMES[name]
        for k, v in a["outcome_dist"].items():
            aggregated[k] += v * weight
        weighted_days += a["median_resolution_days"] * weight
    for k in aggregated:
        aggregated[k] = round(aggregated[k] / total_w, 3)
    median_days = round(weighted_days / total_w)
    top_analog = max(weights.items(), key=lambda kv: kv[1])
    return {
        "outcome_dist": aggregated,
        "median_resolution_days": median_days,
        "top_analog": top_analog[0],
        "top_analog_weight": top_analog[1],
        "top_lesson": ANALOG_OUTCOMES.get(top_analog[0], {}).get("lesson", ""),
    }


# ---------------------------------------------------------------------------
# THE PREDICTIVE FRAMEWORK — synthesize everything
# ---------------------------------------------------------------------------

def synthesized_outcome_probabilities(
    s: Signals, base_scores: dict[str, float], modified_scores: dict[str, float]
) -> dict:
    """Final-form outcome distribution: ensemble across structural + psych + historical + market layers.

    Returns:
      - outcome_dist: 5-bucket probability distribution
      - layer_contributions: dict showing each layer's weighted vote
      - confidence_score: 0..1, how much each layer agrees with the others
    """
    # Layer 1: Structural (the original condition-score model, with psych applied)
    structural = outcome_probabilities(modified_scores, s.today_scalars.coalition_cohesion_score)
    # Map structural keys to our 4 standardized buckets
    structural_4 = {
        "deal": structural["negotiatedResolution"],
        "escalation": structural["escalationCatastrophe"],
        "protracted": structural["protractedContinuation"],
        "intervention": structural["internationalIntervention"],
    }

    # Layer 2: Historical analogs
    analogs = historical_analog_projection(s)
    historical = analogs["outcome_dist"]

    # Layer 3: Market signals (Polymarket — when available)
    e = s.exotic_signals
    market = {
        "deal": e.polymarket_deal_by_jun30_pct / 100 if e.polymarket_deal_by_jun30_pct else None,
        "protracted": None,
        "escalation": None,
        "intervention": None,
    }

    # Layer 4: Regime fracture as discount on protracted (regime collapse → deal or intervention)
    fracture_p = regime_fracture_probability(s)

    # ---- Ensemble (weights tunable) ----
    # 0.45 structural + 0.30 historical + 0.20 market (when available) + 0.05 fracture-adjustment
    final = {}
    for bucket in ["deal", "escalation", "protracted", "intervention"]:
        layers = []
        weights = []
        if bucket in structural_4:
            layers.append(structural_4[bucket])
            weights.append(0.45)
        if bucket in historical:
            layers.append(historical[bucket])
            weights.append(0.30)
        if market.get(bucket) is not None:
            layers.append(market[bucket])
            weights.append(0.20)
        wsum = sum(weights)
        final[bucket] = sum(L * w for L, w in zip(layers, weights)) / wsum if wsum > 0 else 0.0

    # Fracture adjustment: high fracture probability shifts mass from protracted -> deal + intervention
    if fracture_p > 0.20:
        shift = (fracture_p - 0.20) * 0.5
        moved = min(shift, final["protracted"] * 0.5)
        final["protracted"] -= moved
        final["deal"] += moved * 0.6
        final["intervention"] += moved * 0.4

    # Renormalize
    total = sum(final.values())
    if total > 0:
        for k in final:
            final[k] = round(final[k] / total, 3)

    # Add residual "other" bucket
    final["other"] = round(max(0.0, 1.0 - sum(final.values())), 3)

    # Confidence score: 1 - max-pairwise-disagreement across layers
    layer_disagreement = 0.0
    if "deal" in historical and "deal" in structural_4:
        layer_disagreement = max(layer_disagreement, abs(historical["deal"] - structural_4["deal"]))
    if market.get("deal") is not None:
        layer_disagreement = max(layer_disagreement, abs(market["deal"] - structural_4["deal"]))
    confidence = round(max(0.0, 1.0 - layer_disagreement * 1.5), 2)

    return {
        "outcome_dist": final,
        "layer_contributions": {
            "structural": structural_4,
            "historical": historical,
            "market": {k: v for k, v in market.items() if v is not None},
            "fracture_adjustment": fracture_p,
        },
        "confidence_score": confidence,
        "top_analog": analogs["top_analog"],
        "median_resolution_days_analog": analogs["median_resolution_days"],
        "top_analog_lesson": analogs["top_lesson"],
    }


# ---------------------------------------------------------------------------
# Intelligence-product layer — what an analyst would surface for action
# ---------------------------------------------------------------------------

def alpha_signals(s: Signals, synthesis: dict) -> list[dict]:
    """The model-vs-consensus deltas — where there's edge.

    These are the highest-value outputs: "model says X, market says Y, here is
    why model is right (or right to disagree)." This is the alpha.
    """
    e = s.exotic_signals
    out = []
    final = synthesis["outcome_dist"]

    # Deal probability vs Polymarket
    if e.polymarket_deal_by_jun30_pct is not None:
        market_pct = e.polymarket_deal_by_jun30_pct
        model_pct = round(final.get("deal", 0) * 100)
        delta = model_pct - market_pct
        if abs(delta) >= 5:
            direction = "LONG" if delta > 0 else "SHORT"
            out.append({
                "signal": "deal_probability_vs_polymarket",
                "model_pct": model_pct,
                "market_pct": market_pct,
                "delta_pp": delta,
                "trade": f"{direction} Polymarket 'deal by Jun 30' contract",
                "size_conviction": min(1.0, abs(delta) / 20),
                "reasoning": "Model + historical analogs disagree with prediction-market pricing",
            })

    # Brent oil — if model expects escalation but market shows backwardation
    escalation_p = final.get("escalation", 0)
    if escalation_p > 0.40 and e.brent_wti_spread_usd < 15:
        out.append({
            "signal": "oil_escalation_underpricing",
            "trade": "LONG Brent calls $130 strike, 30-60 DTE",
            "size_conviction": min(1.0, (escalation_p - 0.40) * 3),
            "reasoning": (
                f"Model assigns {escalation_p*100:.0f}% escalation probability but Brent-WTI spread "
                f"(${e.brent_wti_spread_usd}) suggests market is not pricing tail risk to Hormuz/Bab al-Mandab "
                f"closure. Skew is asymmetric: oil up >$30 if escalation, modestly down if deal."
            ),
        })

    # Insurance / war-risk premium dislocation
    if e.hormuz_war_risk_premium_pct < 0.6 and escalation_p > 0.35:
        out.append({
            "signal": "war_risk_premium_underpriced",
            "trade": "LONG marine war-risk insurance carriers (Lloyd's syndicates) or VIX-equivalent",
            "size_conviction": 0.6,
            "reasoning": "Lloyd's premium not yet pricing model's escalation probability",
        })

    # Iran rial collapse trade (capital-flight asymmetric)
    if e.rial_official_per_usd and e.rial_black_market_per_usd:
        gap = e.rial_black_market_per_usd / e.rial_official_per_usd
        if gap > 1.5:
            out.append({
                "signal": "iran_rial_capital_flight",
                "trade": "LONG gold (XAU); LONG bitcoin Iran-premium arbitrage (off-shore)",
                "size_conviction": min(1.0, (gap - 1.0) / 2),
                "reasoning": (
                    f"Black-market rate {round(gap*100)}% premium to official — "
                    f"capital flight intensifies; gold + crypto absorb flow"
                ),
            })

    # Convergence / regime-fracture asymmetry
    fracture_p = synthesis["layer_contributions"].get("fracture_adjustment", 0)
    if fracture_p > 0.18:
        out.append({
            "signal": "regime_fracture_underpriced",
            "trade": "LONG Iran-restoration plays (frozen ADRs proxies); LONG OPEC-spare-capacity stories",
            "size_conviction": min(1.0, fracture_p * 3),
            "reasoning": (
                f"Regime fracture probability at {fracture_p*100:.0f}% materially exceeds "
                f"market consensus (<5%). Asymmetric payoff: small cost of carry, large convex upside."
            ),
        })

    return out


def crystallization_triggers(s: Signals) -> list[dict]:
    """Specific forward events that would meaningfully shift probabilities.

    'If X happens within Y days, P(outcome Z) shifts to ~W%' — the daily
    intelligence product an analyst writes for their principal.
    """
    triggers = [
        {
            "trigger": "Khamenei dies or steps down",
            "watch_for": "Public-appearance frequency drops to 0; mobilization at Tehran University",
            "horizon_days": 90,
            "prior_p": 0.10,  # rough actuarial + observed health concern
            "if_fires_p_deal": 0.45,
            "if_fires_p_escalation": 0.20,
            "if_fires_p_protracted": 0.20,
            "if_fires_p_intervention": 0.15,
            "reasoning": "Mojtaba succession ≠ guaranteed; faction war during transition; deal window opens via Pezeshkian or hardline doubles down.",
        },
        {
            "trigger": "Iran formally accepts deferred-nuclear framework",
            "watch_for": "Pakistani mediator carries proposal back to Trump; State Dept readout uses 'constructive'",
            "horizon_days": 30,
            "prior_p": 0.15,
            "if_fires_p_deal": 0.70,
            "if_fires_p_escalation": 0.05,
            "if_fires_p_protracted": 0.20,
            "if_fires_p_intervention": 0.05,
            "reasoning": "If Iran can climb-down on optics, Trump can claim victory, ego-lock breaks.",
        },
        {
            "trigger": "CENTCOM strike on power grid or oil infrastructure",
            "watch_for": "Trump truth-social pre-announcement; Saudi/UAE air-defense activation",
            "horizon_days": 14,
            "prior_p": 0.18,
            "if_fires_p_deal": 0.05,
            "if_fires_p_escalation": 0.55,
            "if_fires_p_protracted": 0.10,
            "if_fires_p_intervention": 0.30,
            "reasoning": "CENTCOM plan briefed = pre-positioning; Iran retaliatory doctrine = wide attack",
        },
        {
            "trigger": "US gas price crosses $4.50",
            "watch_for": "Sustained 7-day average above threshold; AAA national average",
            "horizon_days": 21,
            "prior_p": 0.45,
            "if_fires_p_deal": 0.30,  # Trump exit pressure spike
            "if_fires_p_escalation": 0.20,
            "if_fires_p_protracted": 0.40,
            "if_fires_p_intervention": 0.10,
            "reasoning": "Political pain threshold; midterm calculus dominates — Trump pivots to deal posture",
        },
        {
            "trigger": "China announces Iranian oil sanctions enforcement",
            "watch_for": "MOFCOM statement; Sinopec halts Iranian crude",
            "horizon_days": 60,
            "prior_p": 0.05,
            "if_fires_p_deal": 0.55,
            "if_fires_p_escalation": 0.10,
            "if_fires_p_protracted": 0.30,
            "if_fires_p_intervention": 0.05,
            "reasoning": "Iran's economic lifeline cut; regime forced to negotiate or face collapse",
        },
        {
            "trigger": "Iranian dark fleet seized in third country",
            "watch_for": "Indonesia/Malaysia announce; insurance war-risk premium spikes",
            "horizon_days": 45,
            "prior_p": 0.20,
            "if_fires_p_deal": 0.10,
            "if_fires_p_escalation": 0.45,
            "if_fires_p_protracted": 0.30,
            "if_fires_p_intervention": 0.15,
            "reasoning": "IRGC retaliation across theater; sanctions compliance war",
        },
        {
            "trigger": "Major Hezbollah attack inside Israeli population center",
            "watch_for": "Drone/rocket reaches Tel Aviv; civilian casualties >10",
            "horizon_days": 30,
            "prior_p": 0.25,
            "if_fires_p_deal": 0.05,
            "if_fires_p_escalation": 0.65,
            "if_fires_p_protracted": 0.15,
            "if_fires_p_intervention": 0.15,
            "reasoning": "Israel responds with force decoupling; multi-front spiral; US drawn in deeper",
        },
    ]
    return triggers


def tail_risks(s: Signals, synthesis: dict) -> list[dict]:
    """Low-probability, high-impact scenarios — what nobody is pricing."""
    return [
        {
            "scenario": "Iran tests nuclear device underground",
            "probability_60d": 0.03,
            "impact_severity": 10,
            "indicator_to_watch": "Seismic activity at Sanjarian / Fordow; IAEA emergency board",
            "if_realized": "Brent +$80; Israel preemptive doctrine activates; NPT collapse cascade",
            "trade_pre_event": "LONG OTM oil calls; LONG defense; LONG long-bond convexity",
        },
        {
            "scenario": "Khamenei assassinated (internal or external)",
            "probability_60d": 0.04,
            "impact_severity": 9,
            "indicator_to_watch": "IRGC mobilization signs; sudden state-media silence on Khamenei",
            "if_realized": "Multi-faction Iran civil conflict; Mojtaba uncontested OR coup; ALL bets reset",
            "trade_pre_event": "LONG VIX; LONG gold; SHORT EM equity; CASH",
        },
        {
            "scenario": "Trump declares 'mission accomplished' and withdraws",
            "probability_60d": 0.07,
            "impact_severity": 7,
            "indicator_to_watch": "Truth Social; surprise White House podium; gas price > $4.60",
            "if_realized": "Brent -$25; Iran wins de facto; nuclear program intact; Israel furious",
            "trade_pre_event": "LONG SPY; LONG defensives; SHORT oil",
        },
        {
            "scenario": "Saudi Arabia signs separate peace with Iran",
            "probability_60d": 0.06,
            "impact_severity": 8,
            "indicator_to_watch": "MBS-Khamenei phone call rumored; Riyadh-Tehran flight resumption",
            "if_realized": "GCC realignment locks in; US loses Gulf influence permanently; oil normalizes",
            "trade_pre_event": "LONG GCC equity; LONG MENA infrastructure; SHORT Saudi defense imports",
        },
        {
            "scenario": "Hormuz physically blocked by sunken VLCC",
            "probability_60d": 0.08,
            "impact_severity": 9,
            "indicator_to_watch": "IRGC fast-boats with limpet mines; insurer suspending Hormuz coverage entirely",
            "if_realized": "Brent +$60 in 48h; Asia oil rationing; Singapore strategic reserves drawn",
            "trade_pre_event": "LONG Brent calls; LONG tanker rates (BDRY); LONG strategic petroleum holders",
        },
        {
            "scenario": "Russia covertly transfers Iskander or Kh-101 to Iran",
            "probability_60d": 0.05,
            "impact_severity": 8,
            "indicator_to_watch": "Russian Il-76 traffic Tehran; Iranian state TV showcase of new capability",
            "if_realized": "Saudi/Israeli air-defense overwhelmed; US doctrine forced to 1st-strike",
            "trade_pre_event": "LONG defense contractors; LONG missile-defense names; LONG defense ETFs",
        },
    ]


def contrarian_check(s: Signals, synthesis: dict) -> dict:
    """What would make the current prediction wrong? The discipline of falsifiability."""
    final = synthesis["outcome_dist"]
    top_outcome = max(final.items(), key=lambda kv: kv[1])
    return {
        "current_top_outcome": top_outcome[0],
        "current_top_pct": round(top_outcome[1] * 100),
        "what_would_invalidate": _falsifiers_for(top_outcome[0]),
        "anti_consensus_warning": (
            "If 5+ of these falsifiers fire within 14 days, the model has been wrong-footed; "
            "rerun with revised priors. Discipline: track which falsifiers fired, not which didn't."
        ),
    }


def _falsifiers_for(outcome: str) -> list[str]:
    by_outcome = {
        "deal": [
            "Khamenei makes 2nd public anti-deal vow within 7 days",
            "IRGC seizes 3rd US-flagged vessel",
            "Mojtaba public appearance signaling succession lock",
            "Trump posts 'TIME IS OVER' truth-social with deadline",
            "Pakistan ends mediator role",
        ],
        "escalation": [
            "Iran transmits revised acceptable proposal via Oman",
            "CENTCOM strike plan publicly shelved",
            "Polymarket ceasefire-holds spikes above 40%",
            "Hegseth replaced as SecDef",
            "Khamenei makes conciliatory statement",
        ],
        "protracted": [
            "Major military strike (either direction)",
            "Sudden diplomatic breakthrough at any G20 sideline",
            "Khamenei dies or visibly incapacitated",
            "China announces enforcement against Iranian crude",
            "Saudi-Iran direct peace announcement",
        ],
        "intervention": [
            "China publicly aligns with US sanctions",
            "GCC re-aligns with US (re-enters OPEC, restores air corridors)",
            "Russia withdraws diplomatic cover",
            "EU passes unified sanctions package",
            "UN Security Council unanimous resolution",
        ],
        "other": ["model uncertainty too high to enumerate falsifiers"],
    }
    return by_outcome.get(outcome, [])


def predictive_framework_doc() -> str:
    """Plain-English explanation of how the predictive framework works."""
    return (
        "## Predictive Framework v0.1\n\n"
        "Every emit produces an outcome distribution from FOUR independent layers:\n\n"
        "1. **Structural model (45% weight)** — the four condition scores (deal availability × US exit "
        "pressure × Iran acceptance, plus escalation proximity), each computed from raw `condition_inputs` "
        "and then ADJUSTED by the psychology + dynamics + history modifiers. This is the dashboard's "
        "bottom-up causal model.\n\n"
        "2. **Historical analogs (30% weight)** — weighted similarity scores against 10 past conflicts. "
        "Each analog carries an empirical outcome distribution + median resolution time + a structured "
        "lesson. The current top analog tells you what trajectory historical pattern-matching predicts.\n\n"
        "3. **Market layer (20% weight, when available)** — Polymarket / Kalshi / Metaculus contracts on "
        "specific outcomes. Most efficient signal when data is available.\n\n"
        "4. **Regime fracture adjustment (5% weight)** — derived from the Iran-internal pressure stack. "
        "When fracture probability exceeds 20%, mass shifts from `protracted` to `deal` + `intervention`.\n\n"
        "**Confidence score**: 1 minus pairwise disagreement across the layers. Low confidence when the "
        "layers vote differently — read this as 'one of these models is wrong; figure out which.'\n\n"
        "**Forward projections** (7/14/30 days) come from a separate trajectory analysis: short-horizon "
        "actor pressures dominate the 7-day, structural pressures (oil revenue collapse, electoral cycle, "
        "succession overhang) dominate the 30-day.\n\n"
        "**Exotic triggers**: discrete signal patterns that have historically preceded specific outcomes "
        "(rial dual-rate collapse, Friday-prayer attendance below 30%, IRGC promotion velocity above 0.8, "
        "etc.). When fired, they're surfaced as named patterns with implied score deltas + source-pattern "
        "references.\n\n"
        "Methodology evolves; engine version is stamped in every emit + snapshot for backtesting."
    )

