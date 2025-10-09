import streamlit as st
from services.amazon_ads_service import get_profiles, list_sp_campaigns

st.title("Amazon Ads – Vega Cockpit")

with st.spinner("Loading profiles..."):
    profiles = get_profiles()
st.subheader("Profiles")
st.json(profiles)

with st.spinner("Loading SP campaigns..."):
    campaigns = list_sp_campaigns()
st.subheader("Sponsored Products – Campaigns")
st.dataframe(campaigns)
