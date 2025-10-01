import streamlit as st

def integration_health():
    """
    Quick integration health snapshot based on presence of secrets and prior packs.
    Returns list of (label, status, note).
    """
    checks = []
    # Google Sheets
    gs = bool(st.secrets.get("gsheets_credentials"))
    checks.append(("Google Sheets", "✅" if gs else "⚠️", "Credentials" if gs else "Missing credentials"))
    # Sheets IDs
    if st.secrets.get("gsheets_product_sheet_id") or st.secrets.get("gsheets_ppc_sheet_id") \
       or st.secrets.get("gsheets_finance_sheet_id") or st.secrets.get("gsheets_keywords_sheet_id"):
        checks.append(("Sheets IDs", "✅", "One or more connected"))
    else:
        checks.append(("Sheets IDs", "ℹ️", "You can add IDs later"))

    # Ads (LWA)
    lwa_ready = all([st.secrets.get("sp_api_client_id"), st.secrets.get("sp_api_client_secret"), st.secrets.get("sp_api_refresh_token")])
    checks.append(("Amazon Ads (LWA)", "✅" if lwa_ready else "⚠️", "Ready" if lwa_ready else "Set client/secret/refresh_token"))

    # Compliance sheet
    comp = bool(st.secrets.get("gsheets_compliance_sheet_id"))
    checks.append(("Compliance Index", "✅" if comp else "ℹ️", "Configured" if comp else "Optional"))

    # Changes Log sheet
    chg = bool(st.secrets.get("gsheets_changes_log_sheet_id"))
    checks.append(("Changes Log Sheet", "✅" if chg else "ℹ️", "Configured" if chg else "Optional"))

    return checks
