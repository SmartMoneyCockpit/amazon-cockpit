import streamlit as st
from modules.ppc_manager import ppc_manager_view

st.set_page_config(page_title="PPC Manager — Amazon Cockpit", page_icon="📈", layout="wide")
ppc_manager_view()
