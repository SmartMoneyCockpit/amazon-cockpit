import streamlit as st
from modules.finance_dashboard import finance_dashboard_view

st.set_page_config(page_title="Finance Dashboard — Amazon Cockpit", page_icon="💵", layout="wide")
finance_dashboard_view()
