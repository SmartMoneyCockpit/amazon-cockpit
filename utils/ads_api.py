
"""Amazon Ads (Advertising API) helper using LWA refresh tokens.
Supports:
- quick_test(): simple /v2/profiles call to verify credentials
- AdsClient: minimal client used by PPC Manager for listing profiles/campaigns
Secrets accepted (Streamlit secrets or env):
  sp_api_client_id / sp_api_client_secret / sp_api_refresh_token
  or ads_client_id / ads_client_secret / ads_refresh_token
Optional: ads_region in {'na','eu','fe'} (default 'na').
"""
from __future__ import annotations
import os
import typing as T
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
    val = st.secrets.get(name, None)
    if val is None:
        val = os.environ.get(name, default)
    return val

def load_creds() -> T.Optional[AdsCredentials]:
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

# ---- AdsClient used by PPC Manager (kept compatible) ----
class AdsClient:
    def __init__(self):
        self.creds = load_creds()
        self._access_token: T.Optional[str] = None

    @property
    def region_base(self) -> str:
        return region_base()

    def available(self) -> bool:
        return self.creds is not None

    def _token(self) -> str:
        if not self.available():
            raise RuntimeError("Missing SP-API/LWA secrets")
        if not self._access_token:
            self._access_token = fetch_access_token(self.creds)
        return self._access_token

    def get_profiles(self) -> pd.DataFrame:
        if not self.available():
            return _fallback_profiles_df()
        try:
            tok = self._token()
            r = requests.get(f"{self.region_base}/v2/profiles", headers=headers(tok, self.creds.client_id), timeout=20)
            if r.status_code != 200:
                raise RuntimeError(f"profiles {r.status_code}: {r.text[:200]}")
            js = r.json()
            return pd.DataFrame(js) if isinstance(js, list) else pd.json_normalize(js)
        except Exception as e:
            st.warning(f"Profiles fetch failed: {e}")
            return _fallback_profiles_df()

    def get_sp_campaigns(self, profile_id: str) -> pd.DataFrame:
        if not self.available():
            return _fallback_campaigns_df()
        try:
            tok = self._token()
            r = requests.get(f"{self.region_base}/v2/sp/campaigns", headers=headers(tok, self.creds.client_id, profile_id), timeout=20)
            if r.status_code != 200:
                raise RuntimeError(f"campaigns {r.status_code}: {r.text[:200]}")
            js = r.json()
            return pd.DataFrame(js) if isinstance(js, list) else pd.json_normalize(js)
        except Exception as e:
            st.warning(f"SP campaigns fetch failed: {e}")
            return _fallback_campaigns_df()

    def get_sample_metrics(self) -> pd.DataFrame:
        # 14-day sample shaped like PPC tab expects
        return pd.DataFrame({
            "Date": pd.date_range(end=pd.Timestamp.today(), periods=14),
            "Campaign": ["Auto"]*7 + ["Exact"]*7,
            "Impressions": [10000,12500,9800,11700,10900,13200,12800, 15000,14100,16200,15800,14900,16700,17200],
            "Clicks": [300,320,280,305,295,345,330, 400,395,420,415,405,430,445],
            "Spend": [120,132,118,125,121,142,139, 210,205,219,214,209,223,229],
            "Orders": [25,26,23,24,24,28,27, 36,34,38,37,35,39,41],
            "ACoS%": [40,41,38,39,40,41,42, 33,32,31,32,31,30,29],
            "ROAS": [2.5,2.4,2.6,2.6,2.5,2.4,2.4, 3.0,3.1,3.2,3.1,3.2,3.3,3.4],
        })

def _fallback_profiles_df() -> pd.DataFrame:
    return pd.DataFrame([
        {"profileId": "123", "countryCode": "US", "currencyCode": "USD", "timezone": "America/Los_Angeles"},
        {"profileId": "456", "countryCode": "CA", "currencyCode": "CAD", "timezone": "America/Toronto"},
    ])

def _fallback_campaigns_df() -> pd.DataFrame:
    return pd.DataFrame([
        {"campaignId": "A1", "name": "Auto", "state": "enabled", "dailyBudget": 50},
        {"campaignId": "E1", "name": "Exact", "state": "paused", "dailyBudget": 30},
    ])
