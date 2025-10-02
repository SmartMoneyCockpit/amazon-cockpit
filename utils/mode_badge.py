
from __future__ import annotations
import os
import streamlit as st

def badge():
    public = os.getenv("AUTH_PUBLIC_MODE","true").strip().lower() in ("1","true","yes")
    role = "Public" if public else "Auth Required"
    st.sidebar.markdown(f"**Mode:** {role}")
