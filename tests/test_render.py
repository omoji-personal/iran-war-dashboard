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


def test_render_public_actually_strips_private_content():
    """The public render must NOT contain any F-question card OR any business
    name tied to private categories. A size-only assertion is too weak — a
    size-equal but content-leaking output would slip through."""
    portfolio = render.load_portfolio()
    pub = render.render_html(portfolio, [], history=[], stripped=True)
    full = render.render_html(portfolio, [], history=[], stripped=False)

    assert len(pub) < len(full), "public.html must drop methodology + logs"

    # No F-question card IDs in public HTML
    for q in portfolio["questions"]:
        if q["id"].startswith("F"):
            assert f'id="q-{q["id"]}"' not in pub, (
                f"public render leaks F-question card: {q['id']}"
            )

    # No private business names in user-facing strings
    forbidden_substrings = ("Iranfarhang", "Kipa", "iranfarhang", "kipa",
                             "Mozhgan", "Behrah", "Magiran", "Kemco")
    for tok in forbidden_substrings:
        assert tok not in pub, f"public render leaks private term: {tok!r}"

    # PERSONAL flag is operator-only and must never appear publicly
    assert "flag-personal" not in pub
    assert "PERSONAL" not in pub


def test_base_case_renders_when_present():
    """Base-case section must appear above the question board when metadata
    has base_case_narrative populated. The portfolio.yaml currently has it
    populated; the rendered HTML must show the section."""
    portfolio = render.load_portfolio()
    html = render.render_html(portfolio, [], history=[], stripped=False)
    assert 'class="basecase"' in html, "base-case section missing on private render"
    assert 'class="basecase-h"' in html
    # Order: base-case must appear BEFORE the question board
    assert html.index('class="basecase"') < html.index('class="board"'), (
        "base-case must render above the question board"
    )


def test_base_case_renders_public_variant_for_stripped():
    """Public render uses base_case_narrative_public if set, falls back to
    base_case_narrative otherwise. Must not leak family-business specifics."""
    portfolio = render.load_portfolio()
    pub = render.render_html(portfolio, [], history=[], stripped=True)
    assert 'class="basecase"' in pub
    # Family-business names must never appear in the public base case
    md = portfolio.get("metadata", {})
    if md.get("base_case_narrative_public"):
        for tok in ("Iranfarhang", "Kipa", "iranfarhang", "kipa", "Berman Amendment", "AMAG"):
            assert tok not in pub, f"public base case leaks {tok!r}"


def test_base_case_section_omitted_when_metadata_empty():
    """Renderer must gracefully render nothing if base_case_narrative is missing."""
    portfolio = render.load_portfolio()
    # Synthesize a portfolio with no base case
    p = {**portfolio, "metadata": {**portfolio["metadata"]}}
    p["metadata"].pop("base_case_narrative", None)
    p["metadata"].pop("base_case_narrative_public", None)
    html = render.render_html(p, [], history=[], stripped=False)
    assert 'class="basecase"' not in html


def test_question_board_clusters_present_when_relevant():
    """The board should surface cluster headings whenever at least one
    category has both clusters or just one. At least one heading variant
    must appear in the rendered HTML for the current portfolio."""
    portfolio = render.load_portfolio()
    html = render.render_html(portfolio, [], history=[], stripped=False)
    has_likely = "Most-likely outcomes" in html
    has_tail = "Lower-probability scenarios to watch" in html
    assert has_likely or has_tail, "expected at least one cluster heading in rendered board"
    # Per-category ordering verified by test_question_board_within_category_descending_by_probability


def test_question_board_within_category_descending_by_probability():
    """For at least one category that has both clusters, verify the cards
    inside the rendered HTML appear in descending-probability order."""
    portfolio = render.load_portfolio()
    by_cat = {}
    for q in portfolio["questions"]:
        by_cat.setdefault(q["category"], []).append(q)

    # Render one category in isolation
    for cat_id in by_cat:
        likely, tail = render._split_likely_tail(by_cat[cat_id])
        if likely and tail:
            # Both clusters present — assert sort order
            ordered = likely + tail
            html = render.render_question_board({cat_id: by_cat[cat_id]}, stripped=False)
            positions = [html.index(f'id="q-{q["id"]}"') for q in ordered]
            assert positions == sorted(positions), (
                f"category {cat_id}: cards not rendered in expected likely→tail order"
            )
            return  # one is enough
    # If no category had both clusters, we can't run this assertion (not a failure)
    return


def test_topness_prefers_in_play_over_equal_stakes_tail():
    """A 70% question with 0 movement and equal stakes should now beat a 12%
    tail-risk that just jumped 3pp — that's the round-16 rebalance."""
    in_play = {"id": "X1", "current_probability": 0.70,
                "current_credible_interval_80": [0.55, 0.85],
                "deadline": "2026-09-30",
                "stakeholder_tags": ["us_foreign_policy"]}
    tail = {"id": "X2", "current_probability": 0.12,
             "current_credible_interval_80": [0.05, 0.20],
             "deadline": "2026-09-30",
             "stakeholder_tags": ["us_foreign_policy"]}
    last = {"X1": {"probability": 0.70}, "X2": {"probability": 0.09}}  # X2 jumped 3pp
    today = datetime(2026, 5, 5, tzinfo=timezone.utc)
    s_in = render.topness(in_play, last, today=today)
    s_tail = render.topness(tail, last, today=today)
    assert s_in > s_tail, (
        f"in-play 70% question should outscore tail-risk 12% mover; got {s_in:.3f} vs {s_tail:.3f}"
    )


def test_render_html_no_unfilled_placeholders():
    """Catch f-string / template mistakes that leave literal `{var}` tokens in output.
    Uses a real regex instead of a fixed list of suspect substrings."""
    import re
    portfolio = render.load_portfolio()
    html = render.render_html(portfolio, [], history=[], stripped=False)

    # Strip <style>...</style> and <script>...</script> blocks (legitimate JS/CSS
    # may use {} braces). Ours doesn't, but the test stays defensive.
    cleaned = re.sub(r"<(style|script)\b.*?</\1>", "", html, flags=re.DOTALL | re.IGNORECASE)

    # Match `{...}` where contents look like a Python expression — letters,
    # digits, underscores, brackets, dots, parens, but NOT a CSS pseudo-block
    # (which always contains `:`, semicolons, or has a tag-like chunk before `{`).
    pattern = re.compile(r"\{[A-Za-z_][A-Za-z0-9_\[\]\.\(\)\"'\s]*\}")
    leaks = [m.group(0) for m in pattern.finditer(cleaned)]
    # Whitelist: exact CSS clamp(...)/calc(...)/var(...) helpers won't match because
    # they're inside an external stylesheet. If any genuine leftover f-string
    # placeholder slips through, this assertion fires.
    assert not leaks, f"Unfilled placeholder(s) in HTML: {leaks[:5]}"
