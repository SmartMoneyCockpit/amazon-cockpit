# Delta: Stability, Health & Ops

This **delta-only** bundle adds operational hardening without touching your existing modules.

## Files included
- `start.sh` — robust launcher (binds to `$PORT`, proxy-safe config, optional constraints install)
- `.streamlit/config.toml` — server basics for reverse proxy
- `constraints.txt` — pins critical libraries to avoid surprise upgrades
- `utils/logging_setup.py` — JSON logging to simplify Render log parsing
- `utils/runtime.py` — cached resources, env helpers, health flag
- `pages/900__Diagnostics.py` — quick smoke tests & health view

## How to apply
1. Extract into your **repo root** (same level as `app.py`).
2. Render → Settings → **Start Command**: `./start.sh`
3. Render → Settings → **Build Command** (unchanged): `pip install -r requirements.txt`
   - Optional: to honor constraints, change to: `pip install -c constraints.txt -r requirements.txt`
4. Redeploy.

## Optional tweaks
- Set env var `PYTHON_VERSION=3.11.9` in Render.
- Set `ALLOWED_ORIGINS` if you need strict origin checks for auxiliary endpoints.

## Notes
- No existing files were overwritten except `.streamlit/config.toml` if present (safe defaults).
- Diagnostics page appears under **Pages → 900__Diagnostics** in Streamlit.
