"""One-time migration: build a seed signals.yaml from the current war-data.json.

This reverse-engineers the daily-edit file from whatever the user has been
hand-typing into war-data.json + meta.notes[0]. Output is a starting point —
the user can edit before re-emitting.
"""
from __future__ import annotations

import json
import re
from datetime import date, datetime
from pathlib import Path
from typing import Any

import yaml

from .schema import (
    ConditionInputs,
    Constants,
    DealInputs,
    EscalationInputs,
    ExoticSignals,
    HistoricalAnalogs,
    HistoricalIdeology,
    IranAcceptanceInputs,
    IranDeepDynamics,
    IranRegimeDynamics,
    Meta,
    Mode,
    NewEvents,
    Signals,
    Stakeholders,
    TodayScalars,
    USDynamics,
    UsExitInputs,
)


def _extract_int(text: str, pattern: str, default: int = 0) -> int:
    m = re.search(pattern, text)
    if m:
        try:
            return int(m.group(1).replace(",", ""))
        except ValueError:
            return default
    return default


def _extract_float(text: str, pattern: str, default: float = 0.0) -> float:
    m = re.search(pattern, text)
    if m:
        try:
            return float(m.group(1).replace(",", ""))
        except ValueError:
            return default
    return default


def build_signals_from_json(data: dict[str, Any]) -> Signals:
    """Reverse-engineer Signals from existing war-data.json."""
    notes = (data.get("meta", {}).get("notes") or [""])
    today_note = notes[0] if notes else ""

    # ---- meta ----
    last_updated_iso = data.get("meta", {}).get("lastUpdated", datetime.now().isoformat())
    parsed = datetime.fromisoformat(last_updated_iso.replace("Z", "+00:00"))
    today_date = parsed.date()

    # War day from note prefix "D63 (..."
    day_match = re.match(r"D(\d+)", today_note)
    war_day = int(day_match.group(1)) if day_match else 1

    # Ceasefire day from note "cfDay24" pattern
    cf_day_match = re.search(r"cfDay(\d+)", today_note)
    cf_day = int(cf_day_match.group(1)) if cf_day_match else None

    # ---- mode ----
    cf_enabled = data.get("ceasefireMode", {}).get("enabled", False)
    if cf_enabled:
        # Detect hollow vs active vs extended_indef from notes
        if "extended" in today_note.lower() and "indef" in today_note.lower():
            cf_status = "extended_indef"
        elif any(k in today_note.lower() for k in ("blockade", "seizure", "fired on")):
            cf_status = "hollow"
        else:
            cf_status = "active"
    else:
        cf_status = "collapsed" if war_day > 53 else "none"

    # ---- today_scalars (extract from note prose) ----
    brent = _extract_float(today_note, r"Brent\D{0,4}\$?(\d+(?:\.\d+)?)")
    brent_high = _extract_float(today_note, r"intraday[^$]*\$(\d+(?:\.\d+)?)")
    wti = _extract_float(today_note, r"WTI\D{0,4}\$?(\d+(?:\.\d+)?)")
    gas = _extract_float(today_note, r"gas \$(\d+\.\d+)") or _extract_float(today_note, r"\$(\d+\.\d+)/gal")
    hormuz = _extract_int(today_note, r"Hormuz[^\d]{0,30}(\d+)\s*vessels")
    rial = _extract_int(today_note, r"rial[^\d]{0,20}(\d[\d.,]+)M") * 1_000_000 if "rial" in today_note.lower() else None
    streak = _extract_int(today_note, r"(\d+)-day zero-attack streak", default=0)
    internet_hours = _extract_int(today_note, r"Internet[^=]*=\s*(\d[,\d]*)\+?\s*hrs")
    ships_stranded = _extract_int(today_note, r"~?(\d[,\d]*)\s*ships stranded")
    lebanon = _extract_int(today_note, r"Lebanon[^\d]*(\d[,\d]+)\+?\s*killed")

    # Pull from indicators where note doesn't have it
    ind = data.get("decisionEngine", {}).get("indicators", {})
    us_kia = ind.get("usKIA", 15)
    us_wounded = ind.get("usWounded", 520)
    us_aircraft = ind.get("usAircraftLost", 7)
    iran_civ = ind.get("iranCivKilled_HRANA", 3540)

    today_scalars = TodayScalars(
        brent=brent or 100.0,
        brent_intraday_high=brent_high or None,
        wti=wti or None,
        gas_price=gas or 4.10,
        hormuz_vessels=hormuz or 7,
        rial_per_usd=rial,
        zero_attack_streak_days=streak,
        internet_blackout_hours=internet_hours or None,
        ships_stranded=ships_stranded or None,
        us_kia=us_kia,
        us_wounded=us_wounded,
        us_aircraft_lost=us_aircraft,
        lebanon_killed=lebanon or 0,
        iran_civ_killed_hrana=iran_civ,
        coalition_cohesion_score=ind.get("coalitionCohesionScore", 2.5),
    )

    # ---- condition_inputs (preserved from existing scores via overrides) ----
    de = data.get("decisionEngine", {})
    condition_inputs = ConditionInputs(
        deal=DealInputs(
            iran_proposal_active=False,
            us_acceptance_signal=0.2,
            nuclear_gap_pp=15,
            score_override=de.get("dealAvailability", {}).get("score"),
        ),
        us_exit=UsExitInputs(
            gas_pain_above_threshold=(today_scalars.gas_price > 4.20),
            war_powers_passed=True,
            centcom_strike_plan_briefed=True,
            score_override=de.get("usExitPressure", {}).get("score"),
        ),
        iran_acceptance=IranAcceptanceInputs(
            khamenei_public_vow_against=True,
            irgc_in_charge=True,
            formal_proposals_rejected=3,
            score_override=de.get("iranAcceptance", {}).get("score"),
        ),
        escalation=EscalationInputs(
            centcom_briefed=True,
            hezbollah_action_recent=True,
            new_blockade_action=True,
            score_override=de.get("escalationProximity", {}).get("score"),
        ),
    )

    # ---- new_events: leave empty (today's data is already in war-data.json) ----
    new_events = NewEvents()

    # ---- assemble ----
    return Signals(
        meta=Meta(day=war_day, cf_day=cf_day, date=today_date, notes=[today_note] if today_note else []),
        mode=Mode(ceasefire_status=cf_status),
        constants=Constants(),
        today_scalars=today_scalars,
        condition_inputs=condition_inputs,
        stakeholders=Stakeholders(),
        iran_regime_dynamics=IranRegimeDynamics(),
        us_dynamics=USDynamics(
            gas_price_pain_index=min(1.0, max(0.0, (today_scalars.gas_price - 3.0) / 2.0)),
        ),
        iran_deep_dynamics=IranDeepDynamics(),
        world_dynamics=__import__("engine.schema", fromlist=["WorldDynamics"]).WorldDynamics(),
        historical_ideology=HistoricalIdeology(),
        exotic_signals=ExoticSignals(),
        historical_analogs=HistoricalAnalogs(),
        new_events=new_events,
    )


def write_signals_yaml(signals: Signals, path: Path) -> None:
    data = signals.model_dump(mode="json")
    path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")


def migrate(war_data_path: Path, signals_yaml_path: Path) -> Signals:
    data = json.loads(war_data_path.read_text(encoding="utf-8"))
    signals = build_signals_from_json(data)
    write_signals_yaml(signals, signals_yaml_path)
    return signals
