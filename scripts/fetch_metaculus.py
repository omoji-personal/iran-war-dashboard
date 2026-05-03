"""Fetch Iran-related Metaculus questions via the public REST API.

NOTE 2026-05-03: Metaculus closed their public REST API; authenticated
access only. To enable, create a Metaculus account, get an API token,
and set METACULUS_API_TOKEN in env. Without a token this script
gracefully no-ops and writes a placeholder line in the sources-shifted log.

Usage:
    METACULUS_API_TOKEN=<your-token> python3 scripts/fetch_metaculus.py
"""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LOGS_DIR = REPO_ROOT / "logs" / "sources-shifted"
SNAPSHOT_PATH = REPO_ROOT / "agent" / "metaculus-snapshot.json"

API = "https://www.metaculus.com/api/posts/"


def safe_fetch(url: str, timeout: int = 15) -> dict | None:
    headers = {
        "User-Agent": "iran-predictive-agent/0.2",
        "Accept": "application/json",
    }
    token = os.environ.get("METACULUS_API_TOKEN")
    if token:
        headers["Authorization"] = f"Token {token}"
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError, TimeoutError) as e:
        print(f"[fetch_metaculus] {type(e).__name__}: {e}", file=sys.stderr)
        return None


def fetch_iran_questions(limit: int = 40) -> list[dict]:
    queries = ("iran", "khamenei", "tehran", "hormuz")
    out: list[dict] = []
    seen = set()
    for q in queries:
        url = f"{API}?search={q}&statuses=open&limit={limit}&order_by=-hotness"
        data = safe_fetch(url)
        if not data or not isinstance(data, dict):
            continue
        for item in data.get("results", []):
            qid = item.get("id")
            if qid in seen:
                continue
            seen.add(qid)
            out.append(item)
    return out


def _aggregations_median(q: dict) -> float | None:
    """Modern Metaculus API: medians live under question.aggregations.recency_weighted.latest.centers[0]."""
    question = q.get("question") or {}
    aggs = question.get("aggregations") or {}
    rw = aggs.get("recency_weighted") or {}
    latest = rw.get("latest") or {}
    centers = latest.get("centers") or []
    if centers:
        try:
            return float(centers[0])
        except (ValueError, TypeError):
            return None
    return None


def normalize(q: dict) -> dict:
    qq = q.get("question") or {}
    median = _aggregations_median(q)
    n_forecasters = q.get("nr_forecasters") or qq.get("nr_forecasters")
    return {
        "id": q.get("id"),
        "title": (q.get("title") or "").strip(),
        "url": f"https://www.metaculus.com/questions/{q.get('id')}/",
        "median": round(median, 4) if median is not None else None,
        "p25": None,  # would need percentiles array; skip for now
        "p75": None,
        "n_forecasters": n_forecasters,
        "close_time": qq.get("scheduled_close_time") or q.get("scheduled_close_time"),
    }


def map_to_portfolio_questions(questions: list[dict]) -> dict[str, dict]:
    rules = [
        ("A1", ("iran nuclear deal", "iran-us deal", "iran agreement")),
        ("B1", ("us strike iran", "us attack iran")),
        ("B3", ("israel strike iran", "israel attack iran nuclear")),
        ("C1", ("khamenei", "supreme leader iran")),
        ("C2", ("iran protest", "iran uprising", "iranian regime fall")),
        ("D4", ("brent crude", "oil price")),
    ]
    mapping: dict[str, dict] = {}
    def _n_forecasters(q):
        return q.get("nr_forecasters") or (q.get("question") or {}).get("nr_forecasters") or 0
    for q in questions:
        title = (q.get("title") or "").lower()
        for qid, kws in rules:
            for kw in kws:
                if kw in title:
                    if qid not in mapping or _n_forecasters(q) > _n_forecasters(mapping[qid]):
                        mapping[qid] = q
                    break
    return mapping


def load_prior_snapshot() -> dict:
    if not SNAPSHOT_PATH.exists():
        return {}
    try:
        return json.loads(SNAPSHOT_PATH.read_text())
    except json.JSONDecodeError:
        return {}


def save_snapshot(questions: list[dict]) -> None:
    SNAPSHOT_PATH.parent.mkdir(parents=True, exist_ok=True)
    snap = {
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "questions": {str(q["id"]): q for q in questions if q.get("id") is not None},
    }
    SNAPSHOT_PATH.write_text(json.dumps(snap, indent=2))


def append_log(questions: list[dict], mapping: dict[str, dict], prior: dict) -> str:
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    log_path = LOGS_DIR / f"{today}.md"
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    prior_qs = prior.get("questions", {})
    lines = []
    if log_path.exists():
        lines.append("")
    else:
        lines.append(f"# Sources-shifted log — {today}")
        lines.append("")
    lines.append("## Metaculus scrape (Phase 0 cron)")
    lines.append("")

    if not questions:
        lines.append("_No Iran-related Metaculus questions returned (network failure or empty)._")
        with log_path.open("a" if log_path.exists() else "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        return str(log_path)

    lines.append(f"Fetched {len(questions)} Iran-related questions at {datetime.now(timezone.utc).strftime('%H:%M UTC')}.")
    lines.append("")

    if mapping:
        lines.append("### Mapped to portfolio questions")
        lines.append("")
        lines.append("| Q | Metaculus | Median | 24h Δ | n forecasters | Close |")
        lines.append("|---|---|---|---|---|---|")
        for qid, q in sorted(mapping.items()):
            n = normalize(q)
            qid_str = str(n["id"])
            prior_med = (prior_qs.get(qid_str) or {}).get("median")
            cur_med = n["median"]
            delta = ""
            if prior_med is not None and cur_med is not None:
                d = (cur_med - prior_med) * 100
                delta = f"{d:+.1f}pp"
            cur_str = f"{cur_med*100:.0f}%" if cur_med is not None else "—"
            close = (n.get("close_time") or "")[:10] if n.get("close_time") else "—"
            title = (n.get("title") or "")[:60]
            lines.append(f"| **{qid}** | [#{n['id']} {title}]({n['url']}) | {cur_str} | {delta} | {n.get('n_forecasters') or 0} | {close} |")
        lines.append("")

    lines.append("### All Iran-related Metaculus questions")
    lines.append("")
    lines.append("| ID | Title | Median | n | Close |")
    lines.append("|---|---|---|---|---|")
    def _n_key(q):
        return -(q.get("nr_forecasters") or (q.get("question") or {}).get("nr_forecasters") or 0)
    for q in sorted(questions, key=_n_key)[:20]:
        n = normalize(q)
        cur_str = f"{n['median']*100:.0f}%" if n.get("median") is not None else "—"
        close = (n.get("close_time") or "")[:10] if n.get("close_time") else "—"
        title = (n.get("title") or "")[:80]
        lines.append(f"| [{n['id']}]({n['url']}) | {title} | {cur_str} | {n.get('n_forecasters') or 0} | {close} |")

    with log_path.open("a" if log_path.exists() else "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return str(log_path)


def main() -> int:
    if not os.environ.get("METACULUS_API_TOKEN"):
        print("[fetch_metaculus] METACULUS_API_TOKEN not set — skipping (Metaculus requires auth as of 2025)", file=sys.stderr)
        # Append placeholder so daily log records the skip
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        log_path = LOGS_DIR / f"{today}.md"
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        with log_path.open("a" if log_path.exists() else "w", encoding="utf-8") as f:
            f.write("\n## Metaculus scrape (Phase 0 cron)\n\n_Skipped: Metaculus public API requires `METACULUS_API_TOKEN` (free token, requires account). Set env var to enable._\n")
        return 0
    questions = fetch_iran_questions()
    if not questions:
        print("[fetch_metaculus] no questions retrieved", file=sys.stderr)
        append_log([], {}, load_prior_snapshot())
        return 0
    print(f"[fetch_metaculus] retrieved {len(questions)} questions")
    normalized = [normalize(q) for q in questions]
    prior = load_prior_snapshot()
    mapping = map_to_portfolio_questions(questions)
    log_path = append_log(questions, mapping, prior)
    save_snapshot(normalized)
    print(f"[fetch_metaculus] appended to {log_path}")
    print(f"[fetch_metaculus] mapped {len(mapping)} questions")
    return 0


if __name__ == "__main__":
    sys.exit(main())
