# Render Jobs — Vega Cockpit (UTC schedules)

**Build:** 2025-10-08T21:48:28.445661Z  
Local timezone: America/Mazatlan (UTC−7)

| Job | Command | Cron (UTC) | Notes |
|---|---|---|---|
| alerts_flush | `python workers/alerts_flush.py` | `0 * * * *` | hourly |
| snapshot_heartbeat | `python workers/snapshot_heartbeat.py` | `0 */6 * * *` | every 6h |
| digest_run_weekdays | `python workers/digest_scheduler.py` | `0 20 * * 1-5` | 20:00 UTC = 13:00 local |

UI safety toggles: Daily Digest → Digest Schedule (disable marker), Alerts Center → Silence Alerts (silence marker).
