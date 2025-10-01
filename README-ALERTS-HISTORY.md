# Next Step: Alerts History Archiving

Archive your cockpit alerts to **Google Sheets** and generate a **daily PDF snapshot** from the Alerts Hub.

## What this adds
- Export **CSV/XLSX/PDF** of the latest N alerts (default 500).
- Append alerts to a Google Sheet (append‑only), worksheet auto‑created if missing.

## Files
- `utils/alerts_archive.py` → helpers to format alerts buffer, export files, and write to Sheets.
- `modules_alerts_hub_snippet.py` → UI snippet to paste into `alerts_hub_view()`.

## Prereqs
- From earlier steps:
  - `utils/gsheets_write.py`
  - `utils/export.py`
  - Google Sheets service account in secrets.
- Secret:
  - `gsheets_alerts_history_sheet_id` = target Google Sheet **file ID**

## How to apply
1) Copy `utils/alerts_archive.py` into your project.
2) Open `modules/alerts_hub.py`, and **after** you render the alerts dataframe, paste the snippet from `modules_alerts_hub_snippet.py`.
3) Add the secret `gsheets_alerts_history_sheet_id` and share the sheet with the service account.
4) Redeploy. In Alerts Hub you’ll see **Archive Alerts** with download buttons and **Append Now** to Sheets.

## Tips
- For auto‑archiving (daily at a set time), we can add a server workflow on Render to hit a `/snapshot` endpoint; for now this is a one‑click UI.
