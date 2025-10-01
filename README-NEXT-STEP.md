# Next Step: Wire Google Sheets (Products & PPC)

## 1) Service Account (Google Cloud)
- Create a Service Account and download JSON.
- Share each target Google Sheet with the service account email.

## 2) Add Secrets (Render → Environment)
- `gsheets_credentials` = paste the full JSON (as one line or TOML block).
- `gsheets_product_sheet_id` = the **file ID** of your Product Tracker sheet.
- `gsheets_ppc_sheet_id` = the **file ID** of your PPC sheet.

## 3) Requirements
Append to `requirements.txt`:
```
gspread>=6.0.0
google-auth>=2.30.0
```

## 4) Code changes
Replace `utils/data.py` with the version in this delta pack.

## 5) Sheet layout
Use the CSVs in `sheets_templates/` as your starting tabs.

## 6) Test locally
```
streamlit run app.py
```
Sidebar → Data Sources should now show ✓ for gspread and sheet IDs once secrets are set.
