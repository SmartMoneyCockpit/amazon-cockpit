import streamlit as st
from utils.layout import section_header

def compliance_vault_view():
    section_header("🧾 Compliance Vault")
    st.caption("GMP/COA, expiry tracking, 3rd‑party lab PDFs.")
    st.write("• Documents stored in Vault (placeholder)\n• Expiry alerts: none\n• Missing COAs: none")
    st.info("Next: connect to Drive folder/Notion DB or Sheets index; add upload & reminder scheduler.")
