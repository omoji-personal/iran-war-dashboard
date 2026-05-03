"""Render-pipeline tests — does scripts/render.py produce sane HTML?"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

import pytest

# Make scripts importable
import sys
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import render  # noqa: E402


def test_icd203_full_range():
    # Tail buckets
    assert render.icd203(0.0)[0] == "vanishing"
    assert render.icd203(0.005)[0] == "vanishing"
    # Inside buckets
    assert render.icd203(0.10)[0] == "very unlikely"
    assert render.icd203(0.30)[0] == "unlikely"
    assert render.icd203(0.50)[0] == "roughly even chance"
    assert render.icd203(0.70)[0] == "likely"
    assert render.icd203(0.90)[0] == "very likely"
    assert render.icd203(0.97)[0] == "almost certain"
    # Boundary at 1.0
    assert render.icd203(1.0)[0] == "near certain"


def test_icd203_clamps_out_of_range():
    # Slightly negative or > 1.0 clamps gracefully — never returns "unknown"
    assert render.icd203(-0.05)[0] == "vanishing"
    assert render.icd203(1.05)[0] == "near certain"


def test_first_sentence_truncates_long_text():
    long = "Word. " * 200  # ~1200 chars
    out = render.first_sentence(long)
    # First sentence is "Word." — short
    assert out == "Word."


def test_first_sentence_handles_no_punctuation():
    out = render.first_sentence("just a fragment without ending")
    assert out == "just a fragment without ending"


def test_first_sentence_caps_at_220_chars_no_punct():
    long_no_punct = "x" * 500
    out = render.first_sentence(long_no_punct)
    assert len(out) <= 220
    assert out.endswith("…")


def test_first_sentence_handles_empty():
    assert render.first_sentence("") == ""
    assert render.first_sentence(None) == ""


def test_war_day_arithmetic():
    # D1 is 2026-02-28
    d = datetime(2026, 2, 28, tzinfo=timezone.utc)
    assert render.war_day(d) == 1
    d = datetime(2026, 5, 3, tzinfo=timezone.utc)
    # 2026-02-28 → 2026-05-03 = 64 days later → D65
    assert render.war_day(d) == 65


def test_cf_day_zero_before_ceasefire():
    # Cease-fire start = 2026-04-07. Pre-cease-fire returns 0.
    pre = datetime(2026, 3, 1, tzinfo=timezone.utc)
    assert render.cf_day(pre) == 0
    on = datetime(2026, 4, 7, tzinfo=timezone.utc)
    assert render.cf_day(on) == 1
    later = datetime(2026, 5, 3, tzinfo=timezone.utc)
    assert render.cf_day(later) == 27  # 2026-05-03 minus 2026-04-07 = 26 + 1 = 27


def test_diff_panel_handles_missing_history(tmp_path):
    """When portfolio_history.json doesn't exist, diff returns empty."""
    portfolio = render.load_portfolio()
    diffs = render.compute_diffs_vs_yesterday(portfolio, history=[])
    assert diffs == []


def test_compute_diffs_skips_today_only_history():
    """If history only has TODAY's snapshot, diffs against itself = empty."""
    today_iso = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    portfolio = {
        "questions": [
            {"id": "X1", "current_probability": 0.5, "current_credible_interval_80": [0.4, 0.6]}
        ]
    }
    history = [{"date": today_iso, "questions": [{"id": "X1", "probability": 0.5}]}]
    diffs = render.compute_diffs_vs_yesterday(portfolio, history)
    assert diffs == []


def test_compute_diffs_picks_yesterday_baseline():
    today_iso = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    yesterday_iso = "2025-01-01"  # any earlier date
    portfolio = {
        "questions": [
            {"id": "X1", "question": "test?", "current_probability": 0.50,
             "current_credible_interval_80": [0.45, 0.55]}
        ]
    }
    history = [
        {"date": yesterday_iso, "questions": [{"id": "X1", "probability": 0.30}]},
        {"date": today_iso, "questions": [{"id": "X1", "probability": 0.50}]},  # ignored — same date as today
    ]
    diffs = render.compute_diffs_vs_yesterday(portfolio, history)
    assert len(diffs) == 1
    assert diffs[0]["delta_pp"] == pytest.approx(20.0, abs=0.01)


def test_diff_panel_suppresses_within_ci_noise():
    """A move within the question's CI half-width should NOT appear as a diff."""
    yesterday_iso = "2025-01-01"
    # CI = [0.45, 0.55] → halfwidth 0.05. Move from 0.50 to 0.52 = delta 0.02 < halfwidth.
    portfolio = {
        "questions": [
            {"id": "X1", "question": "test?", "current_probability": 0.52,
             "current_credible_interval_80": [0.45, 0.55]}
        ]
    }
    history = [
        {"date": yesterday_iso, "questions": [{"id": "X1", "probability": 0.50}]},
    ]
    diffs = render.compute_diffs_vs_yesterday(portfolio, history)
    assert diffs == [], "noise within CI should not headline"


def test_render_html_is_well_formed():
    """Renderer must produce valid HTML5 with all 32 question cards (count <article tags)."""
    portfolio = render.load_portfolio()
    html = render.render_html(portfolio, [], history=[], stripped=False)
    assert html.startswith("<!DOCTYPE html>")
    assert html.count('<article class="qcard ') == len(portfolio["questions"])
    # No literal '{' template leftovers
    assert "{{" not in html, "Unfilled template placeholder"


def test_render_public_is_smaller_than_full():
    portfolio = render.load_portfolio()
    full = render.render_html(portfolio, [], history=[], stripped=False)
    pub = render.render_html(portfolio, [], history=[], stripped=True)
    assert len(pub) < len(full), "public.html must drop methodology + logs"


def test_render_html_no_unfilled_placeholders():
    """Catch f-string mistakes that leave literal '{var}' in output."""
    portfolio = render.load_portfolio()
    html = render.render_html(portfolio, [], history=[], stripped=False)
    # Heuristic: no curly-brace pairs in the output (CSS uses curly braces but they're in linked file, not inline)
    # We check for unterminated f-string patterns specifically
    suspicious = ["{q[", "{q.", "{esc(", "{round(", "{label}"]
    for pat in suspicious:
        assert pat not in html, f"Unfilled f-string leak: {pat!r}"
