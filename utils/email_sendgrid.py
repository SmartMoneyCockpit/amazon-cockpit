
from __future__ import annotations
from typing import Optional
import requests
SENDGRID_API_URL='https://api.sendgrid.com/v3/mail/send'
class SendGridError(Exception): pass
def send_email(api_key: str, from_email: str, to_email: str, subject: str, text: str, html: Optional[str]=None)->int:
    headers={'Authorization': f'Bearer {api_key}','Content-Type':'application/json'}
    payload={'personalizations':[{'to':[{'email': to_email}]}],'from':{'email': from_email},'subject': subject,'content':[{'type':'text/plain','value': text}]}
    if html: payload['content'].append({'type':'text/html','value': html})
    resp=requests.post(SENDGRID_API_URL, headers=headers, json=payload, timeout=15)
    if resp.status_code//100 != 2: raise SendGridError(f'SendGrid error {resp.status_code}: {resp.text[:300]}')
    return resp.status_code
