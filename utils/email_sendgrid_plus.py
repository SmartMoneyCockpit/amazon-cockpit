import os, base64, requests
API = "https://api.sendgrid.com/v3/mail/send"
def _cfg():
    return {
        "api_key": os.getenv("SENDGRID_API_KEY","").strip(),
        "email_from": os.getenv("DIGEST_EMAIL_FROM","").strip() or os.getenv("ALERTS_EMAIL_FROM","").strip(),
        "email_to": os.getenv("DIGEST_EMAIL_TO","").strip() or os.getenv("ALERTS_EMAIL_TO","").strip(),
    }
def send_with_optional_attachments(subject: str, html: str, attachments=None):
    cfg = _cfg()
    if not cfg["api_key"] or not cfg["email_from"] or not cfg["email_to"]:
        return {"status":"skipped","message":"missing SENDGRID_API_KEY/from/to"}
    data = {
        "personalizations":[{"to":[{"email": cfg["email_to"]}]}],
        "from":{"email": cfg["email_from"]},
        "subject": subject,
        "content":[{"type":"text/html","value": html}],
    }
    atts = []
    for att in attachments or []:
        try:
            path = att.get("path"); name = att.get("name") or os.path.basename(path)
            with open(path, "rb") as f:
                b64 = base64.b64encode(f.read()).decode("ascii")
            atts.append({"content": b64, "filename": name, "type": "application/octet-stream"})
        except Exception:
            continue
    if atts:
        data["attachments"] = atts
    resp = requests.post(API, headers={"Authorization": f"Bearer {cfg['api_key']}"}, json=data, timeout=20)
    return {"status": "ok" if 200 <= resp.status_code < 300 else "error", "code": resp.status_code, "body": resp.text[:200]}
