#!/bin/bash
# Deploy the public (no-business) version of the Iran War Dashboard
# Run from the repo root: ./deploy-public.sh

set -e

STAGING="/tmp/iran-war-public"

echo "→ Preparing public deployment..."
mkdir -p "$STAGING"

# Copy shared assets
cp dashboard.css "$STAGING/"
cp dashboard.js "$STAGING/"
cp public.html "$STAGING/index.html"

# Strip business fields from war-data.json
python3 -c "
import json, sys
d = json.load(open('war-data.json'))
for k in list(d.keys()):
    if any(x in k.lower() for x in ['iranfarhang', 'kip', 'publishing']):
        del d[k]
d.pop('iranfarhangExpanded', None)
d.pop('kipExpanded', None)
json.dump(d, open('$STAGING/war-data.json', 'w'), indent=2, ensure_ascii=False)
print('  Stripped business fields. Keys remaining:', len(d))
"

# Vercel config (no-cache headers)
cat > "$STAGING/vercel.json" << 'EOF'
{
  "cleanUrls": true,
  "headers": [
    { "source": "/war-data.json", "headers": [{ "key": "Cache-Control", "value": "no-cache, no-store, must-revalidate" }, { "key": "Pragma", "value": "no-cache" }] },
    { "source": "/dashboard.js", "headers": [{ "key": "Cache-Control", "value": "no-cache, no-store, must-revalidate" }] },
    { "source": "/dashboard.css", "headers": [{ "key": "Cache-Control", "value": "no-cache, no-store, must-revalidate" }] }
  ]
}
EOF

echo "→ Deploying to Vercel..."
cd "$STAGING"
vercel deploy --prod --yes

echo "→ Done. Public dashboard: https://iran-war-public.vercel.app"
