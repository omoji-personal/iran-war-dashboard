"""Overnight news ingest from ~15 free RSS feeds — Phase 0 briefing input.

Pulls last 24h of items from a curated set of Iran/MidEast feeds (free, no auth),
normalizes them into a flat JSON list, filters by 24h window + relevance, and
deduplicates near-identical headlines across sources.

Output: ``logs/events/{TODAY}.json`` — consumed by the cron LLM in step 6 of
``agent/cron-prompt.phase-0.md`` to write ``agent/briefing-{TODAY}.json``.

This module exposes pure helpers (normalize_entry, filter_by_window,
deduplicate_by_title, is_relevant) for unit testing, plus a ``main()`` that
performs the actual network pull when run as a script.
"""
from __future__ import annotations

import argparse
import calendar
import html
import json
import re
import sys
from datetime import datetime, timedelta, timezone
from difflib import SequenceMatcher
from pathlib import Path
from typing import Iterable

REPO_ROOT = Path(__file__).resolve().parent.parent
EVENTS_DIR = REPO_ROOT / "logs" / "events"

# Initial feed list — free, no auth, public RSS endpoints.
# Order matters for dedup tie-breaking: items from earlier feeds are preferred.
FEEDS: list[tuple[str, str, str]] = [
    ("Reuters Middle East", "https://www.reuters.com/world/middle-east/rss", "en"),
    ("AP World", "https://apnews.com/index.rss", "en"),
    ("Al-Monitor Iran", "https://www.al-monitor.com/feeds/iran-pulse.rss", "en"),
    ("Amwaj Media", "https://amwaj.media/rss", "en"),
    ("Bourse & Bazaar", "https://www.bourseandbazaar.com/articles?format=rss", "en"),
    ("Iran International", "https://www.iranintl.com/en/rss.xml", "en"),
    ("IRNA English", "https://en.irna.ir/rss", "en"),
    ("Tasnim English", "https://www.tasnimnews.com/en/rss/feed/0", "en"),
    ("Tehran Times", "https://www.tehrantimes.com/rss", "en"),
    ("Times of Israel — Iran", "https://www.timesofisrael.com/topic/iran/feed/", "en"),
    ("Long War Journal", "https://www.longwarjournal.org/feed", "en"),
    ("War on the Rocks", "https://warontherocks.com/feed/", "en"),
    ("Crisis Group MENA", "https://www.crisisgroup.org/middle-east-north-africa/rss.xml", "en"),
    ("US State Department", "https://www.state.gov/press-releases/feed/", "en"),
    ("White House Briefing", "https://www.whitehouse.gov/briefing-room/feed/", "en"),
]

# Relevance: include keywords (any match = keep) and exclude keywords
# (any match = drop, overrides include). Lowercased substring match.
_INCLUDE_KEYWORDS = (
    "iran", "tehran", "khamenei", "pezeshkian", "irgc", "revolutionary guard",
    "hormuz", "rial", "araghchi", "nuclear deal", "sanctions", "houthi",
    "hezbollah", "yemen", "natanz", "fordow", "uranium", "centrifuge",
    "tanker", "strait of hormuz", "persian gulf", "trump iran", "us iran",
    "iran us", "iran-us", "us-iran", "shia", "shi'a", "bandar abbas",
    "iraq", "syria", "lebanon", "gaza",
)
_EXCLUDE_KEYWORDS = (
    "olympic", "olympics", "world cup", "fifa", "cricket", "celebrity",
    "best in show", "persian cat", "iphone", "apple ", "movie review",
    "box office", "concert", "fashion week",
)

_HTML_TAG_RE = re.compile(r"<[^>]+>")
_WHITESPACE_RE = re.compile(r"\s+")


def _strip_html(text: str) -> str:
    no_tags = _HTML_TAG_RE.sub(" ", text)
    unescaped = html.unescape(no_tags)
    return _WHITESPACE_RE.sub(" ", unescaped).strip()


def normalize_entry(raw: dict, *, source_name: str, lang: str) -> dict | None:
    """Normalize one feedparser entry into our flat schema.

    Returns None if the entry is missing required fields (title or link).
    """
    title = (raw.get("title") or "").strip()
    link = (raw.get("link") or "").strip()
    if not title or not link:
        return None

    pub_tuple = raw.get("published_parsed") or raw.get("updated_parsed")
    if pub_tuple is not None:
        try:
            epoch = calendar.timegm(pub_tuple)
            published_at = datetime.fromtimestamp(epoch, tz=timezone.utc).isoformat()
        except (TypeError, ValueError, OverflowError):
            published_at = ""
    else:
        published_at = ""

    summary_raw = raw.get("summary") or raw.get("description") or ""
    summary = _strip_html(summary_raw)
    # Cap summary length so the events JSON doesn't balloon.
    if len(summary) > 400:
        summary = summary[:397].rstrip() + "..."

    return {
        "source": source_name,
        "title": title,
        "url": link,
        "published_at": published_at,
        "lang": lang,
        "summary": summary,
    }


def filter_by_window(items: Iterable[dict], *, max_age_hours: int = 24) -> list[dict]:
    """Keep only items whose published_at is within the last ``max_age_hours``.

    Drops items with missing or unparseable published_at.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(hours=max_age_hours)
    out: list[dict] = []
    for item in items:
        ts = item.get("published_at")
        if not ts:
            continue
        try:
            pub = datetime.fromisoformat(ts)
        except (TypeError, ValueError):
            continue
        if pub.tzinfo is None:
            pub = pub.replace(tzinfo=timezone.utc)
        if pub >= cutoff:
            out.append(item)
    return out


def _normalize_title_for_compare(title: str) -> str:
    """Lowercase + strip punctuation + collapse whitespace for similarity compare."""
    t = title.lower()
    t = re.sub(r"[^a-z0-9\s؀-ۿ]", " ", t)  # keep latin + persian
    t = _WHITESPACE_RE.sub(" ", t).strip()
    return t


def deduplicate_by_title(items: list[dict], *, threshold: float = 0.85) -> list[dict]:
    """Collapse near-identical headlines across sources. First-seen wins."""
    kept: list[dict] = []
    kept_norms: list[str] = []
    for item in items:
        norm = _normalize_title_for_compare(item.get("title", ""))
        if not norm:
            kept.append(item)
            kept_norms.append("")
            continue
        is_dup = False
        for existing in kept_norms:
            if not existing:
                continue
            ratio = SequenceMatcher(None, norm, existing).ratio()
            if ratio >= threshold:
                is_dup = True
                break
        if not is_dup:
            kept.append(item)
            kept_norms.append(norm)
    return kept


def is_relevant(title: str) -> bool:
    """Crude include/exclude keyword filter on title.

    True iff title hits any include keyword AND no exclude keyword.
    """
    t = title.lower()
    if any(bad in t for bad in _EXCLUDE_KEYWORDS):
        return False
    return any(good in t for good in _INCLUDE_KEYWORDS)


# --- script entry ---------------------------------------------------------

def _fetch_feed(name: str, url: str, lang: str) -> list[dict]:
    """Network fetch + normalize. Returns [] on any error so one bad feed
    can't kill the whole tick."""
    try:
        import feedparser  # local import: keeps unit tests importable without network
    except ImportError:
        print(f"[fetch_news] feedparser missing — skip {name}", file=sys.stderr)
        return []
    try:
        parsed = feedparser.parse(url)
    except Exception as e:  # noqa: BLE001
        print(f"[fetch_news] {name} parse failed: {e}", file=sys.stderr)
        return []
    out: list[dict] = []
    for entry in parsed.entries:
        norm = normalize_entry(entry, source_name=name, lang=lang)
        if norm is not None:
            out.append(norm)
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Pull last 24h of news from curated RSS feeds.")
    parser.add_argument("--output", type=Path, default=None,
                        help="Output path. Defaults to logs/events/{TODAY}.json.")
    parser.add_argument("--max-age-hours", type=int, default=24)
    parser.add_argument("--no-relevance-filter", action="store_true",
                        help="Skip the keyword relevance filter (debug aid).")
    args = parser.parse_args(argv)

    all_items: list[dict] = []
    for name, url, lang in FEEDS:
        items = _fetch_feed(name, url, lang)
        all_items.extend(items)

    fresh = filter_by_window(all_items, max_age_hours=args.max_age_hours)
    if not args.no_relevance_filter:
        fresh = [i for i in fresh if is_relevant(i.get("title", ""))]
    deduped = deduplicate_by_title(fresh)
    # Sort newest first
    deduped.sort(key=lambda i: i.get("published_at", ""), reverse=True)

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    output_path = args.output or (EVENTS_DIR / f"{today}.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps({
        "tick_date": today,
        "tick_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "max_age_hours": args.max_age_hours,
        "items_count": len(deduped),
        "items": deduped,
    }, indent=2, ensure_ascii=False))
    print(f"[fetch_news] {len(deduped)} items → {output_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
