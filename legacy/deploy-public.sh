#!/bin/bash
# Deploy the public (no-business) version of the Iran War Dashboard.
#
# PRIMARY PATH (no action needed from you): once the `iran-war-public` Vercel
# project is git-connected to this repo with build command
# `python3 scripts/build-public.py` and output dir `public-dist`, every push
# to main auto-deploys the public dashboard. Use this script only when you
# want to force a manual deploy without pushing.
#
# Run from the repo root: ./deploy-public.sh

set -e

echo "→ Building public dist..."
python3 scripts/build-public.py

echo "→ Deploying public-dist/ to Vercel (project: iran-war-public)..."
cd public-dist
vercel deploy --prod --yes

echo "→ Done. Public dashboard: https://iran-war-public.vercel.app"
