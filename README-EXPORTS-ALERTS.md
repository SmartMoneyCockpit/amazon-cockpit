# Next Step: One‑Click Exports + Basic Alerts

## Files in this delta
- `utils/export.py` → CSV, XLSX, and PDF (ReportLab) exporters.
- `utils/alerts.py` → simple rules for Product/PPC alerts.
- `modules/*_patch.py` → updated views showing how to add Export buttons + push alerts into session.
  - Apply these changes into your existing module files.

## Install
Append to your `requirements.txt`:
```
reportlab>=4.2.0
XlsxWriter>=3.2.0
```

## How to apply
1. Copy `utils/export.py` and `utils/alerts.py` into your project.
2. Merge the contents of:
   - `modules_product_tracker.py` → into `modules/product_tracker.py`
   - `modules_ppc_manager.py` → into `modules/ppc_manager.py`
   - `modules_alerts_hub.py` → into `modules/alerts_hub.py`
3. Redeploy. You’ll see **Export** expanders and the **Alerts Hub** filling when rules trigger.

## Notes
- PDF export returns a simple tabular PDF; for branded layouts we can add headers/footers/logo next.
- Alerts buffer is in `st.session_state["alerts_buffer"]`; a future step can persist to Sheets/DB.
