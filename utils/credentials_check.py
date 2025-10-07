
from __future__ import annotations
from typing import Tuple, Optional
import os
def _secret_like(key: str)->Optional[str]:
    try:
        import streamlit as st
        if key in st.secrets: return str(st.secrets.get(key))
    except Exception: pass
    v=os.getenv(key); return str(v) if v is not None else None
def test_sheets()->Tuple[bool,str]:
    try:
        from infra.sheets_client import SheetsClient
        sc=SheetsClient(); sc.read_table("Settings"); return True,"Google Sheets: OK (read 'Settings')"
    except Exception as e: return False, f"Google Sheets test failed: {e}"
def test_sendgrid()->Tuple[bool,str]:
    try:
        from utils.email_sendgrid import send_email  # noqa
    except Exception:
        return False, "SendGrid client not available (utils.email_sendgrid missing)"
    api=_secret_like("SENDGRID_API_KEY"); frm=_secret_like("EMAIL_FROM"); to=_secret_like("EMAIL_TO")
    missing=[k for k,v in {"SENDGRID_API_KEY":api,"EMAIL_FROM":frm,"EMAIL_TO":to}.items() if not v]
    return (False, "Missing: "+", ".join(missing)) if missing else (True, "SendGrid: Keys present")
