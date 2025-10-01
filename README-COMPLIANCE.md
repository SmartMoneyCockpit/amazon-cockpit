# Next Step: Compliance Vault — Uploader + Expiry Reminders

### What this adds
- **Compliance Index** view (reads Google Sheet `index` tab if `gsheets_compliance_sheet_id` is set; otherwise uses sample).
- **KPIs** for expired / due ≤30 / 31–60 / 61–90 days.
- **Form Uploader** to stage new/updated rows in-session and export the **merged index** (CSV/XLSX/PDF).
- **Alerts** pushed to the Alerts Hub for expired/soon‑to‑expire docs.

### How to apply
1. Copy `utils/compliance.py` into your project.
2. Replace the contents of `modules/compliance_vault.py` with `modules_compliance_vault.py` from this pack.
3. (Optional) Set secret `gsheets_compliance_sheet_id` to point to your Google Sheet (must have a worksheet named `index`).
4. Use `sheets_templates/compliance_index_template.csv` as your starter layout.
5. Redeploy.

### Notes
- Render file system is ephemeral; the uploader **stages in memory** and lets you export an updated index that you can upload to your master Sheet.
- For full write‑back to Google Sheets, we can add a write API in a later step.
