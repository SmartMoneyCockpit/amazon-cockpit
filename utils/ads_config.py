
import os

def env(name, default=None):
    v = os.environ.get(name, default)
    if v is None:
        return default
    return v

def ads_enabled() -> bool:
    # Explicit toggle; default False
    val = env("ADS_ENABLED", "false").strip().lower()
    return val in ("1","true","yes")

CONFIG = {
    "enabled": ads_enabled(),
    "client_id": env("ADS_LWA_CLIENT_ID", env("AMZ_LWA_CLIENT_ID", "")),
    "client_secret": env("ADS_LWA_CLIENT_SECRET", env("AMZ_LWA_CLIENT_SECRET", "")),
    "refresh_token": env("ADS_REFRESH_TOKEN", ""),
    "profile_id": env("ADS_PROFILE_ID", ""),  # advertiser profile id
    "region": env("ADS_REGION", "NA"),
}
