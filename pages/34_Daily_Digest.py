
import os, json, datetime as dt
import pandas as pd
import streamlit as st
from utils.digest_formatter import read_queue, build_markdown_summary, build_plaintext_summary

try:
    from utils.email_sendgrid import send_email, SendGridError
except Exception:
    send_email = None
    SendGridError = Exception

st.set_page_config(page_title="Daily Digest", layout="wide")
st.title("Daily Digest")

DIGEST_FILE = os.path.join("alerts", "digest_queue.jsonl")
os.makedirs("alerts", exist_ok=True)

rows = read_queue(DIGEST_FILE)

def _rule_name(r):
    if not isinstance(r, dict):
        return ""
    return r.get("name") or f"{r.get('metric')} {r.get('operator')} {r.get('threshold')}"

all_metrics = sorted({ (r.get("rule") or {}).get("metric","") for r in rows if isinstance(r, dict)} - {""})
all_types = sorted({ r.get("type","") for r in rows if isinstance(r, dict)} - {""})

fc1, fc2, fc3 = st.columns([1,1,2])
with fc1:
    f_metrics = st.multiselect("Filter metrics", all_metrics, default=all_metrics)
with fc2:
    f_types = st.multiselect("Filter types", all_types, default=all_types)
with fc3:
    st.caption("Filters apply to both the table and the summary below.")

def _apply_filters(rows, metrics, types):
    if not rows: return []
    out = []
    for r in rows:
        rule = r.get("rule") or {}
        metric = rule.get("metric","")
        typ = r.get("type","")
        if metrics and metric not in metrics: continue
        if types and typ not in types: continue
        out.append(r)
    return out

rows_f = _apply_filters(rows, f_metrics, f_types)

def _format_rows(rows):
    if not rows:
        return pd.DataFrame(columns=["ts", "type", "rule", "reason"])
    data = []
    for r in rows:
        ts = r.get("ts")
        typ = r.get("type")
        rule = r.get("rule", {})
        reason = r.get("reason", "")
        data.append({
            "ts": ts, "type": typ, "rule": _rule_name(rule), "reason": reason
        })
    df = pd.DataFrame(data)
    if not df.empty:
        try:
            df["ts_parsed"] = pd.to_datetime(df["ts"], errors="coerce")
            df = df.sort_values("ts_parsed", ascending=False).drop(columns=["ts_parsed"])
        except Exception:
            pass
    return df

df = _format_rows(rows_f)

c1, c2, c3, c4 = st.columns([1,1,1,2])
with c1:
    if st.button("Refresh"):
        st.experimental_rerun()
with c2:
    if st.button("Clear Queue"):
        try:
            open(DIGEST_FILE, "w", encoding="utf-8").close()
            st.success("Digest queue cleared.")
            st.experimental_rerun()
        except Exception as e:
            st.error(f"Could not clear queue: {e}")
with c3:
    txt_summary = build_plaintext_summary(rows_f)
    st.download_button("Download TXT", data=txt_summary.encode("utf-8"),
                       file_name=f"digest_{dt.date.today().isoformat()}.txt", mime="text/plain")
with c4:
    md_summary = build_markdown_summary(rows_f)
    copy_html = """
    <button id='copyBtn' style='padding:6px 12px;border-radius:6px;border:1px solid #ddd;cursor:pointer;'>Copy Summary</button>
    <script>
    const txt = %s;
    const btn = document.getElementById('copyBtn');
    btn.addEventListener('click', async () => {
        try {
            await navigator.clipboard.writeText(txt);
            btn.innerText = 'Copied!';
            setTimeout(() => btn.innerText = 'Copy Summary', 1200);
        } catch (e) {
            btn.innerText = 'Copy failed';
            setTimeout(() => btn.innerText = 'Copy Summary', 1200);
        }
    });
    </script>
    """ % (json.dumps(txt_summary))
    st.components.v1.html(copy_html, height=40)

st.divider()
st.subheader("Queued Alerts")
if df.empty:
    st.info("No alerts queued yet. Use Alerts Center → Evaluate Now to add items.")
else:
    st.dataframe(df, use_container_width=True)

st.divider()
st.subheader("Summary Preview")
st.markdown(md_summary)

# Email via SendGrid (reads defaults from secrets if present)
st.divider()
st.subheader("Email Digest (SendGrid)")
api_key = None; from_email = None; to_email = None
try:
    api_key = st.secrets.get("SENDGRID_API_KEY", None)
    from_email = st.secrets.get("EMAIL_FROM", None)
    to_email = st.secrets.get("EMAIL_TO", None)
except Exception:
    pass

with st.form("sendgrid_form"):
    col1, col2 = st.columns(2)
    with col1:
        api_key = st.text_input("SENDGRID_API_KEY", value=api_key or "", type="password")
        from_email = st.text_input("From email", value=from_email or "")
    with col2:
        to_email = st.text_input("To email", value=to_email or "")
        subject = st.text_input("Subject", value=f"Vega Daily Digest — {dt.date.today().isoformat()}")
    html_body = st.text_area("HTML body (optional)", value=f"<pre>{md_summary}</pre>", height=160)
    submit = st.form_submit_button("Send Test Email")

if submit:
    if not send_email:
        st.error("SendGrid helper not available.")
    elif not api_key or not from_email or not to_email:
        st.error("Please provide API key, From email, and To email.")
    else:
        try:
            code = send_email(api_key, from_email, to_email, subject, txt_summary, html_body)
            if code == 202:
                st.success("Email accepted by SendGrid (202). Check your inbox.")
            else:
                st.warning(f"Unexpected status: {code}")
        except SendGridError as e:
            st.error(f"SendGrid error: {e}")
        except Exception as e:
            st.error(f"Failed to send: {e}")
