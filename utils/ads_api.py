
"""Amazon Ads (Advertising API) helper using LWA refresh tokens.
Now supports reading credentials from:
- Streamlit secrets (lower/UPPER)
- Environment variables (lower/UPPER)
- Render 'Secret Files' mounted under /etc/secrets/<NAME>
Accepted aliases (any of these may be set):
  client_id:  sp_api_client_id | ads_client_id | SP_API_CLIENT_ID | SPAPI_CLIENT_ID | ADS_CLIENT_ID
  client_secret: sp_api_client_secret | ads_client_secret | SP_API_CLIENT_SECRET | SPAPI_CLIENT_SECRET | ADS_CLIENT_SECRET
  refresh_token: sp_api_refresh_token | ads_refresh_token | SP_API_REFRESH_TOKEN | SPAPI_REFRESH_TOKEN | ADS_REFRESH_TOKEN
Region aliases:
  ads_region | REGION   (values: na | eu | fe; default na)
"""
from __future__ import annotations
import os, typing as T, requests, pandas as pd, streamlit as st
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

def _read_secret_file(name: str) -> T.Optional[str]:
    """Read Render Secret File content if present."""
    # Typical mount path for Render Secret Files
    paths = [f"/etc/secrets/{name}", f"/etc/secrets/{name.upper()}", f"/etc/secrets/{name.lower()}" ]
    for p in paths:
        try:
            if os.path.exists(p):
                val = open(p, "r", encoding="utf-8").read().strip()
                if val:
                    return val
        except Exception:
            pass
    return None

def _first_present(names: T.List[str]) -> T.Optional[str]:
    for n in names:
        # 1) Streamlit secrets (accept both exact and UPPER)

        v = st.secrets.get(n, None)
        if v is None:
            v = st.secrets.get(n.upper(), None)
        if v:
            return str(v)
        # 2) Environment
        v = os.environ.get(n) or os.environ.get(n.upper())
        if v:
            return v
        # 3) Secret file
        v = _read_secret_file(n) or _read_secret_file(n.upper())
        if v:
            return v
    return None

def load_creds() -> T.Optional[AdsCredentials]:
    cid = _first_present(["sp_api_client_id","ads_client_id","SP_API_CLIENT_ID","SPAPI_CLIENT_ID","ADS_CLIENT_ID"])
    cs  = _first_present(["sp_api_client_secret","ads_client_secret","SP_API_CLIENT_SECRET","SPAPI_CLIENT_SECRET","ADS_CLIENT_SECRET"])
    rt  = _first_present(["sp_api_refresh_token","ads_refresh_token","SP_API_REFRESH_TOKEN","SPAPI_REFRESH_TOKEN","ADS_REFRESH_TOKEN"])
    if not cid or not cs or not rt:
        return None
    return AdsCredentials(cid, cs, rt)

def region_base() -> str:
    region = (_first_present(["ads_region","REGION"]) or "na").lower()
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

# ---- AdsClient for PPC Manager ----
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
