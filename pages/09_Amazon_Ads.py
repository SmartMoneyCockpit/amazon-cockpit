import streamlit as st
import pandas as pd
from datetime import date, timedelta

from services.amazon_ads_service import (
    get_profiles, list_sp_campaigns, list_sb_campaigns, list_sd_campaigns,
    list_all_campaigns, fetch_metrics
)

st.set_page_config(page_title="Amazon Ads – Vega", layout="wide")
st.title("Amazon Ads – Vega Cockpit")

tabs = st.tabs(["Campaign Lists", "Metrics (Reporting)"])

# -------------------- Campaign Lists --------------------
with tabs[0]:
    st.caption("Live lists from Ads API (archived excluded by default).")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("SP campaigns")
        try:
            sp = list_sp_campaigns(count=1000)
            st.dataframe(sp, use_container_width=True, height=350)
        except Exception as e:
            st.warning(f"SP list error: {e}")

    with col2:
        st.subheader("SB campaigns")
        try:
            sb = list_sb_campaigns()
            st.dataframe(sb, use_container_width=True, height=350)
        except Exception as e:
            st.warning(f"SB list error: {e}")

    with col3:
        st.subheader("SD campaigns")
        try:
            sd = list_sd_campaigns(count=1000)
            st.dataframe(sd, use_container_width=True, height=350)
        except Exception as e:
            st.warning(f"SD list error: {e}")

    st.subheader("All campaigns (normalized)")
    try:
        rows = list_all_campaigns()
        df_all = pd.DataFrame(rows)
        st.dataframe(df_all, use_container_width=True, height=420)
    except Exception as e:
        st.error(f"Failed to render combined table: {e}")

# -------------------- Metrics (Reporting) --------------------
with tabs[1]:
    st.caption("Create + poll Amazon Ads reports for the window you pick.")

    today = date.today()
    c1,c2,c3,c4 = st.columns(4)
    if "metrics_range" not in st.session_state:
        st.session_state["metrics_range"] = (today - timedelta(days=6), today)

    def pick(days):
        start = today - timedelta(days=days-1)
        st.session_state["metrics_range"] = (start, today)
        st.experimental_rerun()

    if c1.button("Last 7d"):  pick(7)
    if c2.button("Last 14d"): pick(14)
    if c3.button("Last 30d"): pick(30)

    start_default, end_default = st.session_state["metrics_range"]
    rng = st.date_input("Date range", (start_default, end_default))
    if isinstance(rng, tuple) and len(rng) == 2:
        start_date, end_date = rng
    else:
        start_date, end_date = start_default, end_default

    st.write(f"Selected: **{start_date} → {end_date}**")

    ad_types = st.multiselect("Ad products", ["SP","SB","SD"], default=["SP","SB","SD"])

    if st.button("Fetch metrics"):
        with st.spinner("Building and downloading reports..."):
            try:
                rows = fetch_metrics(start_date, end_date, which=ad_types, persist=True)
                df = pd.DataFrame(rows)
                if df.empty:
                    st.info("No rows returned for this window.")
                else:
                    # normalize numerics
                    for col in ["impressions","clicks","cost","sales14d","purchases14d"]:
                        if col in df.columns: df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

                    total_imp = int(df.get("impressions", pd.Series([0])).sum())
                    total_clk = int(df.get("clicks", pd.Series([0])).sum())
                    total_cost = float(df.get("cost", pd.Series([0])).sum())
                    total_sales = float(df.get("sales14d", pd.Series([0])).sum())

                    k1,k2,k3,k4,k5,k6 = st.columns(6)
                    k1.metric("Impressions", f"{total_imp:,}")
                    k2.metric("Clicks", f"{total_clk:,}")
                    k3.metric("Cost", f"${total_cost:,.2f}")
                    k4.metric("Sales (14d)", f"${total_sales:,.2f}")
                    roas = (total_sales/total_cost) if total_cost>0 else None
                    k5.metric("RoAS", f"{roas:,.2f}×" if roas is not None else "—")
                    cpc = (total_cost/total_clk) if total_clk>0 else None
                    k6.metric("CPC", f"${cpc:,.2f}" if cpc is not None else "—")

                    # Derived ratios per row
                    def safe_div(a,b): 
                        try: 
                            return a/b if b else None
                        except Exception: 
                            return None
                    if "clicks" in df and "impressions" in df:
                        df["CTR"] = df.apply(lambda r: safe_div(r.get("clicks"), r.get("impressions")), axis=1)
                    if "purchases14d" in df and "clicks" in df:
                        df["CVR"] = df.apply(lambda r: safe_div(r.get("purchases14d"), r.get("clicks")), axis=1)
                    if "cost" in df and "sales14d" in df:
                        df["ACOS"] = df.apply(lambda r: safe_div(r.get("cost"), r.get("sales14d")), axis=1)
                        df["ROAS"] = df.apply(lambda r: safe_div(r.get("sales14d"), r.get("cost")), axis=1)
                        # TACOS uses total revenue; until SP-API integration, treat totalRevenue≈sales14d
                        df["TACOS"] = df["ACOS"]

                    st.dataframe(df, use_container_width=True, height=520)

                    st.download_button("⬇️ Download metrics CSV", data=df.to_csv(index=False).encode("utf-8"),
                                       file_name="amazon_ads_metrics.csv", mime="text/csv")
            except Exception as e:
                st.error(f"Reporting failed: {e}")
                st.info("If your account expects different media types/columns, tweak services.amazon_ads_service.fetch_metrics.")