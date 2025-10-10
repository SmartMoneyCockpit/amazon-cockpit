# utils/api_client.py
from __future__ import annotations
import os, json, requests
import streamlit as st
from typing import Any, Dict, Tuple

def _get_secret_like(key: str, default: str = "") -> str:
    try:
        v = st.secrets.get(key, None)
        if v is not None:
            return str(v)
    except Exception:
        pass
    return os.getenv(key) or os.getenv(key.upper()) or default

API_BASE = (_get_secret_like("API_URL", "") or "").rstrip("/")
API_KEY  = _get_secret_like("API_KEY", "")

def _headers() -> Dict[str, str]:
    h = {}
    if API_KEY:
        h["x-api-key"] = API_KEY
    return h

def api_get(path: str, timeout: float = 15.0) -> Tuple[bool, Any]:
    """
    GET helper. Returns (ok, data_or_error).
    ok=True -> parsed JSON (or text) in data_or_error.
    ok=False -> error message string in data_or_error.
    """
    if not API_BASE:
        return False, "API_URL not set in env/secrets."
    url = f"{API_BASE}{path if path.startswith('/') else '/'+path}"
    try:
        r = requests.get(url, headers=_headers(), timeout=timeout)
        if r.status_code == 200:
            try:
                return True, r.json()
            except Exception:
                return True, r.text
        return False, f"{r.status_code} {r.text}"
    except Exception as e:
        return False, str(e)

# Convenience wrappers you can import elsewhere
def health() -> Tuple[bool, Any]:
    return api_get("/health")

def list_products(limit: int = 50, offset: int = 0) -> Tuple[bool, Any]:
    return api_get(f"/v1/products?limit={limit}&offset={offset}")

def finance_summary():
    return api_get("/v1/finance/summary")

def finance_daily(limit: int = 60):
    return api_get(f"/v1/finance/daily?limit={limit}")

