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
    """Vercel's Python build sandbox is uv-managed (PEP 668 externally-managed).
    pip install requires --break-system-packages flag — safe in ephemeral CI sandbox."""
    try:
        import yaml  # noqa: F401
        return
    except ImportError:
        pass
    print("[build-public] installing pyyaml (Vercel sandbox dependency)", file=sys.stderr)
    install_attempts = [
        # Vercel/uv-managed Python: PEP 668 requires --break-system-packages
        [sys.executable, "-m", "pip", "install", "--quiet", "--disable-pip-version-check", "--break-system-packages", "pyyaml"],
        # Fallback: --user flag with --break-system-packages
        [sys.executable, "-m", "pip", "install", "--quiet", "--disable-pip-version-check", "--user", "--break-system-packages", "pyyaml"],
        # Fallback: install to a temp dir and add to PYTHONPATH
        [sys.executable, "-m", "pip", "install", "--quiet", "--disable-pip-version-check", "--target", "/tmp/buildpub-deps", "pyyaml"],
    ]
    for cmd in install_attempts:
        rc = subprocess.call(cmd, cwd=REPO_ROOT)
        if rc == 0:
            # If --target install, prepend to sys.path
            if "--target" in cmd:
                sys.path.insert(0, "/tmp/buildpub-deps")
            try:
                import yaml  # noqa: F401
                print(f"[build-public] pyyaml installed via: {' '.join(cmd[3:])}", file=sys.stderr)
                return
            except ImportError:
                continue
    print("[build-public] pyyaml install failed across all strategies", file=sys.stderr)
    sys.exit(1)


def main() -> int:
    _ensure_pyyaml()
    print("[build-public] rendering homepage via scripts/render.py --public")
    # Import render in-process so it inherits any pyyaml install we just did
    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    # Set argv so render.main() sees --public
    saved_argv = sys.argv
    try:
        sys.argv = ["render.py", "--public"]
        import render
        render.main()
    except SystemExit as e:
        if e.code not in (0, None):
            print(f"[build-public] render.py exited rc={e.code}", file=sys.stderr)
            return int(e.code) if isinstance(e.code, int) else 1
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"[build-public] render.py raised: {e}", file=sys.stderr)
        return 1
    finally:
        sys.argv = saved_argv

    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir(parents=True)

    # The stripped variant becomes index.html on the iran-war-public domain
    src_public = REPO_ROOT / "public.html"
    if not src_public.exists():
        print(f"[build-public] expected {src_public} after render — missing", file=sys.stderr)
        return 1
    shutil.copy(src_public, OUTPUT_DIR / "index.html")

    # Copy CSS so the page actually styles, but strip rules that name
    # Iranfarhang / Kipa selectors. Selectors leak business names even if no
    # element on the public page uses them.
    src_css = REPO_ROOT / "dashboard.css"
    css_text = src_css.read_text(encoding="utf-8")
    # Remove any line whose CSS selector or value mentions a private business name.
    # Conservative line-level filter — preserves layout rules but drops the 6 known
    # `qcard-cat-iranfarhang` / `qcard-cat-kipa` / `board-cat-iranfarhang` / `board-cat-kipa`
    # selector lines plus any future addition matching the same pattern.
    private_css_tokens = ("iranfarhang", "kipa", "family-business")
    public_css_lines = []
    skip_block = False
    for line in css_text.splitlines():
        low = line.lower()
        if any(tok in low for tok in private_css_tokens):
            # Drop this line. If it opened a block (line ends in `{`), drop until the
            # matching `}` on its own line.
            if line.rstrip().endswith("{"):
                skip_block = True
            continue
        if skip_block:
            if line.strip().startswith("}"):
                skip_block = False
            continue
        public_css_lines.append(line)
    public_css = "\n".join(public_css_lines)
    (OUTPUT_DIR / "dashboard.css").write_text(public_css, encoding="utf-8")

    # Copy ONLY robots.txt — the YAML data files contain F-class
    # (Iranfarhang / Kipa) entries that must not be served on the public deploy.
    # If the public site needs to expose data, render filtered JSON via the
    # render pipeline; never copy raw portfolio/lr/reference YAMLs.
    for f in ("robots.txt",):
        src = REPO_ROOT / f
        if src.exists():
            shutil.copy(src, OUTPUT_DIR / f)

    # Write a public-scoped portfolio.yaml that excludes F-categories — operator
    # might still want a structured-data view of the public questions.
    # Defense-in-depth: filter on BOTH category AND stakeholder-tag so a Q
    # mistakenly placed in a public category but still tagged private gets stripped.
    import yaml as _yaml
    portfolio_data = _yaml.safe_load((REPO_ROOT / "portfolio.yaml").read_text(encoding="utf-8"))
    PRIVATE = {"family_business_iranfarhang", "family_business_kipa"}
    PRIVATE_TAGS = {"omid_personal", "iranfarhang_business", "kipa_business"}
    def _is_private(q):
        if q.get("category") in PRIVATE:
            return True
        return any(t in PRIVATE_TAGS for t in q.get("stakeholder_tags", []))
    public_questions = [q for q in portfolio_data.get("questions", []) if not _is_private(q)]
    # Scrub public-facing question payloads of any tag mentioning private channels
    for q in public_questions:
        q["stakeholder_tags"] = [t for t in q.get("stakeholder_tags", []) if t not in PRIVATE_TAGS]
    # Build a clean metadata block (drop F-class category counts + Iranfarhang/Kipa notes)
    src_md = portfolio_data.get("metadata", {})
    public_md = {
        "engine_version": src_md.get("engine_version"),
        "spec_version": src_md.get("spec_version"),
        "last_full_review": str(src_md.get("last_full_review")) if src_md.get("last_full_review") else None,
        "next_review": str(src_md.get("next_review")) if src_md.get("next_review") else None,
        "total_questions": len(public_questions),
        "public_view": True,
        "note": "Public deploy. Private categories filtered out at build time.",
    }
    public_portfolio = {"questions": public_questions, "metadata": public_md}
    (OUTPUT_DIR / "portfolio.yaml").write_text(
        _yaml.safe_dump(public_portfolio, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )

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
    print(f"[build-public]   index.html, dashboard.css, portfolio.yaml (stripped), robots.txt, vercel.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
