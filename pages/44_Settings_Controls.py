
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Settings Controls", layout="wide")
st.title("⚙️ Settings Controls")

st.caption("Edit critical thresholds and planning parameters directly, then write them to the Google Sheet tab **alerts_settings**.")

# Try Sheets bridge
HAVE_SB = True
try:
    from utils import sheets_bridge as SB  # expected: read_tab(name), write_tab(name, df)
except Exception:
    HAVE_SB = False
    SB = None

def load_alerts_settings() -> pd.DataFrame:
    if HAVE_SB:
        try:
            df = SB.read_tab("alerts_settings")
            if isinstance(df, pd.DataFrame):
                df.columns = [c.strip().lower() for c in df.columns]
                return df
        except Exception:
            pass
    return pd.DataFrame(columns=[
        "doc_days_low","compliance_due_days","ppc_min_spend","ppc_min_clicks",
        "net_margin_min_pct","gross_margin_min_pct",
        "net_margin_min_pct_critical","gross_margin_min_pct_critical",
        "ppc_surge_spend_critical","ppc_surge_clicks_critical","lookback_days_ppc_critical",
        "lead_time_days","safety_stock_days","moq_units"
    ])

def write_alerts_settings(df: pd.DataFrame) -> str:
    if HAVE_SB and hasattr(SB, "write_tab"):
        try:
            SB.write_tab("alerts_settings", df, clear=True)
            return f"sheet:alerts_settings:{len(df)}"
        except Exception as e:
            return f"error:{e}"
    return "no_sheets_bridge"

# Load current
df = load_alerts_settings()
row = df.iloc[0].to_dict() if not df.empty else {}

st.sidebar.header("Save / Load")
if st.sidebar.button("Reload from Sheet"):
    st.experimental_rerun()

st.subheader("Alerts — Baseline thresholds")
c1, c2, c3, c4 = st.columns(4)
doc_days_low = c1.number_input("Low DoC threshold (days)", 1, 365, int(row.get("doc_days_low", 10)))
comp_days   = c2.number_input("Compliance due (days)", 1, 365, int(row.get("compliance_due_days", 30)))
ppc_min_sp  = c3.number_input("PPC min spend ($)", 0.0, 10000.0, float(row.get("ppc_min_spend", 10.0)), 0.5)
ppc_min_clk = c4.number_input("PPC min clicks (0 orders)", 0, 100000, int(row.get("ppc_min_clicks", 12)), 1)

st.subheader("Alerts — Margin thresholds")
c5, c6 = st.columns(2)
net_min   = c5.number_input("Net margin min % (yellow/red band)", -100.0, 100.0, float(row.get("net_margin_min_pct", 0.0)), 0.5)
gross_min = c6.number_input("Gross margin min % (yellow/red band)", -100.0, 100.0, float(row.get("gross_margin_min_pct", 15.0)), 0.5)

st.subheader("Revenue Protection — Critical rules")
c7, c8, c9 = st.columns(3)
net_crit   = c7.number_input("Net margin CRITICAL % (trigger)", -100.0, 100.0, float(row.get("net_margin_min_pct_critical", 0.0)), 0.5)
gross_crit = c8.number_input("Gross margin CRITICAL % (trigger)", -100.0, 100.0, float(row.get("gross_margin_min_pct_critical", 10.0)), 0.5)
ppc_days   = c9.number_input("PPC lookback (days)", 1, 90, int(row.get("lookback_days_ppc_critical", 7)), 1)

c10, c11 = st.columns(2)
ppc_spend_crit = c10.number_input("PPC spend CRITICAL ($)", 0.0, 100000.0, float(row.get("ppc_surge_spend_critical", 25.0)), 0.5)
ppc_clicks_crit = c11.number_input("PPC clicks CRITICAL", 0, 100000, int(row.get("ppc_surge_clicks_critical", 20)), 1)

st.subheader("Reorder Forecast — Planning")
c12, c13, c14 = st.columns(3)
lead_time = c12.number_input("Lead time (days)", 1, 365, int(row.get("lead_time_days", 21)), 1)
safety_stock = c13.number_input("Safety stock (days)", 0, 120, int(row.get("safety_stock_days", 7)), 1)
moq = c14.number_input("MOQ (units)", 0, 1000000, int(row.get("moq_units", 0)), 1)

st.divider()
st.subheader("Preview JSON")
preview = pd.DataFrame([{
    "doc_days_low": doc_days_low,
    "compliance_due_days": comp_days,
    "ppc_min_spend": ppc_min_sp,
    "ppc_min_clicks": ppc_min_clk,
    "net_margin_min_pct": net_min,
    "gross_margin_min_pct": gross_min,
    "net_margin_min_pct_critical": net_crit,
    "gross_margin_min_pct_critical": gross_crit,
    "ppc_surge_spend_critical": ppc_spend_crit,
    "ppc_surge_clicks_critical": ppc_clicks_crit,
    "lookback_days_ppc_critical": ppc_days,
    "lead_time_days": lead_time,
    "safety_stock_days": safety_stock,
    "moq_units": moq,
}])
st.dataframe(preview, use_container_width=True, hide_index=True)

cA, cB = st.columns(2)
if cA.button("💾 Write to Sheet (alerts_settings)"):
    res = write_alerts_settings(preview)
    if res.startswith("sheet:"):
        st.success(f"Saved: {res}")
    else:
        st.error(res)

st.caption("If Google Sheets isn't connected, you can copy the preview and paste into your `alerts_settings` tab manually.")
