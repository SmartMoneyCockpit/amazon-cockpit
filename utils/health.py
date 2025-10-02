
import streamlit as st
import os

from utils.ads_api import quick_test, load_creds

def integration_health():
    """Quick integration health snapshot, including live LWA test."""
    checks = []

    gs = bool(st.secrets.get("gsheets_credentials"))
    checks.append(("Google Sheets", "✅" if gs else "⚠️", "Credentials" if gs else "Missing credentials"))

    if any([
        st.secrets.get("gsheets_product_sheet_id"),
        st.secrets.get("gsheets_ppc_sheet_id"),
        st.secrets.get("gsheets_finance_sheet_id"),
        st.secrets.get("gsheets_keywords_sheet_id"),
    ]):
        checks.append(("Sheets IDs", "✅", "One or more connected"))
    else:
        checks.append(("Sheets IDs", "ℹ️", "You can add IDs later"))

    try:
        t = quick_test()
        checks.append(("Amazon Ads (LWA)", "✅" if t.get("ok") else "⚠️", t.get("message", "Set client/secret/refresh_token")))
    except Exception as e:
        checks.append(("Amazon Ads (LWA)", "⚠️", f"Check failed: {e}"))

    comp = bool(st.secrets.get("gsheets_compliance_sheet_id"))
    checks.append(("Compliance Index", "✅" if comp else "ℹ️", "Configured" if comp else "Optional"))

    chg = bool(st.secrets.get("gsheets_changes_log_sheet_id"))
    checks.append(("Changes Log Sheet", "✅" if chg else "ℹ️", "Configured" if chg else "Optional"))

    return checks

def _get(name: str):
    return st.secrets.get(name) or os.environ.get(name)

def lwa_diagnostics(run_live: bool = False) -> dict:
    creds = load_creds()
    present = {
        "client_id": bool(creds.client_id) if creds else False,
        "client_secret": bool(creds.client_secret) if creds else False,
        "refresh_token": bool(creds.refresh_token) if creds else False,
        "region": (st.secrets.get("ads_region") or os.environ.get("ads_region") or os.environ.get("REGION") or "na").lower(),
        "which_keys": {
            "client_id": "(auto-detected from aliases)",
            "client_secret": "(auto-detected from aliases)",
            "refresh_token": "(auto-detected from aliases)",
        }
    }
    data = {"secrets": present}
    if run_live and creds:
        try:
            t = quick_test()
            data["live"] = t
        except Exception as e:
            data["live"] = {"ok": False, "message": str(e), "profiles": 0}
    return data
