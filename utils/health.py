import streamlit as st\n\ndef integration_health():\n    """\n    Quick integration health snapshot based on presence of secrets and prior packs.\n    Returns list of (label, status, note).\n    """\n    checks = []\n    # Google Sheets\n    gs = bool(st.secrets.get("gsheets_credentials"))\n    checks.append(("Google Sheets", "✅" if gs else "⚠️", "Credentials" if gs else "Missing credentials"))\n    # Sheets IDs\n    if st.secrets.get("gsheets_product_sheet_id") or st.secrets.get("gsheets_ppc_sheet_id") \\n       or st.secrets.get("gsheets_finance_sheet_id") or st.secrets.get("gsheets_keywords_sheet_id"):\n        checks.append(("Sheets IDs", "✅", "One or more connected"))\n    else:\n        checks.append(("Sheets IDs", "ℹ️", "You can add IDs later"))\n\n    # Ads (LWA)\n    lwa_ready = all([st.secrets.get("sp_api_client_id"), st.secrets.get("sp_api_client_secret"), st.secrets.get("sp_api_refresh_token")])\n
# Ads (LWA) — live connectivity test
try:
    from utils.ads_api import quick_test
    t = quick_test()
    if t.get("ok"):
        checks.append(("Amazon Ads (LWA)", "✅", t.get("message","Connected")))
    else:
        checks.append(("Amazon Ads (LWA)", "⚠️", t.get("message","Set client/secret/refresh_token")))
except Exception as e:
    checks.append(("Amazon Ads (LWA)", "⚠️", f"Check failed: {e}"))
\n    checks.append(("Compliance Index", "✅" if comp else "ℹ️", "Configured" if comp else "Optional"))\n\n    # Changes Log sheet\n    chg = bool(st.secrets.get("gsheets_changes_log_sheet_id"))\n    checks.append(("Changes Log Sheet", "✅" if chg else "ℹ️", "Configured" if chg else "Optional"))\n\n    return checks