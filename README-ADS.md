# Next Step: Amazon Ads (SP-API) — Starter Integration

This pack wires **Login With Amazon (LWA)** → **Amazon Advertising API** so your PPC tab lists
**Profiles** and **Sponsored Products Campaigns** live. Charts/optimizer still use sample metrics
until we add the v3 **Reporting API**.

## Apply Steps
1) Copy `utils/ads_api.py` into your project.
2) Replace `modules/ppc_manager.py` with the one in this pack.
3) Add environment secrets (Render → Environment or `.streamlit/secrets.toml`):
```toml
sp_api_client_id = "amzn1.application-oa2-client.xxx"
sp_api_client_secret = "xxxxx"
sp_api_refresh_token = "Atzr|IwEBI..."
# sp_api_role_arn is not used directly here; needed for SP-API data but not Ads LWA
```
4) Ensure your token has Advertising scopes (e.g., `advertising::campaign_management`).
5) Redeploy. In the PPC tab select a profile to load campaigns.

## Requirements
Append these to your `requirements.txt` if not present:
```
requests>=2.32.0
tenacity>=8.2.0
```

## Notes
- Region base defaults to **NA** (`https://advertising-api.amazon.com`). For EU/FE we can expose a selector.
- For **metrics** (impr/clicks/spend/orders, ACOS/ROAS), we'll add Reporting API next:
  - Create a report (`POST /v3/reports`), poll status, download file, load into DataFrame.
  - Then we swap the charts/optimizer to use live report data.
