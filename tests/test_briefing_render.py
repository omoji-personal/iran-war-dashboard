"""Tests for Morning Brief rendering helpers in scripts/render.py."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import render  # noqa: E402


def _briefing(
    *,
    tick_iso: str | None = None,
    movers: list[dict] | None = None,
    events: list[dict] | None = None,
    paragraphs: list[str] | None = None,
    cron_status: str = "ok",
    briefing_partial: bool = False,
) -> dict:
    tick_iso = tick_iso or datetime.now(timezone.utc).isoformat()
    return {
        "tick_date": tick_iso[:10],
        "tick_timestamp_utc": tick_iso,
        "day_number": 77,
        "cron_status": cron_status,
        "events_count_24h": len(events or []),
        "probability_moves_24h": len(movers or []),
        "briefing_partial": briefing_partial,
        "en": {
            "read_paragraphs": paragraphs or ["First para.", "Second para."],
            "movers": movers or [],
            "events": events or [],
        },
        "fa": {
            "read_paragraphs": ["نخستین پاراگراف.", "دومین پاراگراف."],
            "movers": [],
            "events": [],
        },
    }


# --- freshness state ------------------------------------------------------

def test_freshness_state_fresh_when_under_24h():
    b = _briefing(tick_iso=(datetime.now(timezone.utc) - timedelta(hours=2)).isoformat())
    state, hours = render.briefing_freshness_state(b, flag_present=False)
    assert state == "fresh"
    assert 1 <= hours <= 3


def test_freshness_state_aging_between_24h_and_36h():
    b = _briefing(tick_iso=(datetime.now(timezone.utc) - timedelta(hours=30)).isoformat())
    state, hours = render.briefing_freshness_state(b, flag_present=False)
    assert state == "aging"
    assert 29 <= hours <= 31


def test_freshness_state_stale_over_36h():
    b = _briefing(tick_iso=(datetime.now(timezone.utc) - timedelta(hours=40)).isoformat())
    state, hours = render.briefing_freshness_state(b, flag_present=False)
    assert state == "stale"


def test_freshness_state_stale_when_flag_present_even_if_fresh_timestamp():
    b = _briefing(tick_iso=datetime.now(timezone.utc).isoformat())
    state, _ = render.briefing_freshness_state(b, flag_present=True)
    assert state == "stale"


def test_freshness_state_stale_when_briefing_is_none():
    state, hours = render.briefing_freshness_state(None, flag_present=False)
    assert state == "stale"
    assert hours is None


# --- event sanitization ---------------------------------------------------

def test_sanitize_events_drops_items_without_url():
    events = [
        {"headline": "ok", "url": "https://x.test/", "source_name": "S", "public_safe": True},
        {"headline": "no url", "url": "", "source_name": "S", "public_safe": True},
        {"headline": "missing", "source_name": "S", "public_safe": True},
    ]
    out = render.sanitize_events(events, stripped=False)
    assert len(out) == 1
    assert out[0]["headline"] == "ok"


def test_sanitize_events_strips_non_public_safe_when_stripped():
    events = [
        {"headline": "public", "url": "https://x.test/", "source_name": "S", "public_safe": True},
        {"headline": "private", "url": "https://x.test/", "source_name": "S", "public_safe": False},
    ]
    out = render.sanitize_events(events, stripped=True)
    headlines = [e["headline"] for e in out]
    assert "public" in headlines
    assert "private" not in headlines


def test_sanitize_events_keeps_non_public_safe_when_not_stripped():
    events = [
        {"headline": "private", "url": "https://x.test/", "source_name": "S", "public_safe": False},
    ]
    out = render.sanitize_events(events, stripped=False)
    assert len(out) == 1


# --- mover grounding ------------------------------------------------------

def test_ground_movers_keeps_why_when_event_grounded():
    events = [{"headline": "Rial recovered to 1.72M", "url": "https://x.test/", "source_name": "S", "public_safe": True}]
    movers = [{"qid": "F8", "delta_pp": 7, "direction": "down", "old": 48, "new": 41,
               "why": "rial recovered to 1.72M overnight", "citation_url": "https://x.test/", "public_safe": False}]
    out = render.ground_movers(movers, events)
    assert "rial recovered" in out[0]["why"].lower()


def test_ground_movers_replaces_ungrounded_why():
    events = [{"headline": "Trump comment on talks", "url": "https://x.test/", "source_name": "S", "public_safe": True}]
    movers = [{"qid": "F8", "delta_pp": 7, "direction": "down", "old": 48, "new": 41,
               "why": "rial recovered to 1.72M overnight", "citation_url": "https://x.test/", "public_safe": False}]
    out = render.ground_movers(movers, events)
    # Expect the why to be replaced with the fallback string
    assert "no event-grounded" in out[0]["why"].lower() or out[0]["why"] == ""


def test_ground_movers_handles_empty_events_list():
    movers = [{"qid": "F8", "delta_pp": 7, "direction": "down", "old": 48, "new": 41,
               "why": "anything", "citation_url": "https://x.test/", "public_safe": False}]
    out = render.ground_movers(movers, [])
    assert "no event-grounded" in out[0]["why"].lower()


def test_ground_movers_strips_private_movers_when_stripped():
    """F-question movers should not survive into the public variant even if grounded."""
    events = [{"headline": "rial", "url": "https://x.test/", "source_name": "S", "public_safe": True}]
    movers = [
        {"qid": "F8", "delta_pp": 7, "direction": "down", "old": 48, "new": 41,
         "why": "rial recovered", "citation_url": "https://x.test/", "public_safe": False},
        {"qid": "B1", "delta_pp": 3, "direction": "up", "old": 15, "new": 18,
         "why": "rial recovered", "citation_url": "https://x.test/", "public_safe": True},
    ]
    public = render.ground_movers(movers, events, stripped=True)
    qids = [m["qid"] for m in public]
    assert "F8" not in qids
    assert "B1" in qids


# --- render_morning_brief composition -------------------------------------

def test_render_morning_brief_emits_four_panels_when_fresh():
    b = _briefing(
        movers=[{"qid": "F8", "delta_pp": 7, "direction": "down", "old": 48, "new": 41,
                 "why": "rial recovered overnight", "citation_url": "https://x.test/", "public_safe": False}],
        events=[
            {"headline": "Rial recovered overnight to 1.72M", "url": "https://x.test/", "source_name": "Bourse",
             "published_at": "2026-05-15T03:12:00Z", "public_safe": True},
            {"headline": "Araghchi meets Wang Yi in Beijing", "url": "https://y.test/", "source_name": "Tasnim",
             "published_at": "2026-05-15T04:00:00Z", "public_safe": True},
            {"headline": "IRGC fires missile near US destroyer", "url": "https://z.test/", "source_name": "Reuters",
             "published_at": "2026-05-15T05:00:00Z", "public_safe": True},
        ],
    )
    html = render.render_morning_brief(b, stripped=False, lang="en", flag_present=False)
    assert "morning-brief" in html
    assert "brief-strip" in html
    assert "brief-read" in html
    assert "brief-movers" in html
    assert "brief-events" in html
    # Banner state classes
    assert "brief-strip-fresh" in html


def test_render_morning_brief_uses_stale_state_when_flag_present():
    b = _briefing()
    html = render.render_morning_brief(b, stripped=False, lang="en", flag_present=True)
    assert "brief-strip-stale" in html


def test_render_morning_brief_empty_movers_renders_quiet_message():
    b = _briefing(movers=[], events=[
        {"headline": "h1", "url": "https://x.test/", "source_name": "S", "public_safe": True},
        {"headline": "h2", "url": "https://y.test/", "source_name": "S", "public_safe": True},
        {"headline": "h3", "url": "https://z.test/", "source_name": "S", "public_safe": True},
    ])
    html = render.render_morning_brief(b, stripped=False, lang="en", flag_present=False)
    assert "no probability moves" in html.lower() or "quiet" in html.lower() or "brief-movers-empty" in html.lower()


def test_render_morning_brief_renders_no_verified_events_when_fewer_than_three():
    b = _briefing(events=[
        {"headline": "only one", "url": "https://x.test/", "source_name": "S", "public_safe": True},
    ])
    html = render.render_morning_brief(b, stripped=False, lang="en", flag_present=False)
    assert "no verified overnight events" in html.lower() or "brief-events-empty" in html.lower()


def test_render_morning_brief_persian_uses_fa_block():
    b = _briefing()
    b["fa"]["read_paragraphs"] = ["متن فارسی برای آزمون.", "پاراگراف دو."]
    html = render.render_morning_brief(b, stripped=False, lang="fa", flag_present=False)
    assert "متن فارسی برای آزمون" in html


def test_render_morning_brief_falls_back_to_stale_state_when_briefing_none():
    html = render.render_morning_brief(None, stripped=False, lang="en", flag_present=False)
    assert "brief-strip-stale" in html


def test_render_morning_brief_strips_private_content_in_public_variant():
    b = _briefing(
        movers=[
            {"qid": "F8", "delta_pp": 7, "direction": "down", "old": 48, "new": 41,
             "why": "rial recovered", "citation_url": "https://x.test/", "public_safe": False},
        ],
        events=[
            {"headline": "rial recovered", "url": "https://x.test/", "source_name": "S", "public_safe": True},
            {"headline": "private-only", "url": "https://y.test/", "source_name": "S", "public_safe": False},
            {"headline": "another public", "url": "https://z.test/", "source_name": "S", "public_safe": True},
            {"headline": "third public", "url": "https://a.test/", "source_name": "S", "public_safe": True},
        ],
    )
    html = render.render_morning_brief(b, stripped=True, lang="en", flag_present=False)
    assert "F8" not in html
    assert "private-only" not in html


def test_render_morning_brief_wraps_movers_and_events_in_right_column():
    """Movers + events must share a single .brief-right-col wrapper so the
    wide-viewport grid can place them on the right while the read fills the
    left. The wrapper sits AFTER the read in source order so narrow screens
    still flow read → movers → events."""
    b = _briefing(events=[
        {"headline": f"h{i}", "url": f"https://x.test/{i}", "source_name": "S", "public_safe": True}
        for i in range(5)
    ])
    html = render.render_morning_brief(b, stripped=False, lang="en", flag_present=False)
    assert "brief-right-col" in html, "right-column wrapper missing"
    # Order: read must precede right-col, right-col must contain both movers + events
    read_idx = html.index("brief-read")
    right_idx = html.index("brief-right-col")
    movers_idx = html.index("brief-movers")
    events_idx = html.index("brief-events")
    assert read_idx < right_idx, "read must precede right-col in source order"
    assert right_idx < movers_idx < events_idx, "movers + events must live inside right-col"


def test_render_morning_brief_shows_partial_notice_when_flagged():
    b = _briefing(briefing_partial=True, events=[
        {"headline": f"h{i}", "url": f"https://x.test/{i}", "source_name": "S", "public_safe": True}
        for i in range(5)
    ])
    html = render.render_morning_brief(b, stripped=False, lang="en", flag_present=False)
    assert "partial" in html.lower() or "truncated" in html.lower()
