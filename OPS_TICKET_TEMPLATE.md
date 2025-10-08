
# OPS Ticket — Render Jobs & Deploy Handoff (Vega Cockpit)

**Build:** 2025-10-08T21:59:24.540131Z  
**Owner:** @<your-handle>  
**Service:** Vega Cockpit (Streamlit)  
**Region:** <Render region>  
**Env TZ:** America/Mazatlan (Render jobs use **UTC**; see conversions below)

---

## 1) Scope
- Stand up/confirm **Web Service** on Render (Streamlit, `app.py`).
- Create/confirm **Cron Jobs** for alerts, heartbeat, and digest.
- Verify post‑deploy using built‑in smoke tests.
- Attach persistent disk if required for `backups/`, `snapshots/`, `logs/`.

---

## 2) Web Service (Render)
- **Build:** `pip install -r requirements.txt`
- **Start:** `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`
- **Env (minimum):**
  - `SENDGRID_API_KEY` (required for email)
  - `DIGEST_EMAIL_FROM`, `DIGEST_EMAIL_TO`
  - *(optional)* `ALERTS_EMAIL_FROM`, `ALERTS_EMAIL_TO`, `WEBHOOK_URL`
  - *(optional)* `SHEETS_KEY`
  - `TZ=America/Mazatlan`

> Secrets go in Render dashboard; do **not** commit to git.

---

## 3) Cron Jobs (Render → Jobs/Workers) — **UTC**
| Job Name | Command | Cron (UTC) | Notes |
|---|---|---|---|
| `alerts_flush` | `python workers/alerts_flush.py` | `0 * * * *` | hourly |
| `snapshot_heartbeat` | `python workers/snapshot_heartbeat.py` | `0 */6 * * *` | every 6h |
| `digest_run_weekdays` | `python workers/digest_scheduler.py` | `0 20 * * 1-5` | 20:00 UTC ≙ 13:00 America/Mazatlan |

**Conversion aide:** America/Mazatlan is typically **UTC−7**. Confirm offset on deployment day and adjust if needed.

**Safety toggles (UI):**
- Daily Digest → **Digest Schedule** toggle writes/removes `tools/.digest_disabled`.
- Alerts Center → **Silence Alerts** writes `logs/alerts_silenced.json` (Cancel available).

---

## 4) Persistent Disk (optional but recommended)
Mount a disk (e.g., 5 GB) and map:  
`/var/data` → symlink `backups/`, `snapshots/`, `logs/` to persist across deploys.

Example post‑deploy script:
```bash
ln -s /var/data/backups backups || true
ln -s /var/data/snapshots snapshots || true
ln -s /var/data/logs logs || true
```

---

## 5) Post‑Deploy Verification (1–2 min)
- UI: **Utilities → Developer Tools → Run All Smoke Tests** (expect Overall = OK or actionable CHECKs).
- UI: **Daily Digest → Run Digest Now** (artifacts in `backups/`, log entry `digest_run`).  
- UI: **Alerts Center → Re‑send latest alerts** (log entry `alerts_flush`).  
- UI: **Backup Manager → Backups Browser** (download one file successfully).  
- UI: **Jobs History** (see new entries today).

CLI (optional):
```bash
python workers/alerts_flush.py
python workers/snapshot_heartbeat.py
python workers/digest_scheduler.py
```

---

## 6) Rollback Plan
- Disable Jobs (Render) and/or toggle **Digest Schedule** off in UI.
- Revert PR or redeploy previous successful Render build.
- Restore artifacts from `backups/` if needed.

---

## 7) Links
- **Repo:** <https://github.com/<org>/<repo>>
- **Render Web:** <https://dashboard.render.com/web/<your-service-id>>
- **Render Jobs:** <https://dashboard.render.com/jobs>

---

## 8) Notes / Known Items
- Emails will log **skipped** if keys missing — expected until keys are set.
- If Digest is disabled (marker present), scheduler runs but will be a no‑op.
- Network limits can block IP/DNS tests; **Settings Controls → Network Debug** shows status.

---

## 9) Acceptance Criteria
- [ ] Web service is healthy and reachable.
- [ ] Jobs created with correct **UTC** crons and enabled.
- [ ] Smoke tests pass (or CHECKs addressed).
- [ ] Digest artifacts appear in `backups/` and Jobs History shows entries.
- [ ] (If using Disk) snapshots/backups/logs persist across a redeploy.
