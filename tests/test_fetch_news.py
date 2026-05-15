"""Tests for scripts/fetch_news.py — RSS-based overnight news ingest.

The module exists to give the cron LLM a structured 24h feed of items from
free RSS sources. These tests exercise the pure functions (parsing, filtering,
deduplication, schema) — no network.
"""
from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import fetch_news  # noqa: E402


# --- helpers --------------------------------------------------------------

def _item(title: str, hours_ago: float = 1.0, **extra) -> dict:
    """Build a normalized news item with a published_at N hours ago (UTC)."""
    pub = datetime.now(timezone.utc) - timedelta(hours=hours_ago)
    base = {
        "source": "TestFeed",
        "title": title,
        "url": f"https://example.test/{title.replace(' ', '-').lower()}",
        "published_at": pub.isoformat(),
        "lang": "en",
        "summary": "",
    }
    base.update(extra)
    return base


# --- filter_by_window -----------------------------------------------------

def test_filter_by_window_keeps_items_inside_24h():
    items = [_item("fresh-1", hours_ago=1), _item("fresh-23", hours_ago=23)]
    out = fetch_news.filter_by_window(items, max_age_hours=24)
    titles = [i["title"] for i in out]
    assert "fresh-1" in titles
    assert "fresh-23" in titles


def test_filter_by_window_drops_items_older_than_24h():
    items = [_item("old", hours_ago=25), _item("fresh", hours_ago=2)]
    out = fetch_news.filter_by_window(items, max_age_hours=24)
    titles = [i["title"] for i in out]
    assert "old" not in titles
    assert "fresh" in titles


def test_filter_by_window_drops_items_with_missing_published_at():
    items = [{"source": "X", "title": "no date", "url": "https://x.test/", "lang": "en", "summary": ""}]
    out = fetch_news.filter_by_window(items, max_age_hours=24)
    assert out == []


def test_filter_by_window_drops_items_with_unparseable_date():
    items = [
        {"source": "X", "title": "bad date", "url": "https://x.test/",
         "published_at": "not-a-date", "lang": "en", "summary": ""}
    ]
    out = fetch_news.filter_by_window(items, max_age_hours=24)
    assert out == []


# --- deduplicate_by_title -------------------------------------------------

def test_deduplicate_by_title_collapses_near_identical_titles():
    items = [
        _item("Iran fires missile at US destroyer in Hormuz"),
        _item("Iran fires missile at US destroyer in Hormuz Strait"),  # +1 word
        _item("Trump suspends Project Freedom"),
    ]
    out = fetch_news.deduplicate_by_title(items)
    assert len(out) == 2


def test_deduplicate_by_title_keeps_distinct_headlines():
    items = [
        _item("Iran fires missile at US destroyer"),
        _item("Trump suspends Project Freedom"),
        _item("Araghchi meets Wang Yi in Beijing"),
    ]
    out = fetch_news.deduplicate_by_title(items)
    assert len(out) == 3


def test_deduplicate_by_title_prefers_first_seen():
    items = [
        _item("Iran fires missile at US destroyer", source="Reuters"),
        _item("Iran fires missile at US destroyer in Hormuz", source="AP"),
    ]
    out = fetch_news.deduplicate_by_title(items)
    assert len(out) == 1
    assert out[0]["source"] == "Reuters"


# --- normalize_entry ------------------------------------------------------

def test_normalize_entry_extracts_required_fields():
    raw = {
        "title": "Test headline",
        "link": "https://example.test/x",
        "published_parsed": (2026, 5, 15, 10, 0, 0, 0, 0, 0),
        "summary": "A short summary.",
    }
    out = fetch_news.normalize_entry(raw, source_name="TestFeed", lang="en")
    assert out["source"] == "TestFeed"
    assert out["title"] == "Test headline"
    assert out["url"] == "https://example.test/x"
    assert out["lang"] == "en"
    assert out["summary"] == "A short summary."
    # published_at parses as ISO8601 UTC
    parsed = datetime.fromisoformat(out["published_at"])
    assert parsed.tzinfo is not None


def test_normalize_entry_returns_none_for_missing_title():
    raw = {"link": "https://example.test/x"}
    assert fetch_news.normalize_entry(raw, source_name="TestFeed", lang="en") is None


def test_normalize_entry_returns_none_for_missing_link():
    raw = {"title": "x"}
    assert fetch_news.normalize_entry(raw, source_name="TestFeed", lang="en") is None


def test_normalize_entry_strips_html_from_summary():
    raw = {
        "title": "T",
        "link": "https://example.test/x",
        "published_parsed": (2026, 5, 15, 10, 0, 0, 0, 0, 0),
        "summary": "<p>Hello <b>world</b></p>",
    }
    out = fetch_news.normalize_entry(raw, source_name="TestFeed", lang="en")
    assert "<" not in out["summary"]
    assert "Hello world" in out["summary"]


# --- relevance filter -----------------------------------------------------

def test_is_relevant_keeps_iran_us_topics():
    assert fetch_news.is_relevant("Iran fires missile in Hormuz")
    assert fetch_news.is_relevant("Tehran rial drops to record low")
    assert fetch_news.is_relevant("Trump Iran sanctions extended")


def test_is_relevant_drops_unrelated_topics():
    assert not fetch_news.is_relevant("Iran wins gold at Olympics")
    assert not fetch_news.is_relevant("Persian cat wins best in show")
    assert not fetch_news.is_relevant("Apple unveils new iPhone")
