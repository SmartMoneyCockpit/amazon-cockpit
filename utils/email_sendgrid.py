"""
SendGrid guarded mailer (safe no-op if keys not configured).
"""
import os
from typing import Optional, Dict

def is_configured() -> bool:
    return bool(os.getenv("SENDGRID_API_KEY") and os.getenv("EMAIL_FROM") and os.getenv("EMAIL_TO"))

def send_email(subject: str, body_text: str, body_html: Optional[str]=None) -> Dict[str, str]:
    if not is_configured():
        return {"status":"skipped","reason":"sendgrid_not_configured"}
    try:
        import sendgrid
        from sendgrid.helpers.mail import Mail
        sg = sendgrid.SendGridAPIClient(api_key=os.getenv("SENDGRID_API_KEY"))
        msg = Mail(
            from_email=os.getenv("EMAIL_FROM"),
            to_emails=os.getenv("EMAIL_TO"),
            subject=subject,
            plain_text_content=body_text,
            html_content=body_html or body_text.replace("\n","<br/>"),
        )
        resp = sg.send(msg)
        code = getattr(resp,'status_code',None)
        return {"status":"ok","code":code}
    except Exception as e:
        return {"status":"error","error":str(e)}
