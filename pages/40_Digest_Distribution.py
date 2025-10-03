
import os
import streamlit as st

from utils.auth import gate
import utils.security as sec
from utils.distribute import distribute_today, _paths_for_today

st.set_page_config(page_title="Digest Distribution", layout="wide")
sec.enforce()
if not gate(required_admin=True):
    st.stop()

st.title("📤 Digest Distribution (Email / Webhook)")

st.subheader("Env Check")
st.write({
    "SENDGRID_API_KEY": "set" if os.getenv("SENDGRID_API_KEY") else "—",
    "DIGEST_EMAIL_FROM": os.getenv("DIGEST_EMAIL_FROM","—"),
    "DIGEST_EMAIL_TO": os.getenv("DIGEST_EMAIL_TO","—"),
    "WEBHOOK_URL": os.getenv("WEBHOOK_URL","—"),
    "DIGEST_OUT_DIR": os.getenv("DIGEST_OUT_DIR","/tmp"),
})

st.subheader("Today’s artifacts")
paths = _paths_for_today()
st.json(paths if paths else {"info": "No digest artifacts found today in /tmp. Generate via Daily Digest page."})

if st.button("Send Now"):
    res = distribute_today()
    st.json(res)
