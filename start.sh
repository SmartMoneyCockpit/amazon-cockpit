#!/usr/bin/env bash
set -euo pipefail

export PORT="${PORT:-10000}"
mkdir -p ~/.streamlit
cat > ~/.streamlit/config.toml <<'EOF'
[server]
headless = true
address = "0.0.0.0"
enableCORS = true
enableXsrfProtection = false
maxMessageSize = 200

[browser]
gatherUsageStats = false
EOF

echo "[start.sh] PORT=${PORT}"

# Optional: honor constraints to avoid surprise upgrades
if [[ -f "constraints.txt" ]]; then
  echo "[start.sh] Installing constraints (if any)"
  pip install -q --no-input -c constraints.txt -r requirements.txt || true
fi

# Minimal watchdog: if Streamlit exits with non-zero, restart (max 5 tries)
attempt=0
until streamlit run app.py --server.port "$PORT" --server.address 0.0.0.0; do
  code=$?
  attempt=$((attempt+1))
  echo "[start.sh] Streamlit exited with code $code (attempt $attempt/5). Restarting..."
  if [[ $attempt -ge 5 ]]; then
    echo "[start.sh] Max retries reached. Exiting."
    exit $code
  fi
  sleep 2
done
