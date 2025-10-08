"""
Ping helpers for email/webhook.
"""
import os, requests

def ping_sendgrid(timeout: int = 8) -> dict:
    key = os.getenv("SENDGRID_API_KEY","").strip()
    if not key:
        return {"status":"skipped","reason":"no_api_key"}
    url = "https://api.sendgrid.com/v3/user/account"
    try:
        r = requests.get(url, headers={"Authorization": f"Bearer {key}"}, timeout=timeout)
        return {"status": "ok" if 200 <= r.status_code < 300 else "error", "code": r.status_code}
    except Exception as e:
        return {"status":"error","message": str(e)}

def ping_webhook(timeout: int = 6) -> dict:
    url = os.getenv("WEBHOOK_URL","").strip() or os.getenv("ALERTS_WEBHOOK_URL","").strip()
    if not url:
        return {"status":"skipped","reason":"no_webhook_url"}
    try:
        r = requests.get(url, timeout=timeout)
        return {"status": "ok" if 200 <= r.status_code < 400 else "error", "code": r.status_code}
    except Exception as e:
        return {"status":"error","message": str(e)}
