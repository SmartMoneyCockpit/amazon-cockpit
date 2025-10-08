
# Deploy on Render — Vega Cockpit (Handoff)

**Build:** 2025-10-08T21:24:09.518635Z  
Target: Streamlit app on Render (Web Service) + optional background cron via Render Jobs/Workers.

---

## 1) Create the Web Service
- **Environment**: Python
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`
- **Instance**: your choice (Starter is fine)
- **Region**: your choice
- **Environment Variable**: `TZ=America/Mazatlan` (optional)

### Secrets / Env (min recommended)
| Key | Purpose | Notes |
|---|---|---|---|
| `SENDGRID_API_KEY` | Email sender | Required for email sends |
| `DIGEST_EMAIL_FROM` | Digest FROM | e.g., `no-reply@yourdomain.com` |
| `DIGEST_EMAIL_TO` | Digest TO | your email |
| `ALERTS_EMAIL_FROM` | Alerts FROM | optional (fallback to DIGEST_*) |
| `ALERTS_EMAIL_TO` | Alerts TO | optional (fallback to DIGEST_*) |
| `WEBHOOK_URL` | Alerts webhook | optional |
| `SHEETS_KEY` | Google Sheets key | only if using Sheets bridge |
| `TZ` | Timezone | `America/Mazatlan` |

> Do **not** commit secrets. Store them in Render’s dashboard.

### Persistent storage (optional but recommended)
Render’s disk is ephemeral on deploy. If you want backups & snapshots to persist across deploys, attach a **Disk** (e.g., 1–5 GB) and mount it at project root. Then point your service to use that path, or symlink `backups/` and `snapshots/` to your mounted disk path.

```bash
# example postdeploy step (optional)
ln -s /var/data/backups backups || true
ln -s /var/data/snapshots snapshots || true
ln -s /var/data/logs logs || true
```

---

## 2) Scheduling Options (choose one)
- **Render Cron Jobs**: create three Jobs in the Render dashboard (or Workers) calling:
  - `python workers/alerts_flush.py` (hourly)
  - `python workers/snapshot_heartbeat.py` (every 6 hours)
  - `python workers/digest_scheduler.py` (daily, e.g., 13:00 local)
- **Honor marker**: Daily Digest honors `tools/.digest_disabled` (toggle in **Daily Digest → Digest Schedule**).

> If you prefer IaC, see `render.yaml` in this repo as a starting point (Web only). Configure Jobs in the dashboard for exact schedules.

---

## 3) Post-deploy Smoke (UI)
Open **Utilities → Developer Tools**:
- Click **Run All Smoke Tests**
- (Optional) **Create demo data** to populate snapshots/backups/logs
- Use Quick Links to validate **Daily Digest**, **Alerts Center**, **Backup Manager**, **File Inventory**, **Jobs History**

---

## 4) GitHub “release snapshot” (optional)
- Tag a release and attach:
  - `vega_cockpit_cumulative_14_105_BUNDLE.zip`
  - `bundle_file_inventory.csv`
  - `bundle_sha1_manifest.txt`

---

## 5) Troubleshooting
- **Email skips**: appears as `skipped` if keys are missing — set `SENDGRID_API_KEY` + from/to.
- **No artifacts**: run **Run Digest Now** or use **Demo Data Seeder**.
- **Disk/path**: if using a persistent Disk, point `backups/`, `snapshots/`, and `logs/` to it (or symlink).

