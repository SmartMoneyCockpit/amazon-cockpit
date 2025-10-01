# Next Step: A+ & SEO Scanner

### What this adds
- **Keyword Indexing**: tracks indexing and rank per ASIN/keyword; flags **high‑priority deindexed** terms and sends Alerts (crit).
- **Competitor Snapshot**: lightweight table for price/stars/reviews and A+ presence.

### Google Sheets (optional)
Add these secrets and create worksheets named exactly as below:
- `gsheets_keywords_sheet_id` → worksheet **keywords**
- `gsheets_competitors_sheet_id` → worksheet **competitors**

Use the templates in `sheets_templates/` to seed your Sheets.

### How to apply
1. Copy `utils/seo.py` into your project.
2. Replace the contents of `modules/a_plus_seo.py` with `modules_a_plus_seo.py` from this pack.
3. (Optional) Set the two Sheet IDs in secrets and share with your service account.
4. Redeploy.

### Notes
- Exports use the `utils/export.py` added in a prior step.
- Later we can add live on‑page audits and automated competitor pulls.
