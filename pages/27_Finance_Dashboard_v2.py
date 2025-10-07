
import datetime as dt
import pandas as pd
import streamlit as st
from infra.sheets_client import SheetsClient
from dataframes.finance import build_kpis
from utils.anomaly import detect_anomalies

st.set_page_config(page_title="Finance Dashboard v2", layout="wide")

st.title("Finance Dashboard v2")

_last_pull_utc = None

def _read_finances():
    global _last_pull_utc
    try:
        sc = SheetsClient()
        rows = sc.read_table("Finances")
        _last_pull_utc = dt.datetime.utcnow()
        return rows
    except Exception:
        _last_pull_utc = None
        return []

rows = _read_finances()
kpis, df = build_kpis(rows)

st.subheader("Filters")
today = dt.date.today()
default_start = (today - dt.timedelta(days=30))

c1, c2, c3 = st.columns([1.2, 1.2, 1])
with c1:
    start = st.date_input("Start date", value=default_start)
with c2:
    end = st.date_input("End date", value=today)
with c3:
    show_table = st.checkbox("Show raw table", value=False)

if not df.empty and "date" in df.columns:
    df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.date
    mask = (df["date"] >= start) & (df["date"] <= end)
    df_view = df.loc[mask].copy()
else:
    df_view = df.copy()

flags, df_annot = detect_anomalies(df_view, cols=["gmv","acos","tacos","refund_rate"], window=14, z_thresh=2.0)

def _pill(ok: bool, label: str):
    color = "#ef4444" if ok else "#16a34a"
    text = "Anomaly" if ok else "Normal"
    return f"<span style='padding:.15rem .5rem;border-radius:999px;background:{color};color:#fff;font-size:.75rem;'>{label}: {text}</span>"

st.markdown("### Anomaly Status (last point in range)", unsafe_allow_html=True)
p1, p2, p3, p4 = st.columns(4)
with p1: st.markdown(_pill(flags.get("gmv", False), "GMV"), unsafe_allow_html=True)
with p2: st.markdown(_pill(flags.get("acos", False), "ACoS"), unsafe_allow_html=True)
with p3: st.markdown(_pill(flags.get("tacos", False), "TACoS"), unsafe_allow_html=True)
with p4: st.markdown(_pill(flags.get("refund_rate", False), "Refund"), unsafe_allow_html=True)

gmv_sum = float(df_view.tail(30)["gmv"].sum()) if not df_view.empty and "gmv" in df_view.columns else 0.0
acos_last = float(df_view["acos"].iloc[-1]) if not df_view.empty and "acos" in df_view.columns else 0.0
tacos_last = float(df_view["tacos"].iloc[-1]) if not df_view.empty and "tacos" in df_view.columns else 0.0
refund_last = float(df_view["refund_rate"].iloc[-1]) if not df_view.empty and "refund_rate" in df_view.columns else 0.0

fresh_text = "—"
if _last_pull_utc is not None:
    fresh_text = _last_pull_utc.strftime("%Y-%m-%d %H:%M:%SZ UTC")

k1, k2, k3, k4, k5 = st.columns([1,1,1,1,2])
k1.metric("GMV (last 30 in view)", f"${gmv_sum:,.0f}")
k2.metric("ACoS (last in view)", f"{acos_last*100:.1f}%")
k3.metric("TACoS (last in view)", f"{tacos_last*100:.1f}%")
k4.metric("Refund Rate (last in view)", f"{refund_last*100:.2f}%")
with k5:
    st.caption(f"Last updated: {fresh_text}")

st.divider()
st.subheader("Time Series")
st.caption("If Google Sheets is not connected, demo data is shown for preview.")

if not df_view.empty and "date" in df_view.columns and "gmv" in df_view.columns:
    st.area_chart(df_view.set_index("date")[["gmv"]])
else:
    st.info("No finance data available yet for the selected range.")

if not df_annot.empty:
    st.divider()
    st.subheader("Anomaly Details (last 30 rows)")
    show_cols = []
    for c in ["gmv","acos","tacos","refund_rate"]:
        if c in df_annot.columns:
            show_cols += [c, f"{c}_z", f"{c}_anomaly"]
    with st.expander("Show anomaly table", expanded=False):
        st.dataframe(df_annot.tail(30)[["date"] + show_cols] if "date" in df_annot.columns else df_annot.tail(30)[show_cols],
                     use_container_width=True)

if show_table and not df_view.empty:
    with st.expander("Raw table (filtered)", expanded=False):
        st.dataframe(df_view.tail(200), use_container_width=True)
