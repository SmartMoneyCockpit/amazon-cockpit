import os, functools
import streamlit as st

def env(name: str, default: str | None = None) -> str | None:
    return os.getenv(name, default)

def allowed_origins() -> list[str]:
    raw = os.getenv("ALLOWED_ORIGINS", "")
    return [o.strip() for o in raw.split(",") if o.strip()]

@st.cache_resource(show_spinner=False)
def get_requests_session():
    import requests
    s = requests.Session()
    s.headers.update({"User-Agent": "VegaCockpit/Render"})
    return s

def lazy_import(name: str):
    return __import__(name)

def health_ok() -> bool:
    # Simple in-process health signal; extend with real checks as desired.
    return True
