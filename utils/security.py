
from __future__ import annotations
import os
import streamlit as st

def allowed_origins() -> list[str]:
    raw = os.getenv("ALLOWED_ORIGINS","").strip()
    if not raw:
        return []
    return [x.strip().lower() for x in raw.split(",") if x.strip()]

def enforce():
    allowed = allowed_origins()
    if not allowed:
        st.caption("⚠️ ALLOWED_ORIGINS not set. Set it in Render to your deployed URL for hygiene.")
    else:
        st.caption(f"Allowed origins: {', '.join(allowed)}")
