
from __future__ import annotations
from typing import Tuple, Optional
import os

def _secret_like(key: str) -> Optional[str]:
    # Try st.secrets first, then env
    try:
        import streamlit as st  # type: ignore
        if key in st.secrets:
            v = st.secrets.get(key, None)
            return str(v) if v is not None else None
    except Exception:
        pass
    v = os.getenv(key, None)
    return str(v) if v is not None else None

def test_sheets() -> Tuple[bool, str]:
    try:
        from infra.sheets_client import SheetsClient
        sc = SheetsClient()
        # attempt a very light call
        _ = sc.read_table("Settings")  # if missing sheet, it should raise but creds/key path is tested
        return True, "Google Sheets: OK (read 'Settings' successfully)"
    except Exception as e:
        return False, f"Google Sheets test failed: {e}"

def test_sendgrid() -> Tuple[bool, str]:
    try:
        from utils.email_sendgrid import send_email  # type: ignore
    except Exception:
        return False, "SendGrid client not available (utils.email_sendgrid missing)"
    api = _secret_like("SENDGRID_API_KEY")
    frm = _secret_like("EMAIL_FROM")
    to  = _secret_like("EMAIL_TO")
    missing = [k for k,v in {"SENDGRID_API_KEY":api, "EMAIL_FROM":frm, "EMAIL_TO":to}.items() if not v]
    if missing:
        return False, "Missing secrets/env: " + ", ".join(missing)
    return True, "SendGrid: Keys present (not sending test mail here)"
