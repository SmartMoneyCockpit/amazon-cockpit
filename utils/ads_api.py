
"""Amazon Ads (Advertising API) helper using LWA refresh tokens.
- Reads creds from Streamlit secrets or env:
    sp_api_client_id / sp_api_client_secret / sp_api_refresh_token
    OR ads_client_id / ads_client_secret / ads_refresh_token
- Region: secrets['ads_region'] in {'na','eu','fe'} (default 'na').
- Provides quick_test() that gets an access token and calls /v2/profiles.
"""
from __future__ import annotations
import typing as T
import os
import json
import requests
import pandas as pd
import streamlit as st
from dataclasses import dataclass
from tenacity import retry, stop_after_attempt, wait_exponential

LWA_TOKEN_URL = "https://api.amazon.com/auth/o2/token"
REGION_BASE = {
    "na": "https://advertising-api.amazon.com",
    "eu": "https://advertising-api-eu.amazon.com",
    "fe": "https://advertising-api-fe.amazon.com",
}

@dataclass
class AdsCredentials:
    client_id: str
    client_secret: str
    refresh_token: str

def _secrets_get(name: str, default: str = "") -> str:
    # Prefer st.secrets; fallback to env
    val = st.secrets.get(name)
    if val is None:
        val = os.environ.get(name, default)
    return val

def load_creds() -> T.Optional[AdsCredentials]:
    # Support both naming schemes
    cid = _secrets_get("sp_api_client_id") or _secrets_get("ads_client_id")
    cs  = _secrets_get("sp_api_client_secret") or _secrets_get("ads_client_secret")
    rt  = _secrets_get("sp_api_refresh_token") or _secrets_get("ads_refresh_token")
    if not cid or not cs or not rt:
        return None
    return AdsCredentials(cid, cs, rt)

def region_base() -> str:
    region = (_secrets_get("ads_region", "na") or "na").lower()
    return REGION_BASE.get(region, REGION_BASE["na"])

@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=8), reraise=True)
def fetch_access_token(creds: AdsCredentials) -> str:
    data = {
        "grant_type": "refresh_token",
        "refresh_token": creds.refresh_token,
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
    }
    r = requests.post(LWA_TOKEN_URL, data=data, timeout=20)
    if r.status_code != 200:
        raise RuntimeError(f"LWA token failed: {r.status_code} {r.text[:200]}")
    return r.json()["access_token"]

def headers(access_token: str, client_id: str, profile_id: T.Optional[str] = None) -> dict:
    h = {
        "Authorization": f"Bearer {access_token}",
        "Amazon-Advertising-API-ClientId": client_id,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    if profile_id:
        h["Amazon-Advertising-API-Scope"] = str(profile_id)
    return h

def quick_test() -> dict:
    """Return {ok: bool, message: str, profiles: int} by calling /v2/profiles."""
    creds = load_creds()
    if not creds:
        return {"ok": False, "message": "Missing client/secret/refresh_token", "profiles": 0}
    try:
        tok = fetch_access_token(creds)
        r = requests.get(f"{region_base()}/v2/profiles", headers=headers(tok, creds.client_id), timeout=20)
        if r.status_code != 200:
            return {"ok": False, "message": f"profiles {r.status_code}: {r.text[:120]}", "profiles": 0}
        js = r.json()
        n = len(js) if isinstance(js, list) else 1
        return {"ok": True, "message": f"Connected: {n} profile(s)", "profiles": n}
    except Exception as e:
        return {"ok": False, "message": f"Error: {e}", "profiles": 0}
