
from __future__ import annotations
import os, json, base64, hashlib, typing as t
import pandas as pd

STATE_PATH = os.getenv("ALERTS_NOTIFY_STATE", "/tmp/alerts_notify_state.json")

def _read_tab(name: str) -> pd.DataFrame:
    try:
        from utils import sheets_bridge as SB
        df = SB.read_tab(name)
        if isinstance(df, pd.DataFrame):
            df.columns = [c.strip().lower() for c in df.columns]
            return df
    except Exception:
        pass
    return pd.DataFrame()

def _summarize() -> dict:
    """Load current alerts and build a compact summary dict."""
    data = {}
    tabs = {
        "low_doc": "alerts_out_low_doc",
        "compliance": "alerts_out_compliance",
        "ppc": "alerts_out_ppc",
        "margins": "alerts_out_margins",
        "revenue_prot": "alerts_out_revenue_protection",
        "actions": "actions_out",
    }
    for k, v in tabs.items():
        df = _read_tab(v)
        data[k] = {
            "count": 0 if df.empty else int(len(df)),
            "sample": [] if df.empty else df.head(5).to_dict(orient="records"),
        }
    return data

def _fingerprint(payload: dict) -> str:
    """Hash of the key signal so we only send when it changes."""
    # Use counts + top details (type/key/reason if present)
    def clean_rows(rows):
        cleaned = []
        for r in rows:
            cleaned.append({k: r.get(k) for k in list(r.keys())[:6]})
        return cleaned
    sig = {
        "low_doc": (payload["low_doc"]["count"], clean_rows(payload["low_doc"]["sample"])),
        "compliance": (payload["compliance"]["count"], clean_rows(payload["compliance"]["sample"])),
        "ppc": (payload["ppc"]["count"], clean_rows(payload["ppc"]["sample"])),
        "margins": (payload["margins"]["count"], clean_rows(payload["margins"]["sample"])),
        "revenue_prot": (payload["revenue_prot"]["count"], clean_rows(payload["revenue_prot"]["sample"])),
        "actions": (payload["actions"]["count"], clean_rows(payload["actions"]["sample"])),
    }
    raw = json.dumps(sig, sort_keys=True).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()

def _load_state() -> dict:
    if not os.path.exists(STATE_PATH):
        return {}
    try:
        with open(STATE_PATH, "r") as f:
            return json.load(f)
    except Exception:
        return {}

def _save_state(state: dict):
    try:
        with open(STATE_PATH, "w") as f:
            json.dump(state, f)
    except Exception:
        pass

# -------- Senders --------
def _send_email(subject: str, html: str) -> t.Tuple[str, str]:
    """Send via SendGrid if env vars present."""
    import requests
    api_key = os.getenv("SENDGRID_API_KEY","").strip()
    email_from = os.getenv("DIGEST_EMAIL_FROM","").strip() or os.getenv("ALERTS_EMAIL_FROM","").strip()
    email_to   = os.getenv("DIGEST_EMAIL_TO","").strip() or os.getenv("ALERTS_EMAIL_TO","").strip()
    if not api_key or not email_from or not email_to:
        return ("skipped", "missing SENDGRID_API_KEY / *_EMAIL_FROM / *_EMAIL_TO")
    data = {
        "personalizations": [ {"to": [{"email": email_to}]} ],
        "from": {"email": email_from},
        "subject": subject,
        "content": [{"type": "text/html", "value": html}],
    }
    try:
        resp = requests.post(
            "https://api.sendgrid.com/v3/mail/send",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            data=json.dumps(data)
        )
        if 200 <= resp.status_code < 300:
            return ("ok", f"sent to {email_to}")
        return ("error", f"sendgrid {resp.status_code}: {resp.text[:200]}")
    except Exception as e:
        return ("error", str(e))

def _send_webhook(payload: dict) -> t.Tuple[str, str]:
    import requests
    url = os.getenv("WEBHOOK_URL","").strip() or os.getenv("ALERTS_WEBHOOK_URL","").strip()
    if not url:
        return ("skipped", "WEBHOOK_URL not set")
    try:
        resp = requests.post(url, json=payload, timeout=15)
        if 200 <= resp.status_code < 300:
            return ("ok", f"webhook {resp.status_code}")
        return ("error", f"webhook {resp.status_code}: {resp.text[:200]}")
    except Exception as e:
        return ("error", str(e))

def _html_from_payload(p: dict) -> str:
    def row(r: dict) -> str:
        kv = ", ".join(f"{k}={v}" for k,v in r.items() if v is not None)[:180]
        return f"<li>{kv}</li>"
    parts = ["<h3>New alerts detected</h3>"]
    for sec in ["low_doc","compliance","ppc","margins","revenue_prot","actions"]:
        c = p[sec]["count"]
        if c > 0:
            sample = "".join(row(x) for x in p[sec]["sample"])
            parts.append(f"<p><b>{sec.replace('_',' ').title()}</b>: {c}</p><ul>{sample}</ul>")
    return "".join(parts)

def notify_if_new(subject_prefix: str = "Alerts Update") -> dict:
    """Compare with last sent; if changed, send email/webhook and update state."""
    payload = _summarize()
    fp = _fingerprint(payload)
    state = _load_state()
    if state.get("last_fp") == fp:
        return {"status": "no_change", "details": "same fingerprint; not sending"}
    # Compose & send
    html = _html_from_payload(payload)
    results = {}
    results["email"] = _send_email(f"{subject_prefix}", html)
    results["webhook"] = _send_webhook({"type":"alerts_update", "payload": payload})
    # Save state
    state["last_fp"] = fp
    _save_state(state)
    results["status"] = "sent"
    return results


# --- [66–70] Resend latest alerts (bypass fingerprint) ---
def resend_latest(subject_prefix: str = "Alerts Update (Re-send)") -> dict:
    """Rebuild current payload and send email/webhook without touching fingerprint state."""
    payload = _summarize()
    html = _html_from_payload(payload)
    results = {}
    results["email"] = _send_email(f"{subject_prefix}", html)
    results["webhook"] = _send_webhook({"type":"alerts_update_resend", "payload": payload})
    results["status"] = "sent"
    return results
