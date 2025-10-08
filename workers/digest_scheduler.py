
from __future__ import annotations
import os, sys, datetime as dt, pathlib
from utils.logs import log_job
from utils.digest_formatter import read_queue, build_plaintext_summary, build_markdown_summary
try:
    from utils.email_sendgrid import send_email, SendGridError
except Exception:
    send_email=None; 
    class SendGridError(Exception): ...
def _get_secret_like(key: str):
    try:
        import streamlit as st; val=st.secrets.get(key, None); 
        if val: return str(val)
    except Exception: pass
    return os.getenv(key, None)
def _write_fallback_file(txt: str)->str:
    d=dt.date.today().isoformat(); out_dir=pathlib.Path("snapshots")/"digest"/d; out_dir.mkdir(parents=True, exist_ok=True); out_file=out_dir/"daily_digest.txt"; out_file.write_text(txt, encoding="utf-8"); return out_file.as_posix()
def run_digest_scheduler(send_email_enabled: bool=True)->int:
    try:
        rows=read_queue(); txt=build_plaintext_summary(rows); md=build_markdown_summary(rows); saved_to=_write_fallback_file(txt)
        if send_email_enabled and send_email is not None:
            api=_get_secret_like("SENDGRID_API_KEY"); frm=_get_secret_like("EMAIL_FROM"); to=_get_secret_like("EMAIL_TO"); subject=f"Vega Daily Digest — {dt.date.today().isoformat()}"; html=f"<pre>{md}</pre>"
            if api and frm and to:
                try:
                    code=send_email(api, frm, to, subject, txt, html); 
                    if 200<=code<300: log_job("digest_scheduler","ok", f"Email {code}; saved {saved_to}"); return 0
                    else: log_job("digest_scheduler","error", f"Email status {code}; saved {saved_to}"); return 1
                except SendGridError as e: log_job("digest_scheduler","error", f"SendGridError: {e}; saved {saved_to}"); return 1
        status_detail="empty queue" if ("No alerts queued yet" in md) else "file-only"; log_job("digest_scheduler","ok", f"{status_detail}; saved {saved_to}"); return 0
    except Exception as e: log_job("digest_scheduler","error", f"{e!r}"); return 1
def main(argv:list[str])->int:
    send=True
    if len(argv)>1 and argv[1]=="--no-email": send=False
    return run_digest_scheduler(send)
if __name__=="__main__": raise SystemExit(main(sys.argv))


from utils.digest_runner import run_digest

def main():
    return run_digest(subject_prefix="Vega Daily Digest")

if __name__ == "__main__":
    main()
