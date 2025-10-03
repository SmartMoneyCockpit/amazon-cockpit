
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
