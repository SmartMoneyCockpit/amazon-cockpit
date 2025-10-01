"""
Starter Amazon Ads (SP-API Advertising) client.
- Uses Login With Amazon (LWA) to obtain access tokens from client_id/secret/refresh_token.
- Reads SP-API/LWA secrets from Streamlit secrets.
- Fetches Profiles and basic Sponsored Products Campaigns.
- Falls back to sample data if secrets are missing or API fails.

NOTE: For full metrics (impressions, clicks, spend, orders, ACOS/ROAS) you typically need the
Advertising Reporting API (v3) to request/poll a report and then download it. This starter keeps
it light: list profiles/campaigns live, and you can still run charts/optimizer on sample metrics
until we add reporting calls.
"""
from __future__ import annotations
import time
import json
import base64
import typing as T

import streamlit as st
import pandas as pd
import requests
from dataclasses import dataclass
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

LWA_TOKEN_URL = "https://api.amazon.com/auth/o2/token"
ADS_API_BASE  = "https://advertising-api.amazon.com"   # NA prod; can swap for EU/FE

class AdsAuthError(Exception): ...
class AdsApiError(Exception): ...

@dataclass
class AdsCredentials:
    client_id: str
    client_secret: str
    refresh_token: str

def _read_creds() -> T.Optional[AdsCredentials]:
    cid = st.secrets.get("sp_api_client_id")
    cs  = st.secrets.get("sp_api_client_secret")
    rt  = st.secrets.get("sp_api_refresh_token")
    if not cid or not cs or not rt:
        return None
    return AdsCredentials(cid, cs, rt)

@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=8), reraise=True)
def _fetch_access_token(creds: AdsCredentials) -> str:
    data = {
        "grant_type": "refresh_token",
        "refresh_token": creds.refresh_token,
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
    }
    r = requests.post(LWA_TOKEN_URL, data=data, timeout=20)
    if r.status_code != 200:
        raise AdsAuthError(f"LWA token failed: {r.status_code} {r.text[:200]}")
    return r.json()["access_token"]

def _headers(access_token: str, profile_id: T.Optional[str] = None) -> dict:
    h = {
        "Authorization": f"Bearer {access_token}",
        "Amazon-Advertising-API-ClientId": st.secrets.get("sp_api_client_id",""),
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    if profile_id:
        h["Amazon-Advertising-API-Scope"] = str(profile_id)
    return h

def _fallback_profiles_df() -> pd.DataFrame:
    return pd.DataFrame([
        {"profileId":"0000","countryCode":"US","currencyCode":"USD","marketplaceStringId":"ATVPDKIKX0DER","accountInfo":{"marketplaceStringId":"ATVPDKIKX0DER","type":"seller"}}
    ])

def _fallback_campaigns_df() -> pd.DataFrame:
    return pd.DataFrame([
        {"campaignId":"c-1","name":"Auto","state":"enabled","dailyBudget":25.0,"portfolioId":None,"adProduct":"SPONSORED_PRODUCTS"},
        {"campaignId":"c-2","name":"Exact","state":"enabled","dailyBudget":30.0,"portfolioId":None,"adProduct":"SPONSORED_PRODUCTS"},
    ])

class AdsClient:
    def __init__(self, region_base: str = ADS_API_BASE):
        self.region_base = region_base
        self.creds = _read_creds()
        self._access_token: T.Optional[str] = None

    def available(self) -> bool:
        return self.creds is not None

    def _token(self) -> str:
        if not self.creds:
            raise AdsAuthError("Missing SP-API/LWA secrets")
        if not self._access_token:
            self._access_token = _fetch_access_token(self.creds)
        return self._access_token

    def get_profiles(self) -> pd.DataFrame:
        if not self.available():
            return _fallback_profiles_df()
        try:
            tok = self._token()
            r = requests.get(f"{self.region_base}/v2/profiles", headers=_headers(tok), timeout=20)
            if r.status_code != 200:
                raise AdsApiError(f"profiles {r.status_code}: {r.text[:200]}")
            js = r.json()
            return pd.DataFrame(js) if isinstance(js, list) else pd.json_normalize(js)
        except Exception as e:
            st.warning(f"Profiles fetch failed: {e}")
            return _fallback_profiles_df()

    def get_sp_campaigns(self, profile_id: str) -> pd.DataFrame:
        """List SP campaigns (basic fields); budgets/State are included; metrics need reports."""
        if not self.available():
            return _fallback_campaigns_df()
        try:
            tok = self._token()
            # v2 list
            r = requests.get(f"{self.region_base}/v2/sp/campaigns", headers=_headers(tok, profile_id), timeout=20)
            if r.status_code != 200:
                raise AdsApiError(f"campaigns {r.status_code}: {r.text[:200]}")
            js = r.json()
            return pd.DataFrame(js) if isinstance(js, list) else pd.json_normalize(js)
        except Exception as e:
            st.warning(f"Campaigns fetch failed: {e}")
            return _fallback_campaigns_df()

    # Placeholder for reporting (future step)
    def get_sample_metrics(self) -> pd.DataFrame:
        """Return 14-day sample metrics shaped like PPC tab expects."""
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
