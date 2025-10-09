
import streamlit as st, pandas as pd
from datetime import date, timedelta
from services.amazon_ads_service import list_sp_campaigns, list_sb_campaigns, list_sd_campaigns, list_all_campaigns, fetch_metrics

st.set_page_config(page_title="Amazon Ads – Vega", layout="wide")
st.title("Amazon Ads – Vega Cockpit (v7)")

tabs=st.tabs(["Lists","Metrics"])

with tabs[0]:
    st.subheader("SP/SB/SD Campaigns")
    try: st.dataframe(list_sp_campaigns(), use_container_width=True)
    except Exception as e: st.warning(e)
    try: st.dataframe(list_sb_campaigns(), use_container_width=True)
    except Exception as e: st.warning(e)
    try: st.dataframe(list_sd_campaigns(), use_container_width=True)
    except Exception as e: st.warning(e)
    st.subheader("Normalized")
    try: st.dataframe(pd.DataFrame(list_all_campaigns()), use_container_width=True)
    except Exception as e: st.warning(e)

with tabs[1]:
    today=date.today()
    c1,c2,c3=st.columns(3)
    if c1.button("Last 7d"): start=today-timedelta(days=6); end=today
    elif c2.button("Last 14d"): start=today-timedelta(days=13); end=today
    elif c3.button("Last 30d"): start=today-timedelta(days=29); end=today
    else: start=today-timedelta(days=6); end=today
    st.write(f"Window: {start} → {end}")
    if st.button("Fetch metrics"):
        rows=fetch_metrics(start,end,which=("SP","SB","SD"),persist=True)
        df=pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True)
        if not df.empty: st.download_button("⬇️ CSV", df.to_csv(index=False).encode("utf-8"), "amazon_ads_metrics.csv", "text/csv")
