
import os
import streamlit as st
from utils.auth import gate
import utils.security as sec
from utils.alerts_notify import notify_if_new, _summarize

st.set_page_config(page_title="Alerts Notifications", layout="wide")
sec.enforce()
if not gate(required_admin=True):
    st.stop()

st.title("🔔 Alerts Notifications (Email/Webhook)")

st.subheader("Env Check")
st.write({
    "SENDGRID_API_KEY": "set" if os.getenv("SENDGRID_API_KEY") else "—",
    "ALERTS_EMAIL_FROM": os.getenv("ALERTS_EMAIL_FROM","—"),
    "ALERTS_EMAIL_TO": os.getenv("ALERTS_EMAIL_TO","—"),
    "DIGEST_EMAIL_FROM": os.getenv("DIGEST_EMAIL_FROM","—"),
    "DIGEST_EMAIL_TO": os.getenv("DIGEST_EMAIL_TO","—"),
    "WEBHOOK_URL": os.getenv("WEBHOOK_URL","—"),
    "ALERTS_NOTIFY_STATE": os.getenv("ALERTS_NOTIFY_STATE","/tmp/alerts_notify_state.json"),
})

st.subheader("Current Alerts Snapshot")
st.json(_summarize())

if st.button("Send if changed (notify now)"):
    res = notify_if_new()
    st.json(res)


# --- Alert Status (added) ---
import os, json
import streamlit as st
from utils.logs_tail import tail_jsonl

STATE_PATH = os.getenv("ALERTS_NOTIFY_STATE", "/tmp/alerts_notify_state.json")

st.subheader("Alert Status")
last_lines = tail_jsonl(50)
last_alerts = [json.loads(x) for x in last_lines if '"job": "alerts_flush"' in x] if last_lines else []
last = json.loads(last_lines[-1]) if last_lines else {}
last_alert = last_alerts[-1] if last_alerts else {}

c1, c2, c3 = st.columns(3)
c1.metric("Last Job", last.get("job","—"))
c2.metric("Last Status", last.get("status","—"))
c3.metric("Alerts Flush", last_alert.get("status","—"))

with st.expander("State Fingerprint", expanded=False):
    try:
        st.code(STATE_PATH)
        if os.path.exists(STATE_PATH):
            st.code(open(STATE_PATH,"r",encoding="utf-8").read()[:2000])
        else:
            st.info("No state file yet.")
    except Exception as e:
        st.error(str(e))
