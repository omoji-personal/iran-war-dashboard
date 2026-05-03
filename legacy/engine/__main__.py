"""CLI entry: `python -m engine emit | dry-run | lint | migrate`."""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

import yaml

from . import __version__
from .emit import (
    append_history_snapshot,
    assemble,
    write_atomic,
    write_signal_snapshot,
)
from .migrate import migrate as migrate_fn, write_signals_yaml
from .schema import Signals


ROOT = Path(__file__).resolve().parent.parent
SIGNALS_PATH = ROOT / "signals.yaml"
WAR_DATA_PATH = ROOT / "war-data.json"
WAR_DATA_BAK = ROOT / ".war-data.json.bak"
WAR_DATA_PRE_ENGINE_BAK = ROOT / ".war-data.json.pre-engine.bak"
HISTORY_DIR = ROOT / "signals_history"
ENGINE_HISTORY = ROOT / "engine_history.json"


def load_signals(path: Path = SIGNALS_PATH) -> Signals:
    if not path.exists():
        sys.exit(f"signals.yaml not found at {path}. Run `python -m engine migrate` first.")
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    return Signals.model_validate(raw)


def cmd_emit(args) -> int:
    signals = load_signals()
    if not WAR_DATA_PATH.exists():
        sys.exit(f"war-data.json not found at {WAR_DATA_PATH}. Cannot emit without baseline.")
    previous = json.loads(WAR_DATA_PATH.read_text(encoding="utf-8"))
    new_data = assemble(signals, previous)

    # Backup before write
    shutil.copy2(WAR_DATA_PATH, WAR_DATA_BAK)
    write_atomic(WAR_DATA_PATH, new_data)

    # Snapshots
    write_signal_snapshot(HISTORY_DIR, signals)
    append_history_snapshot(ENGINE_HISTORY, signals, new_data)

    print(f"[engine v{__version__}] emitted {WAR_DATA_PATH}")
    print(f"  signal snapshot:  signals_history/{signals.meta.date.isoformat()}.yaml")
    print(f"  engine snapshot:  engine_history.json (calibration spine)")
    return 0


def cmd_dry_run(args) -> int:
    signals = load_signals()
    previous = json.loads(WAR_DATA_PATH.read_text(encoding="utf-8"))
    new_data = assemble(signals, previous)
    # Show high-signal diff: scores, mode, indicators, deep dynamics top-level keys
    de_old = previous.get("decisionEngine", {})
    de_new = new_data.get("decisionEngine", {})

    def fmt(v):
        return f"{v:.2f}" if isinstance(v, float) else str(v)

    print(f"[engine v{__version__}] DRY RUN")
    print(f"  ceasefireMode.enabled  : {previous.get('ceasefireMode', {}).get('enabled')} -> {new_data.get('ceasefireMode', {}).get('enabled')}")
    for k in ("dealAvailability", "usExitPressure", "iranAcceptance", "escalationProximity"):
        old = de_old.get(k, {}).get("score")
        new = de_new.get(k, {}).get("score")
        print(f"  {k:25s}: {fmt(old)} -> {fmt(new)}")
    print(f"  indicators.warDays     : {de_old.get('indicators', {}).get('warDays')} -> {de_new.get('indicators', {}).get('warDays')}")
    dd = new_data.get("deepDynamics", {})
    print(f"  deepDynamics keys      : {sorted(dd.keys())}")
    print(f"  alphaSignals count     : {len(dd.get('alphaSignals', []))}")
    print(f"  exoticTriggers fired   : {sum(1 for v in dd.get('exoticTriggers', {}).values() if v.get('fired'))}/{len(dd.get('exoticTriggers', {}))}")
    print(f"  regime fracture P      : {dd.get('regimeFractureProbability')}")
    print(f"  top historical analog  : {dd.get('historicalAnalogProjection', {}).get('top_analog')}")
    return 0


def cmd_lint(args) -> int:
    signals = load_signals()
    issues = []
    # Mode-flag consistency
    if signals.mode.ceasefire_status == "collapsed" and not signals.condition_inputs.escalation.new_blockade_action:
        issues.append("mode.ceasefire_status=collapsed but escalation.new_blockade_action=False — likely typo")
    # Khamenei religious zeal vs iran_acceptance score
    if (
        signals.stakeholders.khamenei.religious_zeal > 0.85
        and signals.stakeholders.khamenei.public_commitment > 0.85
        and (signals.condition_inputs.iran_acceptance.score_override or 0) > 0.5
    ):
        issues.append("Khamenei religious-zeal lock fired but iran_acceptance.score_override > 0.5 — inconsistent")
    # Day vs date sanity
    from datetime import date
    if signals.meta.day < 1:
        issues.append("meta.day must be >= 1")
    # Print
    if issues:
        print(f"[engine v{__version__}] LINT — {len(issues)} issue(s):")
        for i in issues:
            print(f"  ! {i}")
        return 2
    print(f"[engine v{__version__}] LINT — no issues")
    return 0


def cmd_market_update(args) -> int:
    from .market_fetch import market_update_report
    report = market_update_report()
    print(f"[engine v{__version__}] MARKET UPDATE")
    print(f"  polymarket contracts found: {report['polymarket_contracts_found']}")
    print(f"  metaculus questions found:  {report['metaculus_questions_found']}")
    print(f"  brent spot:                 {report['brent_spot_usd']}")
    print(f"\nSuggested signals.yaml edits (review then paste):")
    for s in report['suggested_signals_yaml_edits']:
        print(s)
    return 0


def cmd_migrate(args) -> int:
    if not WAR_DATA_PATH.exists():
        sys.exit(f"war-data.json not found at {WAR_DATA_PATH}")
    if SIGNALS_PATH.exists() and not args.force:
        sys.exit(f"signals.yaml already exists at {SIGNALS_PATH}. Use --force to overwrite.")
    # Pre-migration backup
    shutil.copy2(WAR_DATA_PATH, WAR_DATA_PRE_ENGINE_BAK)
    signals = migrate_fn(WAR_DATA_PATH, SIGNALS_PATH)
    # Snapshot
    write_signal_snapshot(HISTORY_DIR, signals)
    print(f"[engine v{__version__}] MIGRATE — wrote signals.yaml")
    print(f"  pre-engine backup: {WAR_DATA_PRE_ENGINE_BAK}")
    print(f"  next: edit signals.yaml as needed, then `python -m engine emit`")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(prog="engine", description="iran-war-dashboard engine")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("emit", help="Read signals.yaml, write war-data.json + snapshot")
    sub.add_parser("dry-run", help="Show what emit would change, don't write")
    sub.add_parser("lint", help="Validate signals.yaml + flag inconsistencies")
    mig = sub.add_parser("migrate", help="One-time: seed signals.yaml from current war-data.json")
    mig.add_argument("--force", action="store_true", help="Overwrite existing signals.yaml")
    sub.add_parser("market-update", help="Fetch live market data, print suggested signals.yaml edits")
    args = ap.parse_args()
    return {"emit": cmd_emit, "dry-run": cmd_dry_run, "lint": cmd_lint,
            "migrate": cmd_migrate, "market-update": cmd_market_update}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
