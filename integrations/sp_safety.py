
from utils.sp_config import CONFIG

def ready() -> bool:
    # Minimum secrets to hit live endpoints
    return all([
        CONFIG.get('refresh_token'),
        CONFIG.get('lwa_app_id'),
        CONFIG.get('lwa_client_secret'),
    ])
