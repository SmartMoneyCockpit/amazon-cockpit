import streamlit as st

def _has(key: str) -> bool:
    v = st.secrets.get(key)
    return v is not None and str(v).strip() != ""

def checklist_items():
    items = []

    # Core
    items.append(("Environment tag set (env)", "✅" if _has("env") else "ℹ️", "Optional but recommended: 'staging' or 'prod'"))

    # Google Sheets read
    sheets_creds = _has("gsheets_credentials")
    items.append(("Google Sheets credentials", "✅" if sheets_creds else "⚠️", "Service Account JSON in `gsheets_credentials`"))

    # Product / PPC / Finance / A+ / Competitors IDs
    ids = {
        "gsheets_product_sheet_id": "Product sheet ID",
        "gsheets_ppc_sheet_id": "PPC sheet ID",
        "gsheets_finance_sheet_id": "Finance sheet ID",
        "gsheets_compliance_sheet_id": "Compliance index sheet ID",
        "gsheets_keywords_sheet_id": "Keywords sheet ID",
        "gsheets_competitors_sheet_id": "Competitors sheet ID",
        "gsheets_changes_log_sheet_id": "Changes Log sheet ID",
    }
    any_id = any(_has(k) for k in ids.keys())
    items.append(("Any Sheets file IDs set", "✅" if any_id else "ℹ️", "Set as you go; samples work meanwhile"))
    for k, label in ids.items():
        items.append((label, "✅" if _has(k) else "•", k))

    # Amazon Ads (LWA) creds
    lwa_ok = all(_has(k) for k in ["sp_api_client_id","sp_api_client_secret","sp_api_refresh_token"])
    items.append(("Amazon Ads (LWA) credentials", "✅" if lwa_ok else "⚠️", "Client ID/Secret + Refresh Token"))

    return items
