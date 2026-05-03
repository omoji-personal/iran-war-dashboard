"""Build the stripped public-deploy bundle for the iran-war-public Vercel project.

Vercel's iran-war-public project is configured with build command
`python3 scripts/build-public.py` and outputDirectory `public-dist/`.

This shim replaces the old engine-emit flow (legacy/scripts/build-public.py)
with the new render.py-based approach: render `public.html` (stripped variant
without methodology/logs sections) and assemble it as `public-dist/index.html`
along with `dashboard.css`.

Usage (called by Vercel build):
    python3 scripts/build-public.py
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = REPO_ROOT / "public-dist"


def _ensure_pyyaml() -> None:
    """Vercel's Python build sandbox ships without pyyaml. Install it on first run."""
    try:
        import yaml  # noqa: F401
        return
    except ImportError:
        pass
    print("[build-public] installing pyyaml (Vercel sandbox dependency)", file=sys.stderr)
    rc = subprocess.call(
        [sys.executable, "-m", "pip", "install", "--quiet", "--disable-pip-version-check", "pyyaml"],
        cwd=REPO_ROOT,
    )
    if rc != 0:
        # Try with --user flag if global install fails (Vercel sandbox restrictions)
        rc = subprocess.call(
            [sys.executable, "-m", "pip", "install", "--quiet", "--disable-pip-version-check", "--user", "pyyaml"],
            cwd=REPO_ROOT,
        )
    if rc != 0:
        print(f"[build-public] pyyaml install failed (rc={rc})", file=sys.stderr)
        sys.exit(rc)


def main() -> int:
    _ensure_pyyaml()
    print("[build-public] rendering homepage via scripts/render.py --public")
    rc = subprocess.call([sys.executable, "scripts/render.py", "--public"], cwd=REPO_ROOT)
    if rc != 0:
        print(f"[build-public] render.py failed with rc={rc}", file=sys.stderr)
        return rc

    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir(parents=True)

    # The stripped variant becomes index.html on the iran-war-public domain
    src_public = REPO_ROOT / "public.html"
    if not src_public.exists():
        print(f"[build-public] expected {src_public} after render — missing", file=sys.stderr)
        return 1
    shutil.copy(src_public, OUTPUT_DIR / "index.html")

    # Copy CSS so the page actually styles
    src_css = REPO_ROOT / "dashboard.css"
    shutil.copy(src_css, OUTPUT_DIR / "dashboard.css")

    # Copy the YAML data so Vercel's text/plain Content-Type header serves it readable
    for f in ("portfolio.yaml", "lr_table.yaml", "reference_classes.yaml", "robots.txt"):
        src = REPO_ROOT / f
        if src.exists():
            shutil.copy(src, OUTPUT_DIR / f)

    # Ship a slim vercel.json into the bundle so headers + cleanUrls are correct
    vercel_cfg = (
        '{\n'
        '  "cleanUrls": false,\n'
        '  "headers": [\n'
        '    {\n'
        '      "source": "/(.*)\\\\.yaml",\n'
        '      "headers": [\n'
        '        { "key": "Content-Type", "value": "text/plain; charset=utf-8" },\n'
        '        { "key": "Cache-Control", "value": "no-cache, no-store, must-revalidate" }\n'
        '      ]\n'
        '    },\n'
        '    {\n'
        '      "source": "/index.html",\n'
        '      "headers": [\n'
        '        { "key": "Cache-Control", "value": "no-cache, no-store, must-revalidate" },\n'
        '        { "key": "X-Content-Type-Options", "value": "nosniff" },\n'
        '        { "key": "Referrer-Policy", "value": "no-referrer-when-downgrade" }\n'
        '      ]\n'
        '    },\n'
        '    {\n'
        '      "source": "/dashboard.css",\n'
        '      "headers": [\n'
        '        { "key": "Cache-Control", "value": "no-cache, no-store, must-revalidate" }\n'
        '      ]\n'
        '    }\n'
        '  ]\n'
        '}\n'
    )
    (OUTPUT_DIR / "vercel.json").write_text(vercel_cfg, encoding="utf-8")

    print(f"[build-public] wrote {OUTPUT_DIR}/")
    print(f"[build-public]   index.html, dashboard.css, portfolio.yaml, lr_table.yaml, reference_classes.yaml, robots.txt, vercel.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
