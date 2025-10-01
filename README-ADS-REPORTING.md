# Next Step: Amazon Ads Reporting API (v3) — Live Metrics

This step adds **reporting** so the PPC tab uses **live impressions/clicks/spend/orders** and computes **ACOS/ROAS**.

## Apply
1) Copy `utils/ads_reports.py` into your project.
2) Replace your `modules/ppc_manager.py` with the one from this pack.
3) Ensure you already installed earlier requirements:
```
requests>=2.32.0
tenacity>=8.2.0
```
4) Deploy. In the PPC tab:
   - Select an **Ads profile**
   - Pick a **date range**
   - The app will create → poll → download a Sponsored Products report and render charts/tables.
   - On any API error, it **falls back to sample metrics** automatically.

## Notes
- Report definition uses `reportTypeId: spCampaigns`, columns: date, campaignName, impressions, clicks, cost, conversions (14d), sales (14d).
- If your account is EU/FE, we can expose a region base switch (ads API host) in a follow-up.
- For heavier usage, consider server‑side polling to avoid UI waits; we can offload via a background job in Render if desired.
