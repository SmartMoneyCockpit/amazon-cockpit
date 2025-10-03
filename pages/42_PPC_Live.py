
import os
import datetime as dt
import streamlit as st
from utils.auth import gate
import utils.security as sec
from utils.ads_live import have_creds, list_campaigns, list_adgroups, request_campaign_report, get_report_status, download_report

st.set_page_config(page_title="PPC Live (Ads API)", layout="wide")
sec.enforce()
if not gate(required_admin=False):
    st.stop()

st.title("📡 PPC Live — Amazon Ads API")
st.caption("Reads live campaigns/ad groups and lets you request & download reports. Safe fallbacks if creds are missing.")

# Creds check
if not have_creds():
    st.warning("Set ADS_LWA_CLIENT_ID / ADS_LWA_CLIENT_SECRET / ADS_REFRESH_TOKEN / ADS_PROFILE_ID in Render → Environment to enable live Ads.")
    st.stop()

tab1, tab2, tab3 = st.tabs(["Campaigns", "Ad groups", "Reports"])

with tab1:
    st.subheader("Sponsored Products Campaigns")
    state = st.selectbox("State filter", ["enabled","paused","archived","enabled,paused"], index=0)
    st.caption("Note: This uses v2 campaigns API. Availability varies by region.")
    s, data = list_campaigns(state_filter=state)
    if s != "ok":
        st.error(f"Error: {data}")
    else:
        if not data:
            st.info("No campaigns returned.")
        else:
            st.dataframe(data, use_container_width=True, hide_index=True)

with tab2:
    st.subheader("Ad Groups (pick a campaignId)")
    camp_id = st.text_input("campaignId", "")
    if camp_id:
        try:
            cid = int(camp_id)
            s, data = list_adgroups(cid)
            if s != "ok":
                st.error(f"Error: {data}")
            else:
                st.dataframe(data, use_container_width=True, hide_index=True)
        except ValueError:
            st.error("campaignId must be an integer.")

with tab3:
    st.subheader("Reports — Campaign metrics (yesterday)")
    yday = (dt.datetime.utcnow() - dt.timedelta(days=1)).strftime("%Y%m%d")
    report_date = st.text_input("reportDate (YYYYMMDD)", yday)
    colA, colB, colC = st.columns(3)
    if colA.button("Request report"):
        s, rid = request_campaign_report(report_date)
        if s == "ok":
            st.success(f"Requested. reportId={rid}")
            st.session_state["ads_report_id"] = rid
        else:
            st.error(rid)
    rid = st.session_state.get("ads_report_id", "")
    colB.write(f"Current reportId: {rid or '—'}")
    if colB.button("Check status") and rid:
        s, meta = get_report_status(rid)
        st.json(meta if s=="ok" else {"error": meta})
    if colC.button("Download") and rid:
        s, path = download_report(rid)
        if s == "ok":
            st.success(f"Downloaded: {path}")
            with open(path, "rb") as f:
                st.download_button("⬇️ Download CSV", f, file_name=os.path.basename(path), mime="text/csv")
        else:
            st.error(path)
