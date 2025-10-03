
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Finance Heatmap", layout="wide")
st.title("🔥 Finance Heatmap")

# Try to import matplotlib safely
try:
    import matplotlib.pyplot as plt
    HAVE_MPL = True
except Exception:
    HAVE_MPL = False

# Example: adapt to your actual data utils
try:
    from utils.home_metrics import read_tab
except Exception:
    def read_tab(name):
        return pd.DataFrame()

fin = read_tab("profitability_monthly")

if fin.empty:
    st.info("No finance data available yet.")
else:
    st.subheader("Net Profit Heatmap (example)")
    if not HAVE_MPL:
        st.error("matplotlib is not installed. Add 'matplotlib' to requirements.txt to see charts.")
    else:
        try:
            pivot = fin.pivot_table(index="sku", columns="month", values="net", aggfunc="sum").fillna(0)
            fig, ax = plt.subplots(figsize=(8,4))
            cax = ax.matshow(pivot.values, cmap="RdYlGn")
            ax.set_xticks(range(len(pivot.columns)))
            ax.set_xticklabels(pivot.columns, rotation=45, ha="left")
            ax.set_yticks(range(len(pivot.index)))
            ax.set_yticklabels(pivot.index)
            fig.colorbar(cax)
            st.pyplot(fig)
        except Exception as e:
            st.error(f"Failed to render heatmap: {e}")
