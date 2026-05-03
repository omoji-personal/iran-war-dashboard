"""Market layer — live prediction-market + financial data fetchers.

These are deliberately STUB-FRIENDLY: each fetcher returns None on network
failure or missing API key, so the engine still emits with whatever's already
in signals.exotic_signals.

Daily workflow:
    python -m engine market-update    # fetches available data, prints suggested
                                       # signals.yaml edits — does NOT auto-edit

Real-time integrations require:
  - Polymarket: public API (no key) at https://gamma-api.polymarket.com/
  - Kalshi: API key required, https://trading-api.kalshi.com
  - Metaculus: public read-only API at https://www.metaculus.com/api2/
  - Brent/WTI: requires data subscription (Quandl, EIA, OilPriceAPI)
  - AIS / dark fleet: requires AIS data feed (MarineTraffic, Spire)
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Optional


def _safe_fetch(url: str, timeout: int = 10) -> Optional[dict]:
    """GET JSON; return None on any error."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "iwd-engine/0.1"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError, TimeoutError):
        return None


def fetch_polymarket_iran_contracts() -> dict:
    """Fetch active Iran-related Polymarket contracts.

    Returns dict mapping contract slug -> {price_yes, volume_24h, liquidity}.
    Returns empty dict if fetch fails.
    """
    # Public Polymarket gamma API — no auth required
    url = "https://gamma-api.polymarket.com/markets?tag=iran&active=true&closed=false&limit=20"
    data = _safe_fetch(url)
    if not data or not isinstance(data, list):
        return {}
    out = {}
    for m in data:
        slug = m.get("slug", "")
        price = None
        if isinstance(m.get("outcomePrices"), str):
            try:
                prices = json.loads(m["outcomePrices"])
                price = float(prices[0]) if prices else None
            except (ValueError, IndexError, TypeError):
                price = None
        out[slug] = {
            "price_yes": price,
            "volume_24h": m.get("volume24hr"),
            "liquidity": m.get("liquidity"),
            "question": m.get("question"),
        }
    return out


def fetch_metaculus_iran_questions() -> dict:
    """Fetch active Metaculus Iran questions."""
    url = "https://www.metaculus.com/api2/questions/?search=iran&status=open"
    data = _safe_fetch(url)
    if not data:
        return {}
    out = {}
    for q in data.get("results", []):
        slug = str(q.get("id"))
        cp = q.get("community_prediction", {})
        if isinstance(cp, dict) and "full" in cp:
            full = cp["full"]
            out[slug] = {
                "title": q.get("title"),
                "median": full.get("q2"),
                "p25": full.get("q1"),
                "p75": full.get("q3"),
            }
    return out


def fetch_brent_spot() -> Optional[float]:
    """Fetch latest Brent spot. Stub — requires real data subscription."""
    # Placeholder: production would use OilPriceAPI / EIA / Quandl
    api_key = os.environ.get("OILPRICEAPI_KEY")
    if not api_key:
        return None
    url = f"https://api.oilpriceapi.com/v1/prices/latest?by_code=BRENT_CRUDE_USD"
    data = _safe_fetch(url + f"&access_token={api_key}")
    if data and isinstance(data, dict):
        return data.get("data", {}).get("price")
    return None


def market_update_report() -> dict:
    """Build a 'suggested edits' report for signals.yaml.

    Does NOT modify signals.yaml — prints recommendations.
    """
    poly = fetch_polymarket_iran_contracts()
    meta = fetch_metaculus_iran_questions()
    brent = fetch_brent_spot()

    return {
        "polymarket_contracts_found": len(poly),
        "metaculus_questions_found": len(meta),
        "brent_spot_usd": brent,
        "suggested_signals_yaml_edits": _suggest_edits(poly, meta, brent),
        "raw": {"polymarket": poly, "metaculus": meta},
    }


def _suggest_edits(poly: dict, meta: dict, brent: Optional[float]) -> list[str]:
    edits = []
    # Look for ceasefire-holds / deal contracts
    for slug, c in poly.items():
        q = (c.get("question") or "").lower()
        price = c.get("price_yes")
        if price is None:
            continue
        if "ceasefire" in q and "hold" in q:
            edits.append(f"  exotic_signals.polymarket_ceasefire_holds_pct: {round(price * 100)}  # {slug}")
        elif "iran" in q and ("deal" in q or "agreement" in q):
            edits.append(f"  exotic_signals.polymarket_deal_by_jun30_pct: {round(price * 100)}  # {slug}")
    if brent is not None:
        edits.append(f"  today_scalars.brent: {brent}  # OilPriceAPI live")
    if not edits:
        edits.append("# (no actionable suggestions — fetchers returned no data; check network/keys)")
    return edits


if __name__ == "__main__":
    import json as _json
    print(_json.dumps(market_update_report(), indent=2))
