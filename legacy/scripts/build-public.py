#!/usr/bin/env python3
"""
Build the public (no-business) dashboard into ./public-dist/.

Used by the `iran-war-public` Vercel project as its build command.
Produces a self-contained deploy with:
  - index.html         (from public.html)
  - war-data.json      (with iranfarhang/kip/publishing keys stripped)
  - dashboard.css, dashboard.js  (shared assets)
  - vercel.json        (from public-vercel.json — cache + rewrite rules)

Mirrors what ./deploy-public.sh does, but outputs a directory for git-triggered
Vercel builds instead of pushing via the CLI.

Run: python3 scripts/build-public.py
"""

import json
import pathlib
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DIST = ROOT / "public-dist"


def strip_business(data: dict) -> dict:
    """Remove business-specific keys from war-data.json."""
    keywords = ("iranfarhang", "kip", "publishing")
    # Filter top-level keys whose names contain any business keyword
    cleaned = {
        k: v
        for k, v in data.items()
        if not any(kw in k.lower() for kw in keywords)
    }
    # Explicit drops for expansion flags that don't match the substring filter
    cleaned.pop("iranfarhangExpanded", None)
    cleaned.pop("kipExpanded", None)
    return cleaned


def main() -> int:
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)

    # Shared assets
    for name in ("dashboard.css", "dashboard.js"):
        shutil.copy2(ROOT / name, DIST / name)

    # public.html becomes index.html
    shutil.copy2(ROOT / "public.html", DIST / "index.html")

    # vercel.json for the public project (cache headers; no rewrite needed —
    # index.html is literally at /)
    public_vercel = json.loads((ROOT / "public-vercel.json").read_text())
    public_vercel.pop("rewrites", None)  # no longer needed; index.html IS /
    (DIST / "vercel.json").write_text(json.dumps(public_vercel, indent=2) + "\n")

    # Stripped war-data.json
    data = json.loads((ROOT / "war-data.json").read_text())
    before = len(data)
    cleaned = strip_business(data)
    after = len(cleaned)
    (DIST / "war-data.json").write_text(
        json.dumps(cleaned, ensure_ascii=False, indent=2) + "\n"
    )

    print(f"✓ public-dist/ built")
    print(f"  war-data.json: {before} keys → {after} keys ({before - after} stripped)")
    print(f"  files: {sorted(p.name for p in DIST.iterdir())}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
