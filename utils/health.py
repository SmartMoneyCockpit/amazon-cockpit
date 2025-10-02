
import streamlit as st

def integration_health():
    """Quick integration health snapshot based on presence of secrets
    and a live check for Amazon Ads (LWA). Returns a list of (label, status, note)."""
    checks = []

    # Google Sheets credentials
    gs = bool(st.secrets.get("gsheets_credentials"))
    checks.append(("Google Sheets", "✅" if gs else "⚠️", "Credentials" if gs else "Missing credentials"))

    # Any Sheet IDs present?
    if any([
        st.secrets.get("gsheets_product_sheet_id"),
        st.secrets.get("gsheets_ppc_sheet_id"),
        st.secrets.get("gsheets_finance_sheet_id"),
        st.secrets.get("gsheets_keywords_sheet_id"),
    ]):
        checks.append(("Sheets IDs", "✅", "One or more connected"))
    else:
        checks.append(("Sheets IDs", "ℹ️", "You can add IDs later"))

    # Amazon Ads (LWA) — live connectivity test
    try:
        from utils.ads_api import quick_test
        t = quick_test()
        if t.get("ok"):
            checks.append(("Amazon Ads (LWA)", "✅", t.get("message", "Connected")))
        else:
            checks.append(("Amazon Ads (LWA)", "⚠️", t.get("message", "Set client/secret/refresh_token")))
    except Exception as e:
        checks.append(("Amazon Ads (LWA)", "⚠️", f"Check failed: {e}"))

    # Compliance index (optional)
    comp = bool(st.secrets.get("gsheets_compliance_sheet_id"))
    checks.append(("Compliance Index", "✅" if comp else "ℹ️", "Configured" if comp else "Optional"))

    # Changes log sheet (optional)
    chg = bool(st.secrets.get("gsheets_changes_log_sheet_id"))
    checks.append(("Changes Log Sheet", "✅" if chg else "ℹ️", "Configured" if chg else "Optional"))

    return checks
