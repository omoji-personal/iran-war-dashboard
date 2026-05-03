"""Fetch Iran-related Polymarket contracts via the public Gamma API.

No auth required. Updates `logs/sources-shifted/{TODAY}.md` with current
prices + deltas vs prior tick. Falls back gracefully on network failure.

Usage:
    python3 scripts/fetch_polymarket.py
"""
from __future__ import annotations

import json
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LOGS_DIR = REPO_ROOT / "logs" / "sources-shifted"
SNAPSHOT_PATH = REPO_ROOT / "agent" / "polymarket-snapshot.json"

GAMMA = "https://gamma-api.polymarket.com/markets"


# Untrusted market-title/slug payloads are written into Markdown logs that the
# cron-driven Claude reads as context next tick — a prompt-injection channel.
# Sanitize before emit.
_MD_BAD = re.compile(r"[\|\n\r\t`<>\[\]\\]")


def md_table_safe(s: str | None, cap: int = 120) -> str:
    """Strip Markdown / HTML / table-breaking characters from untrusted text
    before placing it inside a `| cell |`. Caps length so a malicious title
    cannot blow out the log file."""
    if not s:
        return ""
    out = _MD_BAD.sub(" ", str(s))
    out = re.sub(r"\s+", " ", out).strip()
    if len(out) > cap:
        out = out[: cap - 1] + "…"
    return out

# Iran-relevant tag/keyword filters. Polymarket tags evolve; we cast wide net + filter.
KEYWORDS = ("iran", "khamenei", "tehran", "hormuz", "iranian")
# Markets whose question/slug matches any of these are SOCCER/SPORTS/celebrity etc — exclude
EXCLUDE_KEYWORDS = ("fifa", "world cup", "world-cup", "olympic", "olympics", "soccer",
                    "football match", "win the cup", "win the league", "win the title",
                    "celebrity", "oscar", "grammy", "billboard", "song of the year")


def safe_fetch(url: str, timeout: int = 15) -> list | dict | None:
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "iran-predictive-agent/0.2 (+https://iran-war-dashboard-murex.vercel.app)"},
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError, TimeoutError) as e:
        print(f"[fetch_polymarket] {type(e).__name__}: {e}", file=sys.stderr)
        return None


def _is_relevant(m: dict) -> bool:
    slug = (m.get("slug") or "").lower()
    question = (m.get("question") or "").lower()
    text = slug + " " + question
    if any(kw in text for kw in EXCLUDE_KEYWORDS):
        return False
    return any(kw in text for kw in KEYWORDS)


def fetch_iran_markets(limit: int = 500) -> list[dict]:
    """Polymarket's tag filter doesn't actually filter; we fetch broad sample + local-filter."""
    out: list[dict] = []
    seen = set()
    # Pull pages of active markets via the broad query, filter locally
    for offset in (0, 500, 1000):
        url = f"{GAMMA}?active=true&closed=false&limit={limit}&offset={offset}&order=volume24hr&ascending=false"
        data = safe_fetch(url)
        if not isinstance(data, list):
            break
        if len(data) == 0:
            break
        for m in data:
            if not isinstance(m, dict):
                continue
            slug = m.get("slug") or ""
            if slug in seen:
                continue
            if _is_relevant(m):
                seen.add(slug)
                out.append(m)
    return out


def _to_float(v) -> float | None:
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return float(v)
    if isinstance(v, str):
        try:
            return float(v)
        except ValueError:
            return None
    return None


def normalize_market(m: dict) -> dict:
    """Pull the essential fields and the YES price."""
    price_yes = None
    op = m.get("outcomePrices")
    if isinstance(op, str):
        try:
            arr = json.loads(op)
            if arr:
                price_yes = _to_float(arr[0])
        except (ValueError, IndexError, TypeError):
            pass
    elif isinstance(op, list) and op:
        price_yes = _to_float(op[0])
    return {
        "slug": m.get("slug"),
        "question": (m.get("question") or "").strip(),
        "price_yes": round(price_yes, 4) if price_yes is not None else None,
        "volume_24h": _to_float(m.get("volume24hr")),
        "liquidity": _to_float(m.get("liquidity")),
        "end_date": m.get("endDate"),
    }


def map_to_portfolio_questions(markets: list[dict]) -> dict[str, dict]:
    """Heuristic: map Polymarket markets to portfolio question IDs by keyword."""
    rules = [
        # (question_id, keyword set — slug or question must contain at least one)
        ("A1", {"iran-deal", "iran-us-deal", "iran-nuclear-deal", "nuclear deal", "iran-agreement", "iran agreement", "nuclear deal with iran"}),
        ("A2", {"hormuz", "strait of hormuz"}),
        ("B1", {"us-strike-iran", "us-attack-iran", "us strike iran", "us attack iran", "us bomb iran", "us-bomb-iran", "trump iran strike", "us-iran-war", "us invade iran"}),
        ("B3", {"israel-strike-iran", "israel strike iran", "israel attack iran", "israel bomb iran", "israeli strike on iran"}),
        ("C1", {"khamenei-die", "khamenei-leader", "khamenei-step-down", "khamenei alive", "khamenei dead"}),
        ("C2", {"iran-protest", "iranian-protest", "iran protest", "iranian protest", "iran-regime-fall", "iranian regime fall", "regime change iran"}),
        ("D4", {"brent-130", "brent-150", "oil-130", "oil-150", "brent crude 130", "brent above 130"}),
    ]
    mapping: dict[str, dict] = {}
    for m in markets:
        slug = (m.get("slug") or "").lower()
        question = (m.get("question") or "").lower()
        liq = _to_float(m.get("liquidity")) or 0
        for qid, kws in rules:
            for kw in kws:
                if kw in slug or kw in question:
                    cur_liq = _to_float((mapping.get(qid) or {}).get("liquidity")) or 0
                    if qid not in mapping or liq > cur_liq:
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
        "markets": {m["slug"]: m for m in markets if m.get("slug")},
    }
    SNAPSHOT_PATH.write_text(json.dumps(snap, indent=2))


def write_log(markets: list[dict], mapping: dict[str, dict], prior: dict) -> str:
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    log_path = LOGS_DIR / f"{today}.md"
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    prior_markets = prior.get("markets", {})
    lines = [
        f"# Sources-shifted log — {today}",
        "",
        "## Polymarket scrape (Phase 0 cron)",
        "",
    ]

    if not markets:
        lines.append("_No Iran-related markets returned (network failure or empty result). Snapshot not updated._")
        log_path.write_text("\n".join(lines), encoding="utf-8")
        return str(log_path)

    lines.append(f"Fetched {len(markets)} Iran-related markets at {datetime.now(timezone.utc).strftime('%H:%M UTC')}.")
    lines.append("")

    # Mapped to our portfolio questions
    if mapping:
        lines.append("### Mapped to portfolio questions")
        lines.append("")
        lines.append("| Q | Polymarket slug | YES price | 24h Δ | Liquidity | End |")
        lines.append("|---|---|---|---|---|---|")
        for qid, m in sorted(mapping.items()):
            n = normalize_market(m)
            slug = n["slug"]
            prior_p = (prior_markets.get(slug) or {}).get("price_yes")
            cur_p = n["price_yes"]
            delta = ""
            if prior_p is not None and cur_p is not None:
                d = (cur_p - prior_p) * 100
                delta = f"{d:+.1f}pp"
            cur_str = f"{cur_p*100:.0f}%" if cur_p is not None else "—"
            liq = f"{n['liquidity']:,.0f}" if n.get("liquidity") else "—"
            end = (n.get("end_date") or "")[:10] if n.get("end_date") else "—"
            slug_safe = md_table_safe(slug, cap=80)
            lines.append(f"| **{qid}** | `{slug_safe}` | {cur_str} | {delta} | {liq} | {end} |")
        lines.append("")

    # All Iran-tagged markets
    lines.append("### All Iran-related markets")
    lines.append("")
    lines.append("| Slug | Question | YES | Vol 24h | Liquidity |")
    lines.append("|---|---|---|---|---|")
    def _liq_key(m):
        return -(_to_float(m.get("liquidity")) or 0)
    for m in sorted(markets, key=_liq_key)[:30]:
        n = normalize_market(m)
        cur_str = f"{n['price_yes']*100:.0f}%" if n.get("price_yes") is not None else "—"
        vol = f"{n['volume_24h']:,.0f}" if n.get("volume_24h") else "—"
        liq = f"{n['liquidity']:,.0f}" if n.get("liquidity") else "—"
        q_short = md_table_safe(n.get("question"), cap=80)
        slug_safe = md_table_safe(n.get("slug"), cap=80)
        lines.append(f"| `{slug_safe}` | {q_short} | {cur_str} | {vol} | {liq} |")

    log_path.write_text("\n".join(lines), encoding="utf-8")
    return str(log_path)


def main() -> int:
    markets = fetch_iran_markets()
    if not markets:
        print("[fetch_polymarket] no markets retrieved (network or empty)", file=sys.stderr)
        # Still write empty log entry so the cron has provenance
        write_log([], {}, load_prior_snapshot())
        return 0
    print(f"[fetch_polymarket] retrieved {len(markets)} markets")
    normalized = [normalize_market(m) for m in markets]
    prior = load_prior_snapshot()
    mapping = map_to_portfolio_questions(markets)
    log_path = write_log(markets, mapping, prior)
    save_snapshot(normalized)
    print(f"[fetch_polymarket] wrote {log_path}")
    print(f"[fetch_polymarket] mapped {len(mapping)} questions to portfolio")
    return 0


if __name__ == "__main__":
    sys.exit(main())
