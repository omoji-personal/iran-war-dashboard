"""Fetch Iran-related Manifold Markets via the public REST API.

No auth required. Appends to today's `logs/sources-shifted/{TODAY}.md`.
Falls back gracefully on network failure.

Usage:
    python3 scripts/fetch_manifold.py
"""
from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LOGS_DIR = REPO_ROOT / "logs" / "sources-shifted"
SNAPSHOT_PATH = REPO_ROOT / "agent" / "manifold-snapshot.json"

API = "https://api.manifold.markets/v0/search-markets"


def safe_fetch(url: str, timeout: int = 15) -> list | None:
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "iran-predictive-agent/0.2"},
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError, TimeoutError) as e:
        print(f"[fetch_manifold] {type(e).__name__}: {e}", file=sys.stderr)
        return None


def fetch_iran_markets(limit: int = 30) -> list[dict]:
    queries = ("iran", "khamenei", "hormuz", "tehran")
    out: list[dict] = []
    seen = set()
    for q in queries:
        url = f"{API}?term={q}&limit={limit}&filter=open&sort=most-popular"
        data = safe_fetch(url)
        if not isinstance(data, list):
            continue
        for m in data:
            mid = m.get("id")
            if mid in seen:
                continue
            seen.add(mid)
            out.append(m)
    return out


def normalize(m: dict) -> dict:
    return {
        "id": m.get("id"),
        "slug": m.get("slug"),
        "question": (m.get("question") or "").strip(),
        "url": m.get("url") or f"https://manifold.markets/{m.get('creatorUsername')}/{m.get('slug')}",
        "probability": round(m.get("probability"), 4) if m.get("probability") is not None else None,
        "volume": m.get("volume"),
        "trader_count": m.get("uniqueBettorCount"),
        "close_time": m.get("closeTime"),
    }


def map_to_portfolio_questions(markets: list[dict]) -> dict[str, dict]:
    rules = [
        ("A1", ("iran nuclear deal", "iran-us deal", "iran agreement")),
        ("B1", ("us strike iran", "us attack iran", "us bomb iran")),
        ("B3", ("israel strike iran", "israel attack iran")),
        ("C1", ("khamenei",)),
        ("C2", ("iran protest", "iran regime fall", "iran revolution")),
        ("D4", ("brent crude 130", "oil 130", "oil 150")),
    ]
    mapping: dict[str, dict] = {}
    for m in markets:
        question = (m.get("question") or "").lower()
        for qid, kws in rules:
            for kw in kws:
                if kw in question:
                    if qid not in mapping or (m.get("uniqueBettorCount") or 0) > (mapping[qid].get("uniqueBettorCount") or 0):
                        mapping[qid] = m
                    break
    return mapping


def load_prior_snapshot() -> dict:
    if not SNAPSHOT_PATH.exists():
        return {}
    try:
        return json.loads(SNAPSHOT_PATH.read_text())
    except json.JSONDecodeError:
        return {}


def save_snapshot(markets: list[dict]) -> None:
    SNAPSHOT_PATH.parent.mkdir(parents=True, exist_ok=True)
    snap = {
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "markets": {str(m["id"]): m for m in markets if m.get("id")},
    }
    SNAPSHOT_PATH.write_text(json.dumps(snap, indent=2))


def append_log(markets: list[dict], mapping: dict[str, dict], prior: dict) -> str:
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    log_path = LOGS_DIR / f"{today}.md"
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    prior_markets = prior.get("markets", {})
    lines = []
    if log_path.exists():
        lines.append("")
    else:
        lines.append(f"# Sources-shifted log — {today}")
        lines.append("")
    lines.append("## Manifold Markets scrape (Phase 0 cron)")
    lines.append("")

    if not markets:
        lines.append("_No Iran-related Manifold markets returned._")
        with log_path.open("a" if log_path.exists() else "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        return str(log_path)

    lines.append(f"Fetched {len(markets)} Iran-related markets at {datetime.now(timezone.utc).strftime('%H:%M UTC')}.")
    lines.append("")

    if mapping:
        lines.append("### Mapped to portfolio questions")
        lines.append("")
        lines.append("| Q | Manifold | Probability | 24h Δ | Traders | Close |")
        lines.append("|---|---|---|---|---|---|")
        for qid, m in sorted(mapping.items()):
            n = normalize(m)
            mid_str = str(n["id"])
            prior_p = (prior_markets.get(mid_str) or {}).get("probability")
            cur_p = n["probability"]
            delta = ""
            if prior_p is not None and cur_p is not None:
                d = (cur_p - prior_p) * 100
                delta = f"{d:+.1f}pp"
            cur_str = f"{cur_p*100:.0f}%" if cur_p is not None else "—"
            close = ""
            if n.get("close_time"):
                try:
                    ct = datetime.fromtimestamp(n["close_time"] / 1000, tz=timezone.utc)
                    close = ct.strftime("%Y-%m-%d")
                except (ValueError, TypeError):
                    close = "—"
            else:
                close = "—"
            q_short = (n.get("question") or "")[:60]
            lines.append(f"| **{qid}** | [{q_short}]({n['url']}) | {cur_str} | {delta} | {n.get('trader_count') or 0} | {close} |")
        lines.append("")

    lines.append("### All Iran-related Manifold markets")
    lines.append("")
    lines.append("| Question | Probability | Vol | Traders |")
    lines.append("|---|---|---|---|")
    for m in sorted(markets, key=lambda x: -(x.get("uniqueBettorCount") or 0))[:20]:
        n = normalize(m)
        cur_str = f"{n['probability']*100:.0f}%" if n.get("probability") is not None else "—"
        vol = f"{n['volume']:,.0f}" if n.get("volume") else "—"
        q_short = (n.get("question") or "")[:80]
        lines.append(f"| [{q_short}]({n['url']}) | {cur_str} | {vol} | {n.get('trader_count') or 0} |")

    with log_path.open("a" if log_path.exists() else "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return str(log_path)


def main() -> int:
    markets = fetch_iran_markets()
    if not markets:
        print("[fetch_manifold] no markets retrieved", file=sys.stderr)
        append_log([], {}, load_prior_snapshot())
        return 0
    print(f"[fetch_manifold] retrieved {len(markets)} markets")
    normalized = [normalize(m) for m in markets]
    prior = load_prior_snapshot()
    mapping = map_to_portfolio_questions(markets)
    log_path = append_log(markets, mapping, prior)
    save_snapshot(normalized)
    print(f"[fetch_manifold] appended to {log_path}")
    print(f"[fetch_manifold] mapped {len(mapping)} questions")
    return 0


if __name__ == "__main__":
    sys.exit(main())
