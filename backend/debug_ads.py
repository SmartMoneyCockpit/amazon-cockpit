import os, requests

def _has_value(v: str | None) -> bool:
    return bool(v) and v.strip().lower() not in {"", "value", "xxxxx"}

def check_ads_env():
    vals = {
        "ADS_ENABLED": os.getenv("ADS_ENABLED"),
        "AMZ_ADS_API_BASE": os.getenv("AMZ_ADS_API_BASE"),
        "ADS_LWA_CLIENT_ID": os.getenv("ADS_LWA_CLIENT_ID") or os.getenv("AMZ_ADS_CLIENT_ID"),
        "ADS_LWA_CLIENT_SECRET": os.getenv("ADS_LWA_CLIENT_SECRET") or os.getenv("AMZ_ADS_CLIENT_SECRET"),
        "ADS_REFRESH_TOKEN": os.getenv("ADS_REFRESH_TOKEN") or os.getenv("AMZ_ADS_REFRESH_TOKEN"),
        "ADS_PROFILE_ID": os.getenv("ADS_PROFILE_ID") or os.getenv("AMZ_ADS_PROFILE_ID"),
    }
    missing = [k for k,v in vals.items() if not _has_value(v)]
    redacted = {k: (("set:"+str(len(v))) if _has_value(v) else "") for k,v in vals.items()}
    return redacted, missing

def get_access_token():
    client_id = os.getenv("ADS_LWA_CLIENT_ID") or os.getenv("AMZ_ADS_CLIENT_ID")
    client_secret = os.getenv("ADS_LWA_CLIENT_SECRET") or os.getenv("AMZ_ADS_CLIENT_SECRET")
    refresh_token = os.getenv("ADS_REFRESH_TOKEN") or os.getenv("AMZ_ADS_REFRESH_TOKEN")
    if not all([client_id, client_secret, refresh_token]): 
        return False, "missing LWA credentials"
    try:
        r = requests.post(
            "https://api.amazon.com/auth/o2/token",
            data={
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
                "client_id": client_id,
                "client_secret": client_secret,
            },
            timeout=20,
        )
        if r.status_code != 200:
            return False, f"{r.status_code} {r.text[:300]}"
        return True, r.json()["access_token"]
    except Exception as e:
        return False, str(e)

def ping_ads_profiles(access_token: str):
    base = os.getenv("AMZ_ADS_API_BASE", "https://advertising-api.amazon.com").rstrip("/")
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Amazon-Advertising-API-ClientId": os.getenv("ADS_LWA_CLIENT_ID") or os.getenv("AMZ_ADS_CLIENT_ID") or "",
        "Accept": "application/json",
    }
    try:
        r = requests.get(f"{base}/v2/profiles", headers=headers, timeout=20)
        return r.status_code, r.text[:300]
    except Exception as e:
        return 0, str(e)

def ping_ads_campaigns(access_token: str, profile_id: str):
    base = os.getenv("AMZ_ADS_API_BASE", "https://advertising-api.amazon.com").rstrip("/")
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Amazon-Advertising-API-ClientId": os.getenv("ADS_LWA_CLIENT_ID") or os.getenv("AMZ_ADS_CLIENT_ID") or "",
        "Amazon-Advertising-API-Scope": profile_id,
        "Accept": "application/json",
    }
    try:
        r = requests.get(f"{base}/v2/sp/campaigns?stateFilter=enabled,paused", headers=headers, timeout=20)
        return r.status_code, r.text[:300]
    except Exception as e:
        return 0, str(e)
