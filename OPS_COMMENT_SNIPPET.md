# Ops: Create Render Cron Jobs (UTC) + Quick Verify

**Service:** Vega Cockpit (Streamlit)  
**Local TZ:** America/Mazatlan (usually **UTC-7**) — crons below are **UTC**.

## ✅ Jobs to create (Render → *Jobs/Workers* → *New Cron Job*)

| Job name | Command | Cron (UTC) | Purpose |
|---|---|---|---|
| `alerts_flush` | `python workers/alerts_flush.py` | `0 * * * *` | Send alerts email/webhook if payload changed; logs to `logs/vega_jobs.jsonl` |
| `snapshot_heartbeat` | `python workers/snapshot_heartbeat.py` | `0 */6 * * *` | Write `snapshots/heartbeat_*.csv` |
| `digest_run_weekdays` | `python workers/digest_scheduler.py` | `0 20 * * 1-5` | 20:00 UTC = **13:00 Mazatlán** (weekdays) for the daily digest |

> If you prefer 7 days/week for the digest, use `0 20 * * *`.

**Env to match the Web service (set in each Job):**
- `SENDGRID_API_KEY`, `DIGEST_EMAIL_FROM`, `DIGEST_EMAIL_TO`
- (optional) `ALERTS_EMAIL_FROM`, `ALERTS_EMAIL_TO`, `WEBHOOK_URL`
- (optional) `SHEETS_KEY`
- `TZ=America/Mazatlan` (optional, for logs/UI)

**Persistence (recommended):** If the Web uses a persistent Disk for `backups/`, `snapshots/`, `logs/`, attach the same to Jobs or ensure a shared path.

---

## 🧯 Safety toggles (already in the UI)
- **Disable Digest**: *Daily Digest → Digest Schedule* — writes / removes `tools/.digest_disabled`.
- **Silence Alerts**: *Alerts Center → Silence Alerts* — creates `logs/alerts_silenced.json`. (Cancel available.)

---

## 🔎 How to verify (1 min)

**UI (preferred)**
1. *Utilities → Developer Tools* → **Run All Smoke Tests** (expect Overall **OK** or actionable **CHECK**).
2. *Daily Digest* → **Run Digest Now** → artifacts in `backups/`, log shows `digest_run`.
3. *Alerts Center* → **Re-send latest alerts** → log shows `alerts_flush`.
4. *Backup Manager* → Download any file.

**CLI (optional)**
```bash
python workers/alerts_flush.py
python workers/snapshot_heartbeat.py
python workers/digest_scheduler.py
```

---

## 🧰 Troubleshooting
- **Email didn’t send** → missing `SENDGRID_API_KEY` or from/to → UI will show `skipped`.
- **Nothing at schedule time** → Job disabled or cron not UTC.
- **Digest appears off** → `.digest_disabled` marker present — toggle in UI to re-enable.
- **Alerts show “no_change”** → payload didn’t change (normal). Use **Re-send latest** to force an email.

---

## ✅ Acceptance checklist
- [ ] Web service healthy & reachable.
- [ ] Three Jobs created with the cron strings above (UTC) and **enabled**.
- [ ] Smoke tests pass (or CHECKs noted with action).
- [ ] New `digest_run` / `alerts_flush` entries appear in Jobs History today.
- [ ] (If Disk used) `snapshots/` & `backups/` persist across a redeploy.
