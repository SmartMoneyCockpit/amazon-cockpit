import streamlit as st
from modules.alerts_hub import alerts_hub_view

st.set_page_config(page_title="Alerts Hub — Amazon Cockpit", page_icon="🚨", layout="wide")
alerts_hub_view()
