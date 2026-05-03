#!/bin/bash
# Manual local tick — runs the same procedure the cron uses, locally.
# Useful when you want to refresh data immediately without waiting for 06:00 ET.
#
# Usage:
#   bash scripts/run_tick.sh
#
# Differences vs cron:
# - Commits to the CURRENT branch you're on (not proposed-signals/{TODAY})
# - Skips the gh pr create step
# - You decide whether to push manually
#
# Free-only: no paid feeds, no auth required for any default scraper.

set -e
cd "$(dirname "$0")/.."

echo "=== Iran Predictive Agent — manual tick $(date -u +%Y-%m-%dT%H:%M:%SZ) ==="

if [ ! -d ".venv" ]; then
  python3 -m venv .venv
  source .venv/bin/activate
  pip install -q pyyaml pydantic pytest
else
  source .venv/bin/activate
fi

TODAY=$(date -u +%Y-%m-%d)

echo "--- STEP 1: scrapers ---"
python3 scripts/fetch_polymarket.py 2>&1 | tail -3
python3 scripts/fetch_metaculus.py 2>&1 | tail -3
python3 scripts/fetch_manifold.py 2>&1 | tail -3

echo "--- STEP 2: snapshot ---"
python3 -c "
import json, yaml
from pathlib import Path
p = yaml.safe_load(Path('portfolio.yaml').read_text())
snap = {'date': '${TODAY}', 'engineVersion': p['metadata']['engine_version'], 'phase': 0,
        'questions': [{'id': q['id'], 'category': q['category'], 'probability': q['current_probability'],
                      'ci_80': q['current_credible_interval_80'], 'last_updated': str(q['last_updated'])}
                      for q in p['questions']]}
hp = Path('engine_history.json')
hist = json.loads(hp.read_text()) if hp.exists() else []
hist = [h for h in hist if h.get('date') != '${TODAY}']
hist.append(snap)
hp.write_text(json.dumps(hist, indent=2))
print(f'snapshots: {len(hist)}')
"

echo "--- STEP 3: render ---"
python3 scripts/render.py --public 2>&1 | tail -3

echo "--- STEP 4: tests ---"
python3 -m pytest -q 2>&1 | tail -3

echo
echo "=== Tick complete. Files updated. ==="
echo "To deploy:"
echo "  git add -A && git commit -m 'manual tick ${TODAY}' && git push"
echo
echo "Or to review first:"
echo "  git diff --stat"
