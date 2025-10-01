import streamlit as st
from modules.product_tracker import product_tracker_view

st.set_page_config(page_title="Product Tracker — Amazon Cockpit", page_icon="📦", layout="wide")
product_tracker_view()
