import streamlit as st
from modules.home import dashboard_home_view

st.set_page_config(page_title="Amazon Cockpit — Home", page_icon="🛒", layout="wide")

dashboard_home_view()

st.divider()
st.caption("© 2025 Amazon Cockpit. Home dashboard, alerts rollup, and integration health.")
