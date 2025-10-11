import os
import streamlit as st

def env(name: str, default: str | None = None) -> str | None:
    return os.getenv(name, default)

def allowed_origins() -> list[str]:
    raw = os.getenv("ALLOWED_ORIGINS", "")
    return [o.strip() for o in raw.split(",") if o.strip()]

@st.cache_resource(show_spinner=False)
def requests_session():
    import requests
    s = requests.Session()
    s.headers.update({"User-Agent": "AmazonCockpit/Render"})
    return s

def health_ok() -> bool:
    return True
