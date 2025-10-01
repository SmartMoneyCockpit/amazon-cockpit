import streamlit as st
from modules.compliance_vault import compliance_vault_view

st.set_page_config(page_title="Compliance Vault — Amazon Cockpit", page_icon="🧾", layout="wide")
compliance_vault_view()
