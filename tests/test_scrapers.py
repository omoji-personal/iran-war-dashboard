"""Smoke + behavior tests for the three market-feed scrapers.

These tests don't hit the network — they exercise the pure functions.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import fetch_polymarket  # noqa: E402
import fetch_manifold  # noqa: E402


def test_polymarket_excludes_fifa_world_cup():
    """The Polymarket 'iran' tag includes World Cup matches because Iran is a national team.
    Local filter must exclude them."""
    fifa_market = {"slug": "will-iran-win-the-2026-fifa-world-cup-788", "question": "Will Iran win the 2026 FIFA World Cup?"}
    deal_market = {"slug": "us-iran-nuclear-deal-before-2027", "question": "US-Iran nuclear deal before 2027"}
    assert not fetch_polymarket._is_relevant(fifa_market)
    assert fetch_polymarket._is_relevant(deal_market)


def test_polymarket_excludes_oscar_celebrity():
    olympic = {"slug": "iran-olympic-medal-2026", "question": "Iran win gold at 2026 Olympics?"}
    celeb = {"slug": "celebrity-iran-something", "question": "Celebrity Iran appearance"}
    assert not fetch_polymarket._is_relevant(olympic)
    assert not fetch_polymarket._is_relevant(celeb)


def test_polymarket_to_float_handles_string_values():
    assert fetch_polymarket._to_float("1234.56") == 1234.56
    assert fetch_polymarket._to_float(1234) == 1234.0
    assert fetch_polymarket._to_float(None) is None
    assert fetch_polymarket._to_float("not-a-number") is None


def test_polymarket_normalize_handles_string_outcomePrices():
    """Polymarket sometimes returns outcomePrices as a JSON-encoded string."""
    m = {
        "slug": "test-market",
        "question": "Test?",
        "outcomePrices": '["0.42", "0.58"]',
        "volume24hr": "1000",
        "liquidity": "5000",
        "endDate": "2026-12-31",
    }
    n = fetch_polymarket.normalize_market(m)
    assert n["price_yes"] == 0.42
    assert n["volume_24h"] == 1000.0
    assert n["liquidity"] == 5000.0


def test_polymarket_normalize_handles_missing_fields():
    m = {"slug": "x", "question": "?"}
    n = fetch_polymarket.normalize_market(m)
    assert n["price_yes"] is None
    assert n["volume_24h"] is None


def test_polymarket_map_to_portfolio():
    """Keyword mapping should pick A1 for nuclear-deal markets."""
    markets = [
        {"slug": "us-iran-nuclear-deal-before-2027", "question": "US-Iran nuclear deal before 2027", "liquidity": 100000},
        {"slug": "us-strike-iran-by-jul-1", "question": "US strikes Iran by Jul 1", "liquidity": 50000},
    ]
    mapping = fetch_polymarket.map_to_portfolio_questions(markets)
    assert "A1" in mapping
    assert "B1" in mapping


def test_manifold_normalize():
    m = {
        "id": "abc123",
        "slug": "iran-deal",
        "question": "US-Iran deal?",
        "url": "https://manifold.markets/x/iran-deal",
        "probability": 0.42,
        "volume": 5000,
        "uniqueBettorCount": 50,
    }
    n = fetch_manifold.normalize(m)
    assert n["probability"] == 0.42
    assert n["trader_count"] == 50


def test_manifold_map_to_portfolio():
    markets = [
        {"id": "1", "question": "iran nuclear deal by 2026?", "uniqueBettorCount": 100},
        {"id": "2", "question": "khamenei alive on Jan 1, 2027?", "uniqueBettorCount": 60},
    ]
    mapping = fetch_manifold.map_to_portfolio_questions(markets)
    assert "A1" in mapping
    assert "C1" in mapping
