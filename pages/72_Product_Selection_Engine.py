import streamlit as st
import pandas as pd
from utils.selection_engine import score_row, DEFAULT_WEIGHTS
from utils.jobs_history import write_job
from utils.digest_queue import add_summary

st.title("Product Selection Engine (CSV-first)")
st.caption("Upload candidates.csv, tune weights/filters, rank products, export, and queue summary to Daily Digest.")

tabs = st.tabs(["Upload & Preview","Scoring / Filters","Results & Export","Queue to Digest"])

with tabs[0]:
    st.subheader("Upload candidates.csv")
    f = st.file_uploader("candidates.csv", type=["csv"], key="selection_candidates")
    if f is None:
        st.download_button("Download template: candidates.csv", data=open("templates/candidates.csv","rb").read(), file_name="candidates.csv")
        df = None
    else:
        df = pd.read_csv(f)
        st.dataframe(df.head(50), use_container_width=True)

with tabs[1]:
    st.subheader("Weights & Minimum Criteria")
    cols = st.columns(3)
    w = dict(DEFAULT_WEIGHTS)
    # Simple editors
    w["gross_margin"] = cols[0].number_input("Weight: Gross margin", value=float(w["gross_margin"]), step=0.5)
    w["avg_star"]     = cols[1].number_input("Weight: Avg star", value=float(w["avg_star"]), step=0.5)
    w["return_rate"]  = cols[2].number_input("Weight: Return rate (penalty)", value=float(w["return_rate"]), step=0.5)
    cols2 = st.columns(3)
    w["keyword_rank"] = cols2[0].number_input("Weight: Keyword rank", value=float(w["keyword_rank"]), step=0.5)
    w["storage_cost_share"] = cols2[1].number_input("Weight: Storage share (penalty)", value=float(w["storage_cost_share"]), step=0.5)
    w["forecast_units"] = cols2[2].number_input("Weight: Forecast units", value=float(w["forecast_units"]), step=0.5)

    st.markdown("**Minimum thresholds (filters)**")
    c3 = st.columns(4)
    th_margin = c3[0].number_input("Min gross margin", value=0.20, step=0.05)
    th_star   = c3[1].number_input("Min avg star", value=4.0, step=0.1)
    th_rr     = c3[2].number_input("Max return rate (30d)", value=0.05, step=0.01)
    th_risk   = c3[3].selectbox("Policy risk allowed", options=["none only","allow high"], index=0)

with tabs[2]:
    st.subheader("Ranked Results")
    if 'df' in locals() and df is not None and len(df):
        rows = []
        for _,r in df.iterrows():
            score, parts = score_row(r.to_dict(), weights=w)
            gm = (float(r.get("target_price",0))-float(r.get("cost",0)))/float(r.get("target_price",1) or 1)
            risk = str(r.get("policy_risk","")).lower()
            if gm >= th_margin and float(r.get("avg_star",0)) >= th_star and float(r.get("return_rate_30d",1)) <= th_rr:
                if th_risk == "none only" and risk not in ("","none"): 
                    pass
                else:
                    rr = r.to_dict()
                    rr["_score"] = round(score,2)
                    rows.append(rr)
        if rows:
            out = pd.DataFrame(rows).sort_values("_score", ascending=False).reset_index(drop=True)
            st.dataframe(out, use_container_width=True, height=500)
            st.download_button("Download selected_products.csv", data=out.to_csv(index=False).encode("utf-8"), file_name="selected_products.csv")
            st.session_state["selection_results"] = out[["_score","asin","sku","title","category"]].to_dict(orient="records")
        else:
            st.info("No rows met the filters. Adjust thresholds or weights.")
    else:
        st.info("Upload candidates.csv first.")

with tabs[3]:
    st.subheader("Queue Summary to Daily Digest")
    try:
        rows = st.session_state.get("selection_results", [])
        if rows:
            if st.button("Queue top picks to Digest", type="primary"):
                p = add_summary("product_selection", "Product Selection — Top Picks", rows[:50])
                write_job("product_selection", "ok" if p else "error", {"queued_path": p})
                st.success(f"Queued: {p}")
        else:
            st.info("Generate results first on the previous tab.")
    except Exception as e:
        st.error(str(e))
