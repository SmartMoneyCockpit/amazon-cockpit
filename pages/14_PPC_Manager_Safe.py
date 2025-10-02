
import streamlit as st
import pandas as pd
from utils.ads_config import CONFIG

st.set_page_config(page_title="PPC Manager (Safe)", layout="wide")
st.title("📊 PPC Manager (Safe Mode)")

if not CONFIG["enabled"]:
    st.info("Amazon Ads API is **disabled** (ADS_ENABLED=false). Showing sample data only. Enable when Amazon Ads access is approved and a refresh token with advertising scopes is set.")
else:
    st.warning("Ads API enabled, but this Safe page still uses sample data until credentials are validated. Use the original Live Reports page after approval.")

# Simple sample table for visual continuity
data = pd.DataFrame([
    {"Date":"2025-09-23 20:34:05","Campaign":"Auto","Impressions":10900,"Clicks":295,"Spend":95,"Orders":24,"ACoS%":40,"ROAS":2.5},
    {"Date":"2025-09-24 20:34:05","Campaign":"Auto","Impressions":13200,"Clicks":345,"Spend":98,"Orders":28,"ACoS%":41,"ROAS":2.4},
    {"Date":"2025-09-25 20:34:05","Campaign":"Exact","Impressions":12800,"Clicks":330,"Spend":93,"Orders":27,"ACoS%":42,"ROAS":2.4},
    {"Date":"2025-09-26 20:34:05","Campaign":"Exact","Impressions":15000,"Clicks":400,"Spend":101,"Orders":36,"ACoS%":33,"ROAS":3.0},
])
st.dataframe(data, use_container_width=True, hide_index=True)

st.caption("To enable live Ads data later set ADS_ENABLED=true and add ADS_LWA_CLIENT_ID / ADS_LWA_CLIENT_SECRET / ADS_REFRESH_TOKEN / ADS_PROFILE_ID. Your app must be approved for Amazon Advertising API.")
