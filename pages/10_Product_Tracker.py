
import streamlit as st
import pandas as pd
from utils.auth import gate
import utils.security as sec
from utils.ui_refinements import inject_css, sheet_link

st.set_page_config(page_title="Product Tracker", layout="wide")
sec.enforce()
if not gate(required_admin=False):
    st.stop()

inject_css()
st.title("📦 Product Tracker")
st.caption("Sessions, CVR, units, inventory & reviews — enriched with catalog cache.")
st.write(sheet_link("inventory"), unsafe_allow_html=True)
# The rest of your existing Product Tracker content remains unchanged.
st.info("This patch only adds styling helpers and a jump-to-sheet link. Keep your existing logic below this line.")
