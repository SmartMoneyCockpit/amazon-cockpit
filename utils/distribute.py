
from __future__ import annotations
import os, base64, json, datetime as dt, typing as t

DIGEST_DIR = os.getenv("DIGEST_OUT_DIR", "/tmp")

def _today_tag() -> str:
    return dt.datetime.now().strftime("%Y%m%d")

def _paths_for_today() -> dict:
    tag = _today_tag()
    pdf = os.path.join(DIGEST_DIR, f"digest_{tag}.pdf")
    zf  = os.path.join(DIGEST_DIR, f"digest_{tag}.zip")
    out = {}
    if os.path.exists(pdf): out["pdf"] = pdf
    if os.path.exists(zf):  out["zip"] = zf
    return out

# ---------------- Email via SendGrid ----------------
def send_email_via_sendgrid(subject: str, html: str, attachments: t.Optional[dict] = None) -> t.Tuple[str, str]:
    """
    Sends an email via SendGrid API using env vars:
      SENDGRID_API_KEY, DIGEST_EMAIL_FROM, DIGEST_EMAIL_TO
    Attachments: dict {"pdf": <path>, "zip": <path>}
    Returns (status, message).
    """
    import requests

    api_key = os.getenv("SENDGRID_API_KEY","").strip()
    email_from = os.getenv("DIGEST_EMAIL_FROM","").strip()
    email_to   = os.getenv("DIGEST_EMAIL_TO","").strip()

    if not api_key or not email_from or not email_to:
        return ("skipped", "Missing SENDGRID_API_KEY / DIGEST_EMAIL_FROM / DIGEST_EMAIL_TO")

    data = {
        "personalizations": [ {"to": [{"email": email_to}]} ],
        "from": {"email": email_from},
        "subject": subject,
        "content": [{"type": "text/html", "value": html}],
    }

    atts = []
    if attachments:
        for name, path in attachments.items():
            if not path or not os.path.exists(path): 
                continue
            try:
                with open(path, "rb") as f:
                    b64 = base64.b64encode(f.read()).decode("utf-8")
                mime = "application/pdf" if path.endswith(".pdf") else "application/zip"
                atts.append({
                    "content": b64,
                    "type": mime,
                    "filename": os.path.basename(path),
                    "disposition": "attachment"
                })
            except Exception:
                pass
    if atts:
        data["attachments"] = atts

    try:
        resp = requests.post(
            "https://api.sendgrid.com/v3/mail/send",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            data=json.dumps(data)
        )
        if 200 <= resp.status_code < 300:
            return ("ok", f"sent email to {email_to}")
        return ("error", f"sendgrid status {resp.status_code}: {resp.text[:200]}")
    except Exception as e:
        return ("error", str(e))

# ---------------- Webhook POST ----------------
def post_to_webhook(payload: dict) -> t.Tuple[str, str]:
    """
    POSTs JSON payload to WEBHOOK_URL (env). Best-effort, no attachment upload.
    Returns (status, message).
    """
    import requests

    url = os.getenv("WEBHOOK_URL","").strip()
    if not url:
        return ("skipped", "WEBHOOK_URL not set")

    try:
        resp = requests.post(url, json=payload, timeout=15)
        if 200 <= resp.status_code < 300:
            return ("ok", f"webhook status {resp.status_code}")
        return ("error", f"webhook status {resp.status_code}: {resp.text[:200]}")
    except Exception as e:
        return ("error", str(e))

# ---------------- Main helpers ----------------
def distribute_today(subject_prefix: str = "Daily Digest") -> dict:
    """
    Distributes today's digest via channels configured:
      - Email via SendGrid (if SENDGRID_API_KEY & DIGEST_EMAIL_* set)
      - Webhook POST (if WEBHOOK_URL set)
    Returns dict with statuses.
    """
    tag = _today_tag()
    paths = _paths_for_today()
    results = {}

    # Email
    if os.getenv("SENDGRID_API_KEY") and os.getenv("DIGEST_EMAIL_TO") and os.getenv("DIGEST_EMAIL_FROM"):
        html = f"<p>Digest {tag} generated.</p>" + "".join(
            f"<p>Attached: {os.path.basename(p)}</p>" for p in paths.values()
        )
        status, msg = send_email_via_sendgrid(f"{subject_prefix} — {tag}", html, attachments=paths)
        results["email"] = (status, msg)
    else:
        results["email"] = ("skipped", "email env not fully set")

    # Webhook
    if os.getenv("WEBHOOK_URL"):
        payload = {"type": "daily_digest", "date": tag, "paths": paths}
        status, msg = post_to_webhook(payload)
        results["webhook"] = (status, msg)
    else:
        results["webhook"] = ("skipped", "WEBHOOK_URL not set")

    return results
