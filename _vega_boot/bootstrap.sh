#!/usr/bin/env bash
set -euo pipefail
echo "== Vega one-and-done bootstrap =="
BOOTDIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Ensure sitecustomize to fix imports
if [ ! -f sitecustomize.py ]; then
  cp "$BOOTDIR/sitecustomize.py" ./sitecustomize.py
  echo "Wrote sitecustomize.py"
fi

# Seed reports and calendars
python3 "$BOOTDIR/bootstrap_reports.py"

# Ensure data dir and approved tickers
mkdir -p data
if [ ! -f data/approved_tickers.json ]; then
  cp "$BOOTDIR/approved_tickers.json" data/approved_tickers.json
  echo "Seeded data/approved_tickers.json"
fi

# If .env missing, drop a bootstrap version (user can edit safely)
if [ ! -f .env ]; then
  cp "$BOOTDIR/.env.bootstrap" ./.env
  echo "Wrote .env (bootstrap). Update IBKR_BRIDGE_URL and IB_BRIDGE_API_KEY."
fi

echo "Bootstrap complete. Run Streamlit with:  streamlit run app.py"