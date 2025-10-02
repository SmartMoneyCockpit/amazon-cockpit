
import streamlit as st
import pandas as pd
from datetime import timedelta

from utils.layout import section_header
from utils.export import df_to_csv_bytes, df_to_xlsx_bytes, simple_pdf_bytes
from utils.ads_api import AdsClient, quick_test
from utils.ads_reports import fetch_sp_metrics
from utils.ppc_opt import guardrails, bid_rules, negatives, actions_to_df
from utils.alerts import Alert

def ppc_manager_view():
    section_header("📈 PPC Manager (Live Reports)")
    st.caption("Pulls SP metrics via Amazon Ads Reporting API v3 when credentials are set; falls back to sample otherwise.")

    # --- Live LWA Connection Test (Profiles & first profile's campaigns) ---
    try:
        with st.expander("🔌 Live Amazon Ads (LWA) Test"):
            t = quick_test()
            if t.get("ok"):
                st.success(t.get("message","Connected"))
                ads = AdsClient()
                prof_df = ads.get_profiles()
                st.write("**Profiles**")
                st.dataframe(prof_df, use_container_width=True)
                if not prof_df.empty and "profileId" in prof_df.columns:
                    pid = str(prof_df.iloc[0]["profileId"])
                    st.write(f"**Campaigns (profile {pid})**")
                    camp_df = ads.get_sp_campaigns(pid)
                    st.dataframe(camp_df, use_container_width=True)
            else:
                st.warning(t.get("message","Not connected; using sample metrics below."))
    except Exception as e:
        st.info(f"Live test not available: {e}")

    ads = AdsClient()

    # --- Metrics Table ---
    if ads.available():
        try:
            profs = ads.get_profiles()
            profile_id = str(profs.iloc[0]["profileId"]) if not profs.empty else None
        except Exception:
            profile_id = None

        try:
            if profile_id:
                end = pd.Timestamp.today().date()
                start = end - timedelta(days=13)
                df = fetch_sp_metrics(profile_id, start.isoformat(), end.isoformat())
            else:
                df = ads.get_sample_metrics()
        except Exception:
            df = ads.get_sample_metrics()
    else:
        df = AdsClient().get_sample_metrics()

    st.dataframe(df, use_container_width=True)

    # --- Export ---
    with st.expander("⬇️ Export Metrics"):
        c1, c2, c3 = st.columns(3)
        c1.download_button("CSV", df_to_csv_bytes(df), file_name="ppc_metrics.csv")
        c2.download_button("XLSX", df_to_xlsx_bytes(df), file_name="ppc_metrics.xlsx")
        c3.download_button("PDF", simple_pdf_bytes("PPC Metrics", df), file_name="ppc_metrics.pdf")

    # --- Optimizer (optional) ---
    try:
        g = guardrails(df)
        b = bid_rules(df)
        n = negatives(df)
        actions_df = actions_to_df(g, b, n)

        with st.expander("🧠 Optimizations"):
            st.dataframe(actions_df, use_container_width=True)
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
    except Exception as e:
        st.info(f"Optimizer skipped: {e}")
