# services/amazon_ads_service.py
import os, time, requests

ADS_API_BASE = os.getenv("AMZ_ADS_API_BASE", "https://advertising-api.amazon.com")
CLIENT_ID    = os.getenv("AMZ_ADS_CLIENT_ID")
CLIENT_SECRET= os.getenv("AMZ_ADS_CLIENT_SECRET")
REFRESH_TOKEN= os.getenv("AMZ_ADS_REFRESH_TOKEN")
PROFILE_ID   = os.getenv("AMZ_ADS_PROFILE_ID")  # optional

_token_cache = {"access_token": None, "exp": 0}

def _now():
    return int(time.time())

def _get_access_token():
    # cache for ~55 minutes
    if _token_cache["access_token"] and _token_cache["exp"] > _now() + 60:
        return _token_cache["access_token"]

    resp = requests.post(
        "https://api.amazon.com/auth/o2/token",
        data={
            "grant_type": "refresh_token",
            "refresh_token": REFRESH_TOKEN,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        },
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    _token_cache["access_token"] = data["access_token"]
    _token_cache["exp"] = _now() + int(data.get("expires_in", 3600))
    return _token_cache["access_token"]

def _headers(profile_id=None):
    h = {
        "Authorization": f"Bearer {_get_access_token()}",
        "Amazon-Advertising-API-ClientId": CLIENT_ID,
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    if profile_id or PROFILE_ID:
        h["Amazon-Advertising-API-Scope"] = str(profile_id or PROFILE_ID)
    return h

def ads_get(path, params=None, profile_id=None):
    url = f"{ADS_API_BASE}{path}"
    r = requests.get(url, headers=_headers(profile_id), params=params, timeout=60)
    if r.status_code == 401:
        # force refresh once
        _token_cache["access_token"] = None
        r = requests.get(url, headers=_headers(profile_id), params=params, timeout=60)
    r.raise_for_status()
    return r.json()

def get_profiles():
    return ads_get("/v2/profiles")

def list_sp_campaigns(state_filter="enabled,paused", count=1000, start_index=0):
    params = {"stateFilter": state_filter, "count": count, "startIndex": start_index}
    return ads_get("/v2/sp/campaigns", params=params)

def get_sp_report_last_7d():
    # simple cumulative stats via v2 metrics endpoint (if enabled on your account)
    return ads_get("/v2/sp/campaigns", params={"count": 1000})
