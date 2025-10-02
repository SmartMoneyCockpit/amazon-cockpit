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


import os

def _get_secret_or_env(name: str):
    val = st.secrets.get(name, None)
    if val is None:
        val = os.environ.get(name, None)
    return val

def lwa_diagnostics(run_live: bool = False) -> dict:
    """Return a dict showing which LWA fields are present and (optionally) a live token/profile test.

    Accepts both naming schemes: sp_api_* or ads_*.

    Keys returned:

      - secrets: {client_id: bool, client_secret: bool, refresh_token: bool, which_keys: {...}}

      - live: {ok: bool, message: str, profiles: int} (only if run_live=True and secrets are present)

    """

    # Presence by either alias

    client_id = _get_secret_or_env("sp_api_client_id") or _get_secret_or_env("ads_client_id")

    client_secret = _get_secret_or_env("sp_api_client_secret") or _get_secret_or_env("ads_client_secret")

    refresh_token = _get_secret_or_env("sp_api_refresh_token") or _get_secret_or_env("ads_refresh_token")

    region = _get_secret_or_env("ads_region") or "na"

    data = {

        "secrets": {

            "client_id": bool(client_id),

            "client_secret": bool(client_secret),

            "refresh_token": bool(refresh_token),

            "region": region,

            "which_keys": {

                "client_id": "sp_api_client_id" if _get_secret_or_env("sp_api_client_id") else ("ads_client_id" if _get_secret_or_env("ads_client_id") else None),

                "client_secret": "sp_api_client_secret" if _get_secret_or_env("sp_api_client_secret") else ("ads_client_secret" if _get_secret_or_env("ads_client_secret") else None),

                "refresh_token": "sp_api_refresh_token" if _get_secret_or_env("sp_api_refresh_token") else ("ads_refresh_token" if _get_secret_or_env("ads_refresh_token") else None),

            }

        }

    }

    if run_live and all([client_id, client_secret, refresh_token]):

        try:

            from utils.ads_api import quick_test

            data["live"] = quick_test()

        except Exception as e:

            data["live"] = {"ok": False, "message": f"Live check error: {e}", "profiles": 0}

    return data

