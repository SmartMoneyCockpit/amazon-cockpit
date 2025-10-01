import streamlit as st
import pandas as pd
from utils.layout import section_header
from utils.export import df_to_csv_bytes, df_to_xlsx_bytes, simple_pdf_bytes
from utils.ads_api import AdsClient
from utils.ppc_opt import guardrails, bid_rules, negatives, actions_to_df
from utils.alerts import Alert

def ppc_manager_view():
    section_header("📈 PPC Manager (Live Ads Starter)")
    st.caption("Lists live Ads profiles & SP campaigns via Amazon Advertising API (LWA). Metrics/charts use sample data until reporting is added.")

    ads = AdsClient()
    profiles = ads.get_profiles()
    if profiles.empty:
        st.error("No Ads profiles found. Check SP-API/LWA secrets.")
        return

    # Profile selector
    prof_options = {f"{r.get('countryCode','?')} · {r.get('profileId')}": str(r.get('profileId')) for _, r in profiles.iterrows()}
    sel_label = st.selectbox("Ads Profile", list(prof_options.keys()))
    profile_id = prof_options[sel_label]

    # Campaigns
    camps = ads.get_sp_campaigns(profile_id)
    st.subheader("Sponsored Products Campaigns (basic fields)")
    st.dataframe(camps, use_container_width=True)

    # Charts & metrics (sample for now)
    st.divider()
    st.subheader("14‑Day Performance (sample metrics; reporting to be added)")
    sdf = ads.get_sample_metrics()
    st.line_chart(sdf.set_index("Date")[["Impressions","Clicks","Orders"]])
    st.area_chart(sdf.set_index("Date")[["Spend"]])
    st.bar_chart(sdf.set_index("Date")[["ROAS"]])
    st.dataframe(sdf, use_container_width=True)
    c = st.columns(3)
    c[0].metric("Avg ACoS", f"{sdf['ACoS%'].mean():.1f}%")
    c[1].metric("Avg ROAS", f"{sdf['ROAS'].mean():.2f}")
    c[2].metric("Spend (14d)", f"${sdf['Spend'].sum():,.0f}")

    with st.expander("⬇️ Export (sample metrics)"):
        c1, c2, c3 = st.columns(3)
        c1.download_button("CSV", df_to_csv_bytes(sdf), file_name="ppc_sample_metrics.csv")
        c2.download_button("XLSX", df_to_xlsx_bytes(sdf), file_name="ppc_sample_metrics.xlsx")
        c3.download_button("PDF", simple_pdf_bytes("PPC Sample Metrics", sdf), file_name="ppc_sample_metrics.pdf")

    # Optimizer works off the current dataframe (sample for now)
    st.divider()
    st.subheader("Optimizer")
    with st.expander("Settings"):
        c1, c2, c3, c4 = st.columns(4)
        acos_target = c1.number_input("ACoS Target %", value=30.0, min_value=1.0, max_value=100.0, step=0.5)
        min_conv = c2.number_input("Min Orders for Budget Raise", value=5, min_value=0, max_value=100, step=1)
        min_clicks = c3.number_input("Min Clicks (Bid Rules)", value=20, min_value=0, max_value=1000, step=1)
        ctr_floor = c4.number_input("CTR Floor (negatives)", value=0.10, min_value=0.0, max_value=1.0, step=0.01, format="%.2f")

    g_actions = guardrails(sdf, acos_target=acos_target, min_conv=int(min_conv))
    b_actions = bid_rules(sdf.assign(Keyword="(kw)"), acos_target=acos_target, min_clicks=int(min_clicks))
    n_actions = negatives(sdf.assign(Keyword="(kw)"), ctr_floor=float(ctr_floor))
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
