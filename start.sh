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

exec streamlit run app.py --server.port "$PORT" --server.address 0.0.0.0
