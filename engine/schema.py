"""Pydantic schema for signals.yaml — the canonical hand-edited source."""
from __future__ import annotations

from datetime import date as _date
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


CeasefireStatus = Literal["active", "hollow", "extended_indef", "collapsed", "none"]


class Meta(BaseModel):
    model_config = ConfigDict(extra="forbid")
    day: int = Field(ge=1, description="war day (1-indexed from Feb 28)")
    cf_day: Optional[int] = Field(default=None, description="ceasefire day (1-indexed from cf start), null pre-ceasefire")
    date: _date
    notes: list[str] = Field(default_factory=list)


class Mode(BaseModel):
    model_config = ConfigDict(extra="forbid")
    ceasefire_status: CeasefireStatus = "none"


class Constants(BaseModel):
    model_config = ConfigDict(extra="forbid")
    pre_war_brent: float = 65.0
    pre_war_hormuz: float = 135.0
    pre_war_gas: float = 3.00
    d1_missiles: int = 480
    ceasefire_start_day: int = 39
    ceasefire_original_deadline_day: int = 53


class TodayScalars(BaseModel):
    model_config = ConfigDict(extra="forbid")
    brent: float
    brent_intraday_high: Optional[float] = None
    wti: Optional[float] = None
    gas_price: float
    hormuz_vessels: int
    rial_per_usd: Optional[int] = None
    zero_attack_streak_days: int = 0
    internet_blackout_hours: Optional[int] = None
    ships_stranded: Optional[int] = None
    us_kia: int = 0
    us_wounded: int = 0
    us_aircraft_lost: int = 0
    lebanon_killed: int = 0
    iran_civ_killed_hrana: int = 0
    iran_civ_killed_aj: int = 0
    iran_oil_storage_days_remaining: Optional[int] = None
    coalition_cohesion_score: float = 5.0


class DealInputs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    iran_proposal_active: bool = False
    us_acceptance_signal: float = Field(default=0.0, ge=0.0, le=1.0)
    nuclear_gap_pp: int = Field(default=0, ge=0, description="years apart on enrichment-freeze duration")
    score_override: Optional[float] = Field(default=None, ge=0.0, le=1.0)


class UsExitInputs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    gas_pain_above_threshold: bool = False
    war_powers_passed: bool = False
    centcom_strike_plan_briefed: bool = False
    score_override: Optional[float] = Field(default=None, ge=0.0, le=1.0)


class IranAcceptanceInputs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    khamenei_public_vow_against: bool = False
    irgc_in_charge: bool = False
    formal_proposals_rejected: int = 0
    score_override: Optional[float] = Field(default=None, ge=0.0, le=1.0)


class EscalationInputs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    centcom_briefed: bool = False
    hezbollah_action_recent: bool = False
    new_blockade_action: bool = False
    score_override: Optional[float] = Field(default=None, ge=0.0, le=1.0)


class ConditionInputs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    deal: DealInputs = Field(default_factory=DealInputs)
    us_exit: UsExitInputs = Field(default_factory=UsExitInputs)
    iran_acceptance: IranAcceptanceInputs = Field(default_factory=IranAcceptanceInputs)
    escalation: EscalationInputs = Field(default_factory=EscalationInputs)


# ---------------------------------------------------------------------------
# Stakeholder psychology layer
# ---------------------------------------------------------------------------
# Each principal actor is scored on 7 decision-theoretic dimensions, all 0..1
# unless otherwise noted. These feed into the four condition scores via weighted
# aggregation (see compute.psych_modifiers).

DecisionStyle = Literal["transactional", "ideological", "institutional", "personalist", "opportunistic"]


class PsychProfile(BaseModel):
    """Psychological state for a single actor.

    Core 7 decision-theory dimensions + 5 personality-specific traits.
    All 0..1 floats unless otherwise noted. Update daily as evidence shifts.
    """
    model_config = ConfigDict(extra="forbid")
    # ----- Core decision-theory dimensions -----
    risk_tolerance: float = Field(default=0.5, ge=0.0, le=1.0,
                                  description="Willingness to accept catastrophic downside")
    loss_aversion: float = Field(default=0.5, ge=0.0, le=1.0,
                                 description="How much they fear losing what they have vs gaining new")
    public_commitment: float = Field(default=0.5, ge=0.0, le=1.0,
                                     description="How publicly staked their position is — ego cost of climbdown")
    time_horizon_days: int = Field(default=180, ge=1,
                                   description="Effective decision horizon (a week vs a decade matters)")
    audience_domestic_weight: float = Field(default=0.7, ge=0.0, le=1.0,
                                            description="0=plays to international audience, 1=domestic only")
    coalition_dependency: float = Field(default=0.4, ge=0.0, le=1.0,
                                        description="How constrained by their faction/coalition (high = boxed in)")
    flexibility: float = Field(default=0.5, ge=0.0, le=1.0,
                               description="Substantive — red lines (low) vs negotiables (high)")
    decision_style: DecisionStyle = "transactional"
    # ----- Personality-specific traits (the 'character' layer) -----
    ego_size: float = Field(default=0.4, ge=0.0, le=1.0,
                            description="Self-image-as-policy-driver. Trump=very high, technocrats=low")
    need_for_credit: float = Field(default=0.4, ge=0.0, le=1.0,
                                   description="Demands visible attribution for outcomes")
    religious_zeal: float = Field(default=0.0, ge=0.0, le=1.0,
                                  description="Faith-based commitment overrides cost-benefit. IRGC + Khamenei high")
    legacy_calculus: float = Field(default=0.3, ge=0.0, le=1.0,
                                   description="Decisions weighted by 'how will history remember me'")
    succession_anxiety: float = Field(default=0.0, ge=0.0, le=1.0,
                                      description="Decisions distorted by need to secure successor")
    notes: str = ""


# ---------------------------------------------------------------------------
# Iran-specific regime/population split
# ---------------------------------------------------------------------------
# The dashboard's most consequential Iran dynamic: the regime (~10% public
# support per polling) controls all decision-making but the population
# experiences the war's economic pain. The population can't act because the
# regime is "wild and armed," BUT extreme population pressure feeds back into
# regime calculus (street threats = loss aversion spike).

class IranRegimeDynamics(BaseModel):
    model_config = ConfigDict(extra="forbid")
    regime_public_support_pct: float = Field(default=10.0, ge=0.0, le=100.0,
                                             description="% of Iranians who actually support the regime")
    regime_grip_strength: float = Field(default=0.85, ge=0.0, le=1.0,
                                        description="How firmly regime controls security apparatus + media")
    population_restiveness: float = Field(default=0.4, ge=0.0, le=1.0,
                                          description="Active dissent — strikes, protests, online mobilization")
    population_war_fatigue: float = Field(default=0.85, ge=0.0, le=1.0,
                                          description="How exhausted the population is by economic + military toll")
    regime_brittleness: float = Field(default=0.35, ge=0.0, le=1.0,
                                      description="Probability of fracture under shock — a soft regime cracks fast")
    economic_pain_index: float = Field(default=0.9, ge=0.0, le=1.0,
                                       description="Population-level: rial collapse, inflation, food prices")
    notes: str = ""


class Stakeholders(BaseModel):
    """Named principals. Defaults reflect baseline well-known dispositions; overwrite daily."""
    model_config = ConfigDict(extra="forbid")
    # ===== US side =====
    trump: PsychProfile = Field(default_factory=lambda: PsychProfile(
        risk_tolerance=0.7, loss_aversion=0.4, public_commitment=0.85,
        time_horizon_days=14, audience_domestic_weight=0.9, coalition_dependency=0.2,
        flexibility=0.55, decision_style="transactional",
        ego_size=0.95, need_for_credit=0.95, religious_zeal=0.05,
        legacy_calculus=0.6, succession_anxiety=0.0,
        notes="Maximum ego-driven; deal-maker mythology; needs visible win; climb-down cost = self-image"
    ))
    vance: PsychProfile = Field(default_factory=lambda: PsychProfile(
        risk_tolerance=0.45, loss_aversion=0.55, public_commitment=0.5,
        time_horizon_days=120, audience_domestic_weight=0.85, coalition_dependency=0.6,
        flexibility=0.6, decision_style="institutional",
        ego_size=0.7, need_for_credit=0.6, religious_zeal=0.3,
        legacy_calculus=0.7, succession_anxiety=0.5,
        notes="Restrainer; 2028 shadow distorts every move; cannot be seen as soft"
    ))
    rubio: PsychProfile = Field(default_factory=lambda: PsychProfile(
        risk_tolerance=0.55, loss_aversion=0.5, public_commitment=0.65,
        time_horizon_days=90, audience_domestic_weight=0.7, coalition_dependency=0.7,
        flexibility=0.5, decision_style="institutional",
        ego_size=0.55, need_for_credit=0.5, religious_zeal=0.2,
        legacy_calculus=0.6, succession_anxiety=0.0,
        notes="Hawk-leaning State principal; brokers Lebanon track; constrained by WH line"
    ))
    hegseth: PsychProfile = Field(default_factory=lambda: PsychProfile(
        risk_tolerance=0.75, loss_aversion=0.3, public_commitment=0.8,
        time_horizon_days=30, audience_domestic_weight=0.9, coalition_dependency=0.4,
        flexibility=0.25, decision_style="personalist",
        ego_size=0.7, need_for_credit=0.6, religious_zeal=0.35,
        legacy_calculus=0.4, succession_anxiety=0.0,
        notes="Military-action preference; 'ready to restart combat' rhetoric; Christian-nationalist register"
    ))
    # ===== Iran regime side =====
    khamenei: PsychProfile = Field(default_factory=lambda: PsychProfile(
        risk_tolerance=0.65, loss_aversion=0.85, public_commitment=0.95,
        time_horizon_days=3650, audience_domestic_weight=0.55, coalition_dependency=0.3,
        flexibility=0.15, decision_style="ideological",
        ego_size=0.75, need_for_credit=0.6, religious_zeal=0.95,
        legacy_calculus=0.95, succession_anxiety=0.85,
        notes="Public nuclear/missile vow forecloses concessions; 86 yrs old; legacy + succession dominate"
    ))
    pezeshkian: PsychProfile = Field(default_factory=lambda: PsychProfile(
        risk_tolerance=0.4, loss_aversion=0.7, public_commitment=0.5,
        time_horizon_days=365, audience_domestic_weight=0.85, coalition_dependency=0.85,
        flexibility=0.65, decision_style="institutional",
        ego_size=0.4, need_for_credit=0.4, religious_zeal=0.35,
        legacy_calculus=0.5, succession_anxiety=0.2,
        notes="Civilian-pragmatic; constrained by Khamenei + IRGC; voice but no decision power"
    ))
    araghchi: PsychProfile = Field(default_factory=lambda: PsychProfile(
        risk_tolerance=0.4, loss_aversion=0.6, public_commitment=0.55,
        time_horizon_days=120, audience_domestic_weight=0.55, coalition_dependency=0.85,
        flexibility=0.7, decision_style="transactional",
        ego_size=0.4, need_for_credit=0.5, religious_zeal=0.25,
        legacy_calculus=0.4, succession_anxiety=0.0,
        notes="JCPOA-era diplomat; sidelined by IRGC; messenger more than principal"
    ))
    irgc: PsychProfile = Field(default_factory=lambda: PsychProfile(
        risk_tolerance=0.85, loss_aversion=0.45, public_commitment=0.9,
        time_horizon_days=180, audience_domestic_weight=0.6, coalition_dependency=0.4,
        flexibility=0.2, decision_style="ideological",
        ego_size=0.6, need_for_credit=0.55, religious_zeal=0.9,
        legacy_calculus=0.55, succession_anxiety=0.4,
        notes="Theocratic-militant; ascendant since FM track collapsed; institutional + ideological"
    ))
    mojtaba_khamenei: PsychProfile = Field(default_factory=lambda: PsychProfile(
        risk_tolerance=0.5, loss_aversion=0.85, public_commitment=0.4,
        time_horizon_days=3650, audience_domestic_weight=0.8, coalition_dependency=0.7,
        flexibility=0.4, decision_style="ideological",
        ego_size=0.55, need_for_credit=0.45, religious_zeal=0.85,
        legacy_calculus=0.7, succession_anxiety=0.95,
        notes="Likely successor; succession-mode = risk-averse + narrow audience + religious branding"
    ))
    # ===== Iran POPULATION (separate from regime) =====
    iran_population: PsychProfile = Field(default_factory=lambda: PsychProfile(
        risk_tolerance=0.2, loss_aversion=0.95, public_commitment=0.15,
        time_horizon_days=30, audience_domestic_weight=1.0, coalition_dependency=0.05,
        flexibility=0.85, decision_style="opportunistic",
        ego_size=0.0, need_for_credit=0.0, religious_zeal=0.2,
        legacy_calculus=0.1, succession_anxiety=0.0,
        notes=("90%+ would accept any deal that ends economic pain. Cannot ACT — regime is "
               "armed and willing to shoot. But extreme restiveness raises regime loss-aversion.")
    ))
    # ===== Mediators / wildcards =====
    putin: PsychProfile = Field(default_factory=lambda: PsychProfile(
        risk_tolerance=0.7, loss_aversion=0.6, public_commitment=0.4,
        time_horizon_days=730, audience_domestic_weight=0.5, coalition_dependency=0.2,
        flexibility=0.7, decision_style="opportunistic",
        ego_size=0.85, need_for_credit=0.7, religious_zeal=0.25,
        legacy_calculus=0.7, succession_anxiety=0.4,
        notes="Leverage-seeker; offers diplomatic cover; price-of-oil beneficiary; sees crisis as asset"
    ))
    munir: PsychProfile = Field(default_factory=lambda: PsychProfile(
        risk_tolerance=0.5, loss_aversion=0.5, public_commitment=0.4,
        time_horizon_days=365, audience_domestic_weight=0.6, coalition_dependency=0.5,
        flexibility=0.7, decision_style="institutional",
        ego_size=0.55, need_for_credit=0.6, religious_zeal=0.3,
        legacy_calculus=0.55, succession_anxiety=0.2,
        notes="Pakistan Army Chief; primary intermediary; survival depends on producing a result"
    ))
    netanyahu: PsychProfile = Field(default_factory=lambda: PsychProfile(
        risk_tolerance=0.7, loss_aversion=0.4, public_commitment=0.85,
        time_horizon_days=180, audience_domestic_weight=0.85, coalition_dependency=0.55,
        flexibility=0.3, decision_style="personalist",
        ego_size=0.85, need_for_credit=0.7, religious_zeal=0.25,
        legacy_calculus=0.7, succession_anxiety=0.0,
        notes="Lebanon front escalator; war = political oxygen; personal legal jeopardy distorts incentives"
    ))
    hezbollah: PsychProfile = Field(default_factory=lambda: PsychProfile(
        risk_tolerance=0.6, loss_aversion=0.7, public_commitment=0.7,
        time_horizon_days=365, audience_domestic_weight=0.7, coalition_dependency=0.8,
        flexibility=0.4, decision_style="ideological",
        ego_size=0.4, need_for_credit=0.5, religious_zeal=0.85,
        legacy_calculus=0.5, succession_anxiety=0.2,
        notes="Bleeding from Israel strikes; 2,521+ killed; calls truces 'meaningless'; theological"
    ))


# (removed obsolete duplicate Stakeholders — earlier definition above is canonical)


class ViolationEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")
    severity: int = Field(ge=1, le=3)
    actor: str
    target: str
    description: str
    type: str = "strike"


class NegotiationEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")
    status: str = "in_progress"
    description: str


class RecoveryPoint(BaseModel):
    model_config = ConfigDict(extra="forbid")
    hormuz_daily: int
    brent_daily: float
    ships_stranded: int


class DailySeriesPoint(BaseModel):
    model_config = ConfigDict(extra="forbid")
    missiles: int = 0
    drones: int = 0


class DailyRow(BaseModel):
    model_config = ConfigDict(extra="forbid")
    date: str
    missiles: int = 0
    drones: int = 0
    primary_targets: str = ""
    capability: str = ""
    cost: str = ""
    assessment: str = ""


class NewEvents(BaseModel):
    model_config = ConfigDict(extra="forbid")
    violation: Optional[ViolationEvent] = None
    negotiation: Optional[NegotiationEvent] = None
    recovery_point: Optional[RecoveryPoint] = None
    daily_series: DailySeriesPoint = Field(default_factory=DailySeriesPoint)
    daily_row: Optional[DailyRow] = None


# ---------------------------------------------------------------------------
# US internal dynamics (mirrors Iran regime/population split on US side)
# ---------------------------------------------------------------------------

class USDynamics(BaseModel):
    """US internal pressure system — admin, Congress, public, deep-state, base."""
    model_config = ConfigDict(extra="forbid")
    # Trump-coalition internal
    maga_base_war_support: float = Field(default=0.55, ge=0.0, le=1.0,
                                         description="MAGA base — supports strikes on Iran but war fatigue rising")
    establishment_gop_pressure: float = Field(default=0.4, ge=0.0, le=1.0,
                                              description="Traditional GOP — hawkish but want clean exit")
    democrats_pressure_to_end: float = Field(default=0.85, ge=0.0, le=1.0,
                                             description="Dem opposition + war powers push")
    deep_state_alignment: float = Field(default=0.5, ge=0.0, le=1.0,
                                        description="CENTCOM, IC, State alignment with WH line — drift = friction")
    # Electoral / political pain
    gas_price_pain_index: float = Field(default=0.6, ge=0.0, le=1.0,
                                        description="Derived from gas_price; threshold-based political risk")
    midterms_proximity_days: int = Field(default=550, ge=0,
                                         description="Days to Nov 2026 midterms — distorts WH risk calculus")
    approval_rating_war: float = Field(default=0.35, ge=0.0, le=1.0,
                                       description="% approving Trump's handling of Iran")
    # Financial / market
    market_recession_prob: float = Field(default=0.4, ge=0.0, le=1.0,
                                         description="Fed/markets pricing recession from oil + supply shock")
    # Ideological / cultural
    christian_nationalist_pressure: float = Field(default=0.45, ge=0.0, le=1.0,
                                                  description="Hegseth/Vance-aligned cohort wanting biblical-frame outcome")
    isolationist_resurgence: float = Field(default=0.5, ge=0.0, le=1.0,
                                           description="MAGA-isolationist + Tucker-axis — 'why are we there'")
    notes: str = ""


# ---------------------------------------------------------------------------
# Iran deep dynamics (beyond regime/population — clerical, succession, ethnic)
# ---------------------------------------------------------------------------

class IranDeepDynamics(BaseModel):
    """Layered Iran-internal pressures the dashboard's surface metrics miss."""
    model_config = ConfigDict(extra="forbid")
    # Clerical establishment vs IRGC militancy
    clerical_irgc_alignment: float = Field(default=0.7, ge=0.0, le=1.0,
                                           description="High = clerics back IRGC; low = moderating clergy push back")
    qom_seminary_dissent: float = Field(default=0.15, ge=0.0, le=1.0,
                                        description="Quietist clergy distancing from regime")
    # Succession anxiety (Khamenei is 86)
    khamenei_health_concern: float = Field(default=0.4, ge=0.0, le=1.0,
                                           description="How much succession is shaping decisions today")
    mojtaba_succession_lock: float = Field(default=0.6, ge=0.0, le=1.0,
                                           description="Probability Mojtaba inherits — distorts faction behavior")
    # Ethnic / regional pressure points
    kurd_unrest: float = Field(default=0.4, ge=0.0, le=1.0,
                               description="Western Iran restive (40-yr pattern; Hengaw network active)")
    baluch_unrest: float = Field(default=0.5, ge=0.0, le=1.0,
                                 description="Southeast — Jaish al-Adl periodically active")
    arab_minority_unrest: float = Field(default=0.35, ge=0.0, le=1.0,
                                        description="Khuzestan — oil region restiveness")
    # Diaspora / external pressure
    diaspora_mobilization: float = Field(default=0.6, ge=0.0, le=1.0,
                                         description="LA/Toronto/London Iranian diaspora pushing regime change")
    # Economic structure
    oil_revenue_collapse_pct: float = Field(default=0.85, ge=0.0, le=1.0,
                                            description="% drop in oil export revenue — regime's lifeline")
    sanctioned_elite_wealth_at_risk: float = Field(default=0.7, ge=0.0, le=1.0,
                                                   description="Bonyad / IRGC business empire under pressure")
    # Military / operational
    proxy_network_coherence: float = Field(default=0.4, ge=0.0, le=1.0,
                                           description="Hezbollah + Houthi + Iraq militias coordination quality")
    nuclear_program_status: Literal["intact", "degraded", "crippled"] = "degraded"
    notes: str = ""


# ---------------------------------------------------------------------------
# World dynamics (mediator + great-power layer)
# ---------------------------------------------------------------------------

class WorldDynamics(BaseModel):
    """How the rest of the world is positioned — feeds intervention + isolation."""
    model_config = ConfigDict(extra="forbid")
    china_stance: Literal["pro_iran", "neutral_pro_iran", "neutral", "neutral_pro_us", "pro_us"] = "neutral_pro_iran"
    china_oil_buyer_committed: float = Field(default=0.7, ge=0.0, le=1.0,
                                             description="Will China keep buying Iranian oil despite blockade")
    russia_leverage_seeking: float = Field(default=0.85, ge=0.0, le=1.0,
                                           description="Russia using crisis to extract Western concessions on Ukraine")
    eu_unity: float = Field(default=0.4, ge=0.0, le=1.0,
                            description="EU coherence — France/UK refused blockade = low")
    gcc_realignment: float = Field(default=0.7, ge=0.0, le=1.0,
                                   description="Gulf states pulling away from US-led order — UAE OPEC exit signal")
    global_south_neutrality: float = Field(default=0.7, ge=0.0, le=1.0,
                                           description="Africa/LatAm/SE Asia non-aligned — refuses US framing")
    israel_independence_score: float = Field(default=0.85, ge=0.0, le=1.0,
                                             description="Israel acts unilaterally without US sign-off (Lebanon)")
    un_security_council_paralysis: float = Field(default=0.95, ge=0.0, le=1.0,
                                                 description="P5 unable to act — Russia/China veto US, US vetoes Iran")
    notes: str = ""


# ---------------------------------------------------------------------------
# Historical / ideological context (rarely changes, but conditions everything)
# ---------------------------------------------------------------------------

class HistoricalIdeology(BaseModel):
    """Long-arc structural factors that don't move daily but condition every actor's frame."""
    model_config = ConfigDict(extra="forbid")
    # Iran historical priors (1979 → present)
    iran_1979_revolution_legacy: float = Field(default=0.95, ge=0.0, le=1.0,
                                               description="Anti-imperial founding myth still load-bearing for regime")
    iran_iraq_war_trauma: float = Field(default=0.9, ge=0.0, le=1.0,
                                        description="8-yr war 1980-88; 'never again unprepared' shapes nuclear push")
    hostage_crisis_us_lens: float = Field(default=0.85, ge=0.0, le=1.0,
                                          description="444-day hostage crisis still defines US public view of Iran")
    soleimani_assassination_iran_lens: float = Field(default=0.9, ge=0.0, le=1.0,
                                                     description="2020 strike — IRGC blood debt + casus belli memory")
    jcpoa_collapse_iran_lens: float = Field(default=0.85, ge=0.0, le=1.0,
                                            description="'US can't be trusted on agreements' — undercuts deal viability")
    israel_existential_frame: float = Field(default=0.95, ge=0.0, le=1.0,
                                            description="Iran-as-existential-threat is structural in Israeli policy")
    shia_geopolitics: float = Field(default=0.8, ge=0.0, le=1.0,
                                    description="Shia crescent doctrine — Iran's regional axis identity")
    # US historical priors
    us_iraq_war_fatigue: float = Field(default=0.85, ge=0.0, le=1.0,
                                       description="2003-2011 + Afghanistan = strong public aversion to forever wars")
    us_october_7_pivot: float = Field(default=0.7, ge=0.0, le=1.0,
                                      description="Oct 2023 → Iran-as-axis recentered US strategy")
    # Trump-specific
    trump_jcpoa_personal_animus: float = Field(default=0.9, ge=0.0, le=1.0,
                                               description="JCPOA was Obama's win; Trump withdrawal 2018 = personal brand")
    # Universal
    nuclear_taboo_strength: float = Field(default=0.85, ge=0.0, le=1.0,
                                          description="Strength of 'no nuclear weapons used since 1945' norm")
    notes: str = ""


# ---------------------------------------------------------------------------
# Exotic / behavioral / out-of-band signals
# ---------------------------------------------------------------------------
# These are the "leading indicators of leading indicators" — signals that
# typically move BEFORE the headline metrics catch up. Many require dedicated
# data sources (Polymarket API, OFAC filings, AIS feeds, social analytics)
# but each can be hand-typed daily from observation as a starting point.

class ExoticSignals(BaseModel):
    """Out-of-band leading indicators that surface signals before headlines."""
    model_config = ConfigDict(extra="forbid")

    # ===== Iran economy / black market =====
    rial_official_per_usd: Optional[int] = Field(default=None,
        description="Official CBI rate; gap to black market = regime grip")
    rial_black_market_per_usd: Optional[int] = Field(default=None,
        description="Tehran bazaar rate — true currency confidence proxy")
    gold_price_tehran_per_gram_usd: Optional[float] = Field(default=None,
        description="Gold spike = capital flight + dollarization")
    bitcoin_iran_premium_pct: Optional[float] = Field(default=None,
        description="LocalBitcoins/Bisq Iran premium vs spot — sanctions-evasion intensity")
    cement_price_index_tehran: Optional[float] = Field(default=None,
        description="Industrial-supply prices = real-economy collapse leading indicator")

    # ===== Iran population behavior =====
    vpn_install_rate_index: float = Field(default=0.5, ge=0.0, le=1.0,
        description="VPN/Tor downloads — dissent + circumvention signal")
    starlink_terminals_estimated: int = Field(default=20000, ge=0,
        description="Active Starlink terminals in Iran — independent comms layer")
    google_search_passport_renewal: float = Field(default=0.5, ge=0.0, le=1.0,
        description="Search-trends passport/visa/emigration — exit-intention signal")
    google_search_protest_trend: float = Field(default=0.5, ge=0.0, le=1.0,
        description="Aggregated dissent-search index")

    # ===== Iran institutional / regime =====
    khamenei_public_appearance_freq_30d: int = Field(default=2, ge=0,
        description="Public appearances in last 30d — health/grip indicator")
    friday_prayer_attendance_index: float = Field(default=0.6, ge=0.0, le=1.0,
        description="Tehran University Friday prayer attendance vs baseline")
    irgc_promotion_velocity: float = Field(default=0.5, ge=0.0, le=1.0,
        description="Pace of IRGC commander promotions — ascendancy or purge?")
    bonyad_assets_frozen_estimate_usd_b: Optional[float] = Field(default=None,
        description="Foundation wealth under foreign sanctions — elite-pain indicator")

    # ===== Tanker / oil shadow market =====
    iranian_dark_fleet_active_tankers: Optional[int] = Field(default=None,
        description="AIS-off Iranian-linked tankers — sanctions-evasion fleet")
    china_iranian_oil_imports_kbpd: Optional[int] = Field(default=None,
        description="China's reported Iranian crude imports — sanctions-evasion lifeline")
    brent_wti_spread_usd: float = Field(default=10.0,
        description="Brent minus WTI — Hormuz premium isolation marker")
    hormuz_war_risk_premium_pct: float = Field(default=0.5, ge=0.0, le=1.0,
        description="Lloyd's / insurance industry war-risk premium for Hormuz transit")

    # ===== Market / prediction-market signals =====
    polymarket_ceasefire_holds_pct: int = Field(default=18, ge=0, le=100,
        description="Polymarket ceasefire-holds-by-X-date contract")
    polymarket_deal_by_jun30_pct: int = Field(default=15, ge=0, le=100)
    kalshi_oil_above_120_pct: Optional[int] = Field(default=None, ge=0, le=100,
        description="Kalshi event contract — Brent above $120 by end-of-month")
    metaculus_war_continues_2026_pct: Optional[int] = Field(default=None, ge=0, le=100)
    polymarket_volume_24h_usd: int = Field(default=280_000_000,
        description="24h Polymarket Iran-related contract volume — engagement intensity")

    # ===== US side =====
    google_search_iran_war_us: float = Field(default=0.6, ge=0.0, le=1.0,
        description="US Google trends — public attention to conflict")
    s_and_p_iran_correlated_drawdown_pct: Optional[float] = Field(default=None,
        description="S&P 500 drawdown specifically attributed to Iran exposure")
    cboe_oil_vix: Optional[float] = Field(default=None,
        description="OVX — implied volatility on oil futures")
    federal_funds_rate_pct: Optional[float] = Field(default=None,
        description="Fed has limited room — high rate = constrained recession response")

    # ===== Diplomatic / institutional =====
    iaea_inspector_access_score: float = Field(default=0.3, ge=0.0, le=1.0,
        description="IAEA monitoring access to Iranian nuclear sites")
    swift_iran_isolation_score: float = Field(default=0.95, ge=0.0, le=1.0,
        description="SWIFT/banking exclusion intensity")
    un_condemnation_resolutions_60d: int = Field(default=0,
        description="Count of UN resolutions condemning either side in last 60 days")
    ofac_designations_30d: int = Field(default=0,
        description="New OFAC SDN designations against Iranian entities in last 30 days")

    # ===== Proxy network signals =====
    houthi_attacks_red_sea_7d: int = Field(default=0)
    iraq_militia_attacks_us_bases_7d: int = Field(default=0)
    hezbollah_rocket_launches_7d: int = Field(default=0)
    syria_route_disruption_index: float = Field(default=0.7, ge=0.0, le=1.0,
        description="Iran-to-Hezbollah arms supply line health")

    # ===== Information / narrative =====
    iran_state_media_threat_level_idx: float = Field(default=0.7, ge=0.0, le=1.0,
        description="Press TV / Fars threat-rhetoric intensity")
    us_msm_war_coverage_index: float = Field(default=0.5, ge=0.0, le=1.0,
        description="Major US outlets dedicated coverage volume — sustained attention proxy")
    twitter_iranian_dissent_sentiment: float = Field(default=0.6, ge=0.0, le=1.0,
        description="Persian-language Twitter anti-regime sentiment intensity")

    notes: str = ""


# ---------------------------------------------------------------------------
# Historical analogs — past conflicts to compare current state against
# ---------------------------------------------------------------------------

HistoricalAnalog = Literal[
    "cuban_missile_crisis_1962",     # 13-day brink → de-escalation via back-channel
    "iran_iraq_war_endgame_1988",    # Khomeini "drinking poison" — when Iran has finally accepted
    "suez_crisis_1956",              # Western intervention → forced withdrawal
    "yom_kippur_war_1973",           # Surprise + oil shock + superpower brinksmanship
    "kuwait_invasion_1990_91",       # Coalition response + decisive military action
    "kosovo_intervention_1999",      # Air-only campaign → political settlement
    "syria_civil_war_2011_present",  # Protracted multi-actor stalemate
    "jcpoa_negotiation_2013_15",     # Years-long indirect → breakthrough framework
    "korean_war_armistice_1953",     # Ceasefire-without-peace, frozen conflict
    "october_war_aftermath_1973_75", # Henry Kissinger shuttle diplomacy
]


class HistoricalAnalogs(BaseModel):
    """Similarity scores to past conflicts — analog reasoning is core to forecasting."""
    model_config = ConfigDict(extra="forbid")
    cuban_missile_crisis_1962: float = Field(default=0.3, ge=0.0, le=1.0)
    iran_iraq_war_endgame_1988: float = Field(default=0.4, ge=0.0, le=1.0)
    suez_crisis_1956: float = Field(default=0.2, ge=0.0, le=1.0)
    yom_kippur_war_1973: float = Field(default=0.55, ge=0.0, le=1.0)
    kuwait_invasion_1990_91: float = Field(default=0.4, ge=0.0, le=1.0)
    kosovo_intervention_1999: float = Field(default=0.25, ge=0.0, le=1.0)
    syria_civil_war_2011_present: float = Field(default=0.5, ge=0.0, le=1.0)
    jcpoa_negotiation_2013_15: float = Field(default=0.45, ge=0.0, le=1.0)
    korean_war_armistice_1953: float = Field(default=0.6, ge=0.0, le=1.0)
    october_war_aftermath_1973_75: float = Field(default=0.5, ge=0.0, le=1.0)
    notes: str = ""


class Signals(BaseModel):
    """Top-level signals.yaml structure — the only file edited daily.

    Layered architecture (each layer changes at its own cadence):
      DAILY:    meta, today_scalars, new_events, exotic_signals (mostly)
      WEEKLY:   condition_inputs, stakeholders, iran_regime_dynamics,
                us_dynamics, iran_deep_dynamics, world_dynamics, historical_analogs
      RARELY:   historical_ideology, constants
    """
    model_config = ConfigDict(extra="forbid")
    meta: Meta
    mode: Mode
    constants: Constants = Field(default_factory=Constants)
    today_scalars: TodayScalars
    condition_inputs: ConditionInputs = Field(default_factory=ConditionInputs)
    stakeholders: Stakeholders = Field(default_factory=Stakeholders)
    iran_regime_dynamics: IranRegimeDynamics = Field(default_factory=IranRegimeDynamics)
    us_dynamics: USDynamics = Field(default_factory=USDynamics)
    iran_deep_dynamics: IranDeepDynamics = Field(default_factory=IranDeepDynamics)
    world_dynamics: WorldDynamics = Field(default_factory=WorldDynamics)
    historical_ideology: HistoricalIdeology = Field(default_factory=HistoricalIdeology)
    exotic_signals: ExoticSignals = Field(default_factory=ExoticSignals)
    historical_analogs: HistoricalAnalogs = Field(default_factory=HistoricalAnalogs)
    new_events: NewEvents = Field(default_factory=NewEvents)
