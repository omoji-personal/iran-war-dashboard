"""Schema + structural tests for portfolio.yaml + reference_classes.yaml + lr_table.yaml.

Phase 0 MVP test surface — replaces the deprecated engine/ tests."""
from __future__ import annotations

from pathlib import Path

import pytest
import yaml


REPO_ROOT = Path(__file__).resolve().parent.parent
PORTFOLIO = REPO_ROOT / "portfolio.yaml"
REF_CLASSES = REPO_ROOT / "reference_classes.yaml"
LR_TABLE = REPO_ROOT / "lr_table.yaml"


@pytest.fixture(scope="module")
def portfolio():
    return yaml.safe_load(PORTFOLIO.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def reference_classes():
    return yaml.safe_load(REF_CLASSES.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def lr_table():
    return yaml.safe_load(LR_TABLE.read_text(encoding="utf-8"))


def test_portfolio_has_questions_list(portfolio):
    assert "questions" in portfolio
    assert isinstance(portfolio["questions"], list)
    assert len(portfolio["questions"]) >= 20, "Phase 0 MVP expects at least 20 questions"


def test_portfolio_metadata_present(portfolio):
    md = portfolio.get("metadata", {})
    assert md.get("engine_version"), "metadata.engine_version required"
    assert md.get("spec_version"), "metadata.spec_version required"


def test_every_question_has_required_fields(portfolio):
    required = {
        "id", "category", "question", "resolution_criterion", "deadline",
        "baseline_class", "expiration_policy", "stakeholder_tags",
        "current_probability", "current_credible_interval_80",
        "current_icd203_label", "last_updated",
        # Reference classes are part of the schema even when set to null
        # (the contract is "the field is present, populated or explicitly null").
        "reference_class_strict", "reference_class_broad",
    }
    for q in portfolio["questions"]:
        missing = required - set(q.keys())
        assert not missing, f"Question {q.get('id')} missing fields: {missing}"


def test_probabilities_are_in_range(portfolio):
    for q in portfolio["questions"]:
        p = q["current_probability"]
        assert 0.0 <= p <= 1.0, f"{q['id']}: probability {p} out of [0,1]"


def test_credible_intervals_are_sane(portfolio):
    for q in portfolio["questions"]:
        ci = q["current_credible_interval_80"]
        assert isinstance(ci, list) and len(ci) == 2, f"{q['id']}: CI must be [lo, hi]"
        lo, hi = ci
        assert 0.0 <= lo <= hi <= 1.0, f"{q['id']}: CI [{lo}, {hi}] inverted or out of range"
        p = q["current_probability"]
        assert lo <= p <= hi, f"{q['id']}: point estimate {p} not within CI [{lo}, {hi}]"


def test_question_ids_are_unique(portfolio):
    ids = [q["id"] for q in portfolio["questions"]]
    assert len(ids) == len(set(ids)), f"Duplicate IDs: {[i for i in ids if ids.count(i) > 1]}"


def test_categories_are_known(portfolio):
    known = {
        "diplomatic_resolution", "military_escalation", "regime_leadership",
        "economic_structural", "us_side",
        "family_business_iranfarhang", "family_business_kipa",
    }
    for q in portfolio["questions"]:
        assert q["category"] in known, f"{q['id']}: unknown category {q['category']}"


def test_baseline_class_is_known(portfolio):
    known = {
        "ar", "ar_plus_reference_class", "ar_plus_oil_export_model",
        "polymarket_or_broad_reference_class", "reference_class",
        "actuarial_plus_reference_class", "ar_plus_explicit_subjective",
        "explicit_subjective", "oil_options_implied_plus_ar",
        "538_plus_polymarket",
    }
    for q in portfolio["questions"]:
        bc = q["baseline_class"]
        assert bc in known, f"{q['id']}: unknown baseline_class {bc}"


def test_humility_flagged_questions_have_notes(portfolio):
    for q in portfolio["questions"]:
        if q.get("humility_flag"):
            assert q.get("humility_note"), f"{q['id']}: humility-flagged question must explain why"


def test_lr_table_every_lr_is_sourced(lr_table):
    """Audit R1: every LR carries source class — historical-analog,
    market-implied, or explicitly-subjective with replacement criteria."""
    valid_classes = {"historical_analog", "market_implied", "explicitly_subjective"}
    for lr in lr_table["likelihood_ratios"]:
        sc = lr.get("source_class")
        assert sc in valid_classes, f"{lr.get('id')}: invalid source_class {sc}"
        if sc == "explicitly_subjective":
            assert lr.get("replacement_criteria"), (
                f"{lr.get('id')}: explicitly_subjective LR requires replacement_criteria"
            )
        assert lr.get("source_calc"), f"{lr.get('id')}: source_calc required"


def test_lr_table_metadata_no_unmarked_subjective(lr_table):
    md = lr_table.get("metadata", {})
    assert md.get("unmarked_subjective_count") == 0, (
        "Unmarked subjective LRs must be 0 — every LR must declare its source class"
    )


def test_reference_classes_have_inclusion_criteria(reference_classes):
    """Reference classes must specify what's in the class."""
    for class_id, body in reference_classes.items():
        if class_id == "metadata":
            continue
        assert isinstance(body, dict), f"{class_id}: body must be dict"
        assert body.get("inclusion_criteria"), f"{class_id}: missing inclusion_criteria"


def test_portfolio_reference_classes_resolve(portfolio, reference_classes):
    """Every non-null reference_class_strict / reference_class_broad named in
    portfolio.yaml MUST exist as a key in reference_classes.yaml. Without this
    test, a typo or rename leaves an orphan reference and tests still pass."""
    valid = {k for k in reference_classes.keys() if k != "metadata"}
    for q in portfolio["questions"]:
        for field in ("reference_class_strict", "reference_class_broad"):
            ref = q.get(field)
            if ref is None:
                continue
            assert ref in valid, (
                f"{q['id']}: {field}={ref!r} does not exist in reference_classes.yaml"
            )


def test_reference_classes_metadata_count_matches(reference_classes):
    """metadata.total_classes must match the number of non-metadata top-level keys."""
    actual = len([k for k in reference_classes.keys() if k != "metadata"])
    declared = reference_classes.get("metadata", {}).get("total_classes")
    assert declared == actual, (
        f"reference_classes.yaml metadata.total_classes={declared} but file has {actual} classes"
    )


def test_lr_table_lr_directionality_consistent_with_notes(lr_table):
    """If an LR's question_relevance value is explicitly described in the
    source_calc as 'evidence against' the question hypothesis, the LR must
    be < 1; if 'evidence for', LR > 1. Catches the sign errors gemini found."""
    for lr in lr_table["likelihood_ratios"]:
        calc = (lr.get("source_calc") or "").lower()
        for qid, val in (lr.get("question_relevance") or {}).items():
            if val is None:
                continue
            # Only evaluate the assertion for LR rows that explicitly mention
            # the question id in the calc text (otherwise we'd over-constrain).
            if qid.lower() not in calc:
                continue
            against_phrases = ("argues against", "evidence against", "evidence ag.")
            for_phrases = ("argues for", "evidence for ", "evidence for\n")
            if any(p in calc for p in against_phrases):
                assert val < 1.0, f"{lr['id']}/{qid}: source_calc says 'against' but LR={val} >= 1"
            if any(p in calc for p in for_phrases):
                assert val > 1.0, f"{lr['id']}/{qid}: source_calc says 'for' but LR={val} <= 1"


def test_portfolio_yaml_parses_without_warnings(portfolio):
    """Smoke test — yaml.safe_load already validated structure; no specific check beyond load."""
    assert portfolio is not None


def test_deadline_format_is_iso(portfolio):
    """Deadlines must be ISO YYYY-MM-DD parseable."""
    from datetime import datetime
    for q in portfolio["questions"]:
        d = q["deadline"]
        # YAML may have parsed as date or string
        if hasattr(d, "isoformat"):
            d = d.isoformat()
        try:
            datetime.fromisoformat(str(d))
        except ValueError:
            pytest.fail(f"{q['id']}: invalid deadline {d!r}")


def test_stakeholder_tags_are_known(portfolio):
    """Stakeholder tags must come from the published stakeholder-class registry."""
    known_tags = {
        "us_foreign_policy", "iran_regime_survival", "oil_energy_markets",
        "regional_security", "omid_personal",
        "iranfarhang_business", "kipa_business",
    }
    for q in portfolio["questions"]:
        for tag in q.get("stakeholder_tags", []):
            assert tag in known_tags, f"{q['id']}: unknown stakeholder tag {tag!r}"
