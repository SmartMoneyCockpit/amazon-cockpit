# Deploy on Render — Vega Cockpit (Handoff)

**Build:** 2025-10-08T21:48:28.444886Z  
This doc covers Render web service setup, envs, scheduling options, and post‑deploy smoke.
(If you already merged a previous copy, this PR just keeps it alongside job docs.)

## Web Service
- Build: `pip install -r requirements.txt`
- Start: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`
- Env: set `TZ=America/Mazatlan` (optional)

## Secrets / Env (minimum)
SENDGRID_API_KEY, DIGEST_EMAIL_FROM, DIGEST_EMAIL_TO, (optional) ALERTS_EMAIL_FROM/TO, WEBHOOK_URL, SHEETS_KEY.

## Scheduling
Use Render Jobs/Workers with the commands and UTC crons listed in **RENDER_JOBS.md**.

## Post‑deploy Smoke
Utilities → Developer Tools → Run All Smoke Tests; optionally create demo data; use Quick Links to validate Daily Digest, Alerts, Backup Manager, File Inventory, Jobs History.
