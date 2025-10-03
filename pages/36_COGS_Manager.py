import streamlit as st
import pandas as pd
from utils.auth import gate
import utils.security as sec

st.set_page_config(page_title="COGS Manager", layout="wide")
sec.enforce()
if not gate(required_admin=False):
    st.stop()

st.title("🧮 COGS Manager")
st.caption("Edit your `cogs_map` (sku,cogs_per_unit). Used for gross margin and alerts.")

try:
    from utils import sheets_bridge as SB
    HAVE_SB = True
except Exception:
    HAVE_SB = False
    SB = None

def read_tab(name: str) -> pd.DataFrame:
    if HAVE_SB:
        try:
            df = SB.read_tab(name)
            if isinstance(df, pd.DataFrame):
                df.columns = [c.strip().lower() for c in df.columns]
                return df
        except Exception:
            pass
    return pd.DataFrame()

def write_tab(name: str, df: pd.DataFrame, clear=True) -> str:
    if HAVE_SB and hasattr(SB, "write_tab"):
        try:
            SB.write_tab(name, df, clear=clear)
            return f"sheet:{name}:{len(df)}"
        except Exception as e:
            return f"error:{e}"
    return "no_sheets_bridge"

inv = read_tab("inventory")
skus = sorted(inv["sku"].dropna().astype(str).unique().tolist()) if not inv.empty and "sku" in inv.columns else []
cogs = read_tab("cogs_map")
if cogs.empty:
    cogs = pd.DataFrame({"sku": skus, "cogs_per_unit": [None]*len(skus)})
else:
    cogs = cogs.groupby("sku", as_index=False).agg(cogs_per_unit=("cogs_per_unit","first"))

st.subheader("Edit COGS")
edited = st.data_editor(cogs, num_rows="dynamic", use_container_width=True)

colA, colB = st.columns(2)
if colA.button("💾 Save to Sheet (cogs_map)"):
    st.success(write_tab("cogs_map", edited))

st.subheader("Margin Breach Preview")
from utils.margins_guard import margin_breaches
nm = st.number_input("Net margin minimum %", -100.0, 100.0, 0.0, 0.5)
gm = st.number_input("Gross margin minimum %", -100.0, 100.0, 15.0, 0.5)
breaches = margin_breaches(net_margin_pct_thresh=nm, gross_margin_pct_thresh=gm)
if breaches.empty:
    st.info("No margin breaches at current thresholds.")
else:
    st.dataframe(breaches, use_container_width=True, hide_index=True)
