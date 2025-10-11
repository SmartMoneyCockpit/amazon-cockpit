# One-and-Done Ops Delta

This bundle contains **only new/changed files** to harden your Render deployment.

## Files
- `start.sh` — robust launcher (PORT binding + mini watchdog)
- `.streamlit/config.toml` — proxy-safe defaults
- `constraints.txt` — pins critical libs
- `render.yaml` — sets build/start commands (safe defaults)
- `utils/logging_setup.py` — JSON logs
- `utils/runtime.py`, `utils/cors.py` — helpers
- `pages/000__Health.py`, `pages/900__Diagnostics.py` — quick checks

## Render Settings
- **Start Command:** `./start.sh`
- **Build Command:** `pip install -c constraints.txt -r requirements.txt`
- **Health Check Path:** `/` (or set to `/?health=1` and keep Health page)
- **Env Vars:** set `PYTHON_VERSION=3.11.9`; keep your existing secrets.

## Notes
- No destructive changes; drop-in safe.
- If you don't want the Diagnostics/Health pages visible to users, rename them or hide via Streamlit navigation.
