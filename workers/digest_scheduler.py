
from __future__ import annotations
import os, sys, datetime as dt, pathlib
from typing import Optional

from utils.logs import log_job
from utils.digest_formatter import read_queue, build_plaintext_summary, build_markdown_summary

# SendGrid optional
try:
    from utils.email_sendgrid import send_email, SendGridError  # type: ignore
except Exception:
    send_email = None
    class SendGridError(Exception): ...  # fallback

def _get_secret_like(key: str) -> Optional[str]:
    """Try st.secrets first (if running in Streamlit), then environment variables."""
    try:
        import streamlit as st  # type: ignore
        val = st.secrets.get(key, None)
        if val:
            return str(val)
    except Exception:
        pass
    return os.getenv(key, None)

def _write_fallback_file(txt: str) -> str:
    d = dt.date.today().isoformat()
    out_dir = pathlib.Path("snapshots") / "digest" / d
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "daily_digest.txt"
    out_file.write_text(txt, encoding="utf-8")
    return out_file.as_posix()

def run_digest_scheduler(send_email_enabled: bool = True) -> int:
    try:
        rows = read_queue()
        txt = build_plaintext_summary(rows)
        md = build_markdown_summary(rows)

        # If no alerts, still write a file and log 'ok:empty'
        saved_to = _write_fallback_file(txt)

        # Try email if configured and enabled
        if send_email_enabled and send_email is not None:
            api_key = _get_secret_like("SENDGRID_API_KEY")
            from_email = _get_secret_like("EMAIL_FROM")
            to_email = _get_secret_like("EMAIL_TO")
            subject = f"Vega Daily Digest — {dt.date.today().isoformat()}"
            html_body = f"<pre>{md}</pre>"
            if api_key and from_email and to_email:
                try:
                    code = send_email(api_key, from_email, to_email, subject, txt, html_body)
                    if 200 <= code < 300:
                        log_job("digest_scheduler", "ok", f"Email sent (status {code}); saved {saved_to}")
                        print(f"[digest_scheduler] OK email={code} file={saved_to}")
                        return 0
                    else:
                        log_job("digest_scheduler", "error", f"Email status {code}; saved {saved_to}")
                        print(f"[digest_scheduler] ERROR email={code} file={saved_to}")
                        return 1
                except SendGridError as e:
                    log_job("digest_scheduler", "error", f"SendGridError: {e}; saved {saved_to}")
                    print(f"[digest_scheduler] ERROR SendGridError={e} file={saved_to}")
                    return 1

        # No email configured / disabled: just file output OK
        # If there are truly no alerts, note it—but treat as OK
        status_detail = "empty queue" if ("No alerts queued yet" in md) else "file-only"
        log_job("digest_scheduler", "ok", f"{status_detail}; saved {saved_to}")
        print(f"[digest_scheduler] OK {status_detail} file={saved_to}")
        return 0

    except Exception as e:
        log_job("digest_scheduler", "error", f"{e!r}")
        print(f"[digest_scheduler] ERROR {e!r}")
        return 1

def main(argv: list[str]) -> int:
    # Usage: python -m workers.digest_scheduler [--no-email]
    send = True
    if len(argv) > 1 and argv[1] == "--no-email":
        send = False
    return run_digest_scheduler(send_email_enabled=send)

if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
