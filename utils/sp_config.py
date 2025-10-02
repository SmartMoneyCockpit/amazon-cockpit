
import os

def env(name, default=None):
    v = os.environ.get(name, default)
    if v is None or (isinstance(v, str) and v.strip() == ""):
        return default
    return v

def get_marketplace_ids():
    raw = env("AMZ_MARKETPLACE_IDS", "ATVPDKIKX0DER")  # US default
    return [x.strip() for x in raw.split(",") if x.strip()]

CONFIG = {
    "refresh_token": env("AMZ_REFRESH_TOKEN", ""),
    "lwa_app_id": env("AMZ_LWA_CLIENT_ID", ""),
    "lwa_client_secret": env("AMZ_LWA_CLIENT_SECRET", ""),
    "aws_access_key": env("AMZ_AWS_ACCESS_KEY_ID", None),
    "aws_secret_key": env("AMZ_AWS_SECRET_ACCESS_KEY", None),
    "role_arn": env("AMZ_ROLE_ARN", None),
    "region": env("AMZ_REGION", "NA"),
    "marketplace_ids": get_marketplace_ids(),
    "seller_id": env("AMZ_SELLER_ID", ""),
    "timezone": env("TIMEZONE", env("timezone", "America/Mazatlan")),
}
