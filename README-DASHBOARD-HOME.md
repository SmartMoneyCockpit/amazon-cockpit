# Next Step: Dashboard Home

Adds a **Home** tab with:
- **Top KPIs** (Revenue, GP, Net, ACoS) from Finance
- **Product health** (ASINs tracked, low days of cover, suppressed, avg stars)
- **Alerts summary** (counts and latest 50)
- **Integration Health** (secrets/IDs presence)
- **Quick Links** to each module

## Apply
1) Copy `modules/home.py` and `utils/health.py` into your project.
2) Replace your `app.py` with the one in this pack (adds the new "Home" tab).
3) Redeploy.

Notes:
- Alerts rollup reads `st.session_state['alerts_buffer']`. Visit modules to populate it.
- Integration health only checks presence of secrets/IDs; it doesn't call external APIs here.
