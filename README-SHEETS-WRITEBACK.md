# Next Step: Google Sheets Write‑Back — PPC Changes Log (Append Rows)

This pack adds a tiny helper to **append** your PPC Changes Log to a Google Sheet.

## Files
- `utils/gsheets_write.py` → generic write‑back utility using gspread
- `modules_ppc_manager_writeback_snippet.py` → a small snippet to drop into `ppc_manager.py`

## Prereqs
- You already installed (from earlier steps):
```
gspread>=6.0.0
google-auth>=2.30.0
```
- Your `gsheets_credentials` secret (service account JSON) is set.

## Setup
1) Copy `utils/gsheets_write.py` into your project.
2) In `modules/ppc_manager.py`, paste the snippet from `modules_ppc_manager_writeback_snippet.py`
   **after** you compute `actions_df` and show exports.
3) Add a secret with your **target Sheet file ID**:
   - `gsheets_changes_log_sheet_id` = the Google Sheet **file ID** where logs should be stored.
   - The service account must have edit access to this Sheet.
4) Redeploy.

## Use
- In the PPC tab, you’ll see **“Changes Log → Google Sheets”**.
- Pick a worksheet name (default `ppc_changes_log`) and click **Append to Google Sheet**.
- The helper creates the worksheet if missing and writes headers if empty.

## Notes
- The helper is generic; reuse it for other write‑backs later (e.g., Alerts history, Compliance index updates).
- For error‑tolerant batch jobs, we can offload write‑backs to a server workflow and queue retries silently.
