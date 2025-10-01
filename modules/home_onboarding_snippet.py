import streamlit as st
import pandas as pd
from utils.onboarding import checklist_items

def render_getting_started():
    st.subheader("🧭 Getting Started Checklist")
    items = checklist_items()
    df = pd.DataFrame(items, columns=["Item","Status","Note / Key"])
    st.dataframe(df, use_container_width=True, hide_index=True)

    with st.expander("⬇️ Secrets Template (download)"):
        template = """\
# .streamlit/secrets.toml
env = "staging"

# --- Amazon Ads (LWA) ---
sp_api_client_id = "amzn1.application-oa2-client.xxx"
sp_api_client_secret = "xxxxx"
sp_api_refresh_token = "Atzr|IwEBI..."

# --- Google Sheets ---
# Paste full Service Account JSON as a single line or TOML block
gsheets_credentials = ""

# Individual file IDs (optional; add as you connect each module)
gsheets_product_sheet_id = ""
gsheets_ppc_sheet_id = ""
gsheets_finance_sheet_id = ""
gsheets_compliance_sheet_id = ""
gsheets_keywords_sheet_id = ""
gsheets_competitors_sheet_id = ""
gsheets_changes_log_sheet_id = ""
"""
        st.download_button("Download secrets.toml template", data=template.encode("utf-8"), file_name="secrets.toml", mime="text/plain")
    st.caption("Tip: Share each Google Sheet with the service account email shown in your JSON credentials.")
