# Amazon Cockpit (Baseline)

This is a minimal, deployable Streamlit app that mirrors the Vega style, with six baseline modules:
1) Product Tracker
2) PPC Manager
3) A+ & SEO Panel
4) Compliance Vault
5) Finance Dashboard
6) Alerts Hub

## Quick Start

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Secrets (optional)

Create `.streamlit/secrets.toml` or Render env vars for future integrations:

```toml
# Example placeholders
env = "staging"
sp_api_client_id = ""
sp_api_client_secret = ""
sp_api_refresh_token = ""
sp_api_role_arn = ""
gsheets_credentials = ""         # JSON string or path when implemented
gsheets_product_sheet_id = ""
gsheets_ppc_sheet_id = ""
```

## Roadmap hooks

- Replace sample data with SP‑API / Google Sheets ingestion.
- Add rules engine & alert notifications.
- Add PDF/Sheets one‑click export.
- Add team‑scoped views (ROI Renegades, Joanne, Faith).
```
