# Next Step: Daily Digest → Google Sheets Metadata Log

Adds a simple **1‑row per day** log of KPIs + alerts counts into a Google Sheet.

## Files
- `utils/digest_log.py` → computes KPIs and appends to a Sheet
- `snapshot_log.py` → Streamlit entry that can generate the PDF and append the log
- `modules_home_digest_writeback_snippet.py` → UI snippet to add a button on Home

## Secrets
- `gsheets_digest_log_sheet_id` → Google Sheet **file ID**
- `gsheets_credentials` → service account JSON (already used in earlier steps)

## How to apply
1) Copy `utils/digest_log.py` and `snapshot_log.py` into your project.
2) In `modules/home.py`, paste the snippet (`modules_home_digest_writeback_snippet.py`) below the Daily Digest block.
3) Add secret `gsheets_digest_log_sheet_id` and share the sheet with your service account.
4) Redeploy.
5) Optional automation: schedule `streamlit run snapshot_log.py` daily (Render Cron / GH Actions).

## Output Columns
- date, revenue, gross_profit, net_profit, acos_pct
- asins, low_cover, suppressed, avg_stars
- alerts_total, alerts_crit, alerts_warn, alerts_info

You can later chart this Sheet for week‑over‑week trends or pull it back into the cockpit.
