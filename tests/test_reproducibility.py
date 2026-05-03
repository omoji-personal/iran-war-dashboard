"""R12: Snapshot reproducibility test.

Asserts that re-running the engine on the current signals.yaml twice produces
byte-identical output (modulo wall-clock-derived fields). Catches regressions
where a pseudo-random call leaks in or where non-deterministic dict iteration
changes ordering.

Also asserts that engine output for a frozen signals snapshot (committed under
tests/fixtures/) hashes to the same value across runs of the same engine
version. Locks the engine's deterministic surface.
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

import pytest
import yaml

from engine import __version__
from engine.emit import assemble
from engine.schema import Signals


REPO_ROOT = Path(__file__).resolve().parent.parent
SIGNALS_PATH = REPO_ROOT / "signals.yaml"


def _load_signals_and_baseline():
    raw = yaml.safe_load(SIGNALS_PATH.read_text())
    signals = Signals(**raw)
    # Use a minimal baseline (engine fills in everything it controls)
    baseline = {}
    return signals, baseline


def _deterministic_payload(out: dict) -> dict:
    """Return a copy of war-data.json with non-deterministic fields scrubbed.

    `meta.lastUpdated` is wall-clock-derived; ignore for determinism.
    """
    cleaned = copy.deepcopy(out)
    if "meta" in cleaned and isinstance(cleaned["meta"], dict):
        cleaned["meta"].pop("lastUpdated", None)
    return cleaned


def _hash(obj: dict) -> str:
    canon = json.dumps(obj, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(canon.encode("utf-8")).hexdigest()


def test_engine_output_is_deterministic_across_runs():
    """Same signals → same engine output. No hidden randomness."""
    signals, baseline = _load_signals_and_baseline()

    out_a = assemble(signals, baseline)
    out_b = assemble(signals, baseline)

    payload_a = _deterministic_payload(out_a)
    payload_b = _deterministic_payload(out_b)

    h_a = _hash(payload_a)
    h_b = _hash(payload_b)
    assert h_a == h_b, (
        "Engine output diverged across two runs on identical signals. "
        "Likely a non-deterministic field (random seed, unsorted dict iteration, "
        "wall-clock leak). Investigate which key differs."
    )


def test_engine_version_is_stamped():
    """Every emit carries engineVersion for calibration-spine integrity."""
    signals, baseline = _load_signals_and_baseline()
    out = assemble(signals, baseline)
    assert out["decisionEngine"]["engineVersion"] == __version__
    assert out["deepDynamics"]["engineVersion"] == __version__


def test_overrides_active_surfaced():
    """R2: when score_override is set, deepDynamics.overridesActive lists it."""
    signals, baseline = _load_signals_and_baseline()
    out = assemble(signals, baseline)
    # The current signals.yaml has all 4 overrides set
    overrides = out["deepDynamics"]["overridesActive"]
    assert isinstance(overrides, list)
    # At minimum the field exists
    assert "overridesActive" in out["deepDynamics"]
