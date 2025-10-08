
# Render Jobs — Vega Cockpit (Operational Handoff)

**Build:** 2025-10-08T21:35:10.248898Z

This document lists the **exact jobs** to create in Render for the cockpit to run hands‑off.  
Schedules below assume **Render cron uses UTC**. Your local timezone is **America/Mazatlan (UTC‑7)**.

---

## Summary (UTC schedules)

| Job | Command | Suggested Schedule (UTC) | Notes |
|---|---|---|---|
| Alerts Flush | `python workers/alerts_flush.py` | `0 * * * *` (hourly) | Emails/webhook if payload changed; logs to `logs/vega_jobs.jsonl` |
| Snapshot Heartbeat | `python workers/snapshot_heartbeat.py` | `0 */6 * * *` (every 6h) | Writes `snapshots/heartbeat_*.csv` |
| Digest Run (weekdays) | `python workers/digest_scheduler.py` | `0 20 * * 1-5` | 20:00 UTC ≙ 13:00 **America/Mazatlan** |

> If you prefer daily 7 days/week: use `0 20 * * *` instead of the weekday rule.

**Safety toggles**
- **Disable Digest** (UI): Daily Digest → *Digest Schedule* → toggle creates/removes `tools/.digest_disabled` marker.  
- **Silence Alerts** (UI): Alerts Center → *Silence Alerts* writes `logs/alerts_silenced.json` marker (you can cancel anytime).

---

## Create the jobs on Render

1. In Render, go to **Jobs** (or Workers) → **New Job** → **Cron**.  
2. For each job:
   - **Name:** `alerts_flush` / `snapshot_heartbeat` / `digest_run`
   - **Command:** from the table above
   - **Schedule (UTC):** from the table above
   - **Environment:** same as your web service (ensure `SENDGRID_API_KEY`, `DIGEST_EMAIL_*`, etc.)

> Tip: if you attached a persistent Disk to your web service, create a Disk for the Jobs too (or ensure paths are shared) so `backups/`, `snapshots/`, and `logs/` persist.

---

## How to verify (1 minute)

**A) Alerts Flush**
```bash
python workers/alerts_flush.py
```
- Expect a new entry in `logs/vega_jobs.jsonl` with `"job":"alerts_flush"` and `"status":"sent"` or `"no_change"`.

**B) Heartbeat**
```bash
python workers/snapshot_heartbeat.py
```
- Expect `snapshots/heartbeat_*.csv` and a log entry.

**C) Digest**
```bash
python workers/digest_scheduler.py
```
- Expect artifacts in `backups/` and a `"digest_run"` entry in the jobs log. If email keys are missing, it logs `"skipped"` (OK).

---

## Troubleshooting

- **Email didn’t send** → Check `SENDGRID_API_KEY`, `DIGEST_EMAIL_FROM`, `DIGEST_EMAIL_TO`. UI shows status in Daily Digest.
- **Nothing happens at schedule time** → Make sure the Job is **enabled** in Render and schedule is **UTC**.  
- **Digest disabled?** → The UI toggle writes `tools/.digest_disabled`; remove it in the UI or delete the file.
- **Alerts not sending** → If the payload didn’t change, `"status":"no_change"` is expected. Use **Re‑send latest** in Alerts Center to force.

---

## Appendix — Local↔UTC quick reference

- **America/Mazatlan** today is **UTC‑7**.  
  - 13:00 local → **20:00 UTC**  
  - 09:00 local → **16:00 UTC**  
  - 07:00 local → **14:00 UTC**

