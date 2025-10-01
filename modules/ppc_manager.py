import streamlit as st
import pandas as pd
from datetime import date, timedelta

from utils.layout import section_header
from utils.export import df_to_csv_bytes, df_to_xlsx_bytes, simple_pdf_bytes
from utils.ads_api import AdsClient
from utils.ads_reports import fetch_sp_metrics
from utils.ppc_opt import guardrails, bid_rules, negatives, actions_to_df
from utils.alerts import Alert

def ppc_manager_view():
    section_header("📈 PPC Manager (Live Reports)")
    st.caption("Pulls SP metrics via Amazon Ads Reporting API v3 when credentials are set; falls back to sample otherwise.")

    ads = AdsClient()
    profiles = ads.get_profiles()
    if profiles.empty:
        st.error("No Ads profiles found. Check SP-API/LWA secrets.")
        return

    prof_options = {f"{r.get('countryCode','?')} · {r.get('profileId')}": str(r.get('profileId')) for _, r in profiles.iterrows()}
    sel_label = st.selectbox("Ads Profile", list(prof_options.keys()))
    profile_id = prof_options[sel_label]

    # Date range
    with st.expander("Date Range"):
        end = st.date_input("End Date", value=date.today())
        start = st.date_input("Start Date", value=end - timedelta(days=13))
    start_s = start.strftime("%Y-%m-%d")
    end_s = end.strftime("%Y-%m-%d")

    # Fetch live (or sample) metrics
    st.subheader("Performance")
    df = fetch_sp_metrics(profile_id, start_s, end_s)
    st.line_chart(df.set_index("Date")[["Impressions","Clicks","Orders"]])
    st.area_chart(df.set_index("Date")[["Spend"]])
    st.bar_chart(df.set_index("Date")[["ROAS"]])
    st.dataframe(df, use_container_width=True)
    c = st.columns(3)
    c[0].metric("Avg ACoS", f"{df['ACoS%'].mean():.1f}%")
    c[1].metric("Avg ROAS", f"{df['ROAS'].mean():.2f}")
    c[2].metric("Spend (Period)", f"${df['Spend'].sum():,.0f}")

    with st.expander("⬇️ Export Metrics"):
        c1, c2, c3 = st.columns(3)
        c1.download_button("CSV", df_to_csv_bytes(df), file_name="ppc_metrics.csv")
        c2.download_button("XLSX", df_to_xlsx_bytes(df), file_name="ppc_metrics.xlsx")
        c3.download_button("PDF", simple_pdf_bytes("PPC Metrics", df), file_name="ppc_metrics.pdf")

    # Optimizer
    st.divider()
    st.subheader("Optimizer")
    with st.expander("Settings"):
        c1, c2, c3, c4 = st.columns(4)
        acos_target = c1.number_input("ACoS Target %", value=30.0, min_value=1.0, max_value=100.0, step=0.5)
        min_conv = c2.number_input("Min Orders for Budget Raise", value=5, min_value=0, max_value=100, step=1)
        min_clicks = c3.number_input("Min Clicks (Bid Rules)", value=20, min_value=0, max_value=1000, step=1)
        ctr_floor = c4.number_input("CTR Floor (negatives)", value=0.10, min_value=0.0, max_value=1.0, step=0.01, format="%.2f")

    g_actions = guardrails(df, acos_target=acos_target, min_conv=int(min_conv))
    b_actions = bid_rules(df.assign(Keyword="(kw)"), acos_target=acos_target, min_clicks=int(min_clicks))
    n_actions = negatives(df.assign(Keyword="(kw)"), ctr_floor=float(ctr_floor))
    actions_df = pd.concat([
        actions_to_df(g_actions),
        actions_to_df(b_actions),
        actions_to_df(n_actions)
    ], ignore_index=True)

    if actions_df.empty:
        st.success("No optimization actions suggested by current settings.")
    else:
        st.dataframe(actions_df, use_container_width=True)
        with st.expander("⬇️ Export Suggestions"):
            c1, c2, c3 = st.columns(3)
            c1.download_button("CSV", df_to_csv_bytes(actions_df), file_name="ppc_actions.csv")
            c2.download_button("XLSX", df_to_xlsx_bytes(actions_df), file_name="ppc_actions.xlsx")
            c3.download_button("PDF", simple_pdf_bytes("PPC Optimizations", actions_df), file_name="ppc_actions.pdf")

        crit = actions_df[actions_df["action"] == "Pause"]
        warn = actions_df[actions_df["action"].isin(["Cut Budget","Lower Bid"])]
        buf = []
        for _, r in crit.iterrows():
            buf.append(Alert("crit", f"PPC: Pause keyword '{r['target']}' ({r.get('campaign','')})", "PPC").__dict__)
        for _, r in warn.iterrows():
            buf.append(Alert("warn", f"PPC: {r['action']} on '{r['target']}'", "PPC").__dict__)
        if buf:
            st.warning(f"{len(buf)} PPC optimization alert(s) — see Alerts Hub.")
            st.session_state.setdefault("alerts_buffer", [])
            st.session_state["alerts_buffer"].extend(buf)
