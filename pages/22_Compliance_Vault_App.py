
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import urllib.parse

st.set_page_config(page_title="Compliance Vault", layout="wide")
st.title("🧾 Compliance Vault")
st.caption("Track expiry dates and quickly compose vendor emails. Source: 'compliance' tab in your Google Sheet.")

SB = None
try:
    from utils import sheets_bridge as SB  # type: ignore
except Exception:
    SB = None

def load_df():
    if SB is not None:
        try:
            return SB.read_tab("compliance")
        except Exception as e:
            st.error(f"Couldn't read 'compliance' tab: {e}")
    up = st.file_uploader("Or upload compliance CSV", type=["csv"])
    if up:
        return pd.read_csv(up)
    return pd.DataFrame()

df = load_df()
if df.empty:
    st.info("Expected columns: asin, doc_type, issuer, issued_on, expires_on, link, notes")
    st.stop()

df.columns = [c.strip().lower() for c in df.columns]
for col in ["asin","doc_type","expires_on"]:
    if col not in df.columns:
        st.error("Missing required columns: asin, doc_type, expires_on")
        st.stop()

def to_date(x):
    try:
        return pd.to_datetime(x).date()
    except:
        return None

df["expires_on_dt"] = df["expires_on"].apply(to_date)
today = datetime.utcnow().date()
df["days_to_expiry"] = df["expires_on_dt"].apply(lambda d: (d - today).days if d else None)

def badge(days):
    if days is None: return "⬜ Unknown"
    if days < 0: return "🔴 Expired"
    if days <= 30: return "🟠 Due ≤30d"
    return "🟢 OK"

df["status"] = df["days_to_expiry"].apply(badge)

st.subheader("Summary")
c1,c2,c3,c4 = st.columns(4)
c1.metric("Total", len(df))
c2.metric("Expired", int((df["status"]=="🔴 Expired").sum()))
c3.metric("Due ≤30d", int((df["status"]=="🟠 Due ≤30d").sum()))
c4.metric("Healthy", int((df["status"]=="🟢 OK").sum()))

st.subheader("Records")
st.dataframe(df.drop(columns=["expires_on_dt"]), use_container_width=True, hide_index=True)

st.subheader("Compose Vendor Email")
default_to = st.text_input("To", "")
templ = ("Hello,\n\nOne or more documents for ASIN {asin} ({doc}) will expire on {date}. "
         "Please send updated documentation at your earliest convenience.\n\nThank you.")
row = st.selectbox("Pick a line to compose", options=df.index, format_func=lambda i: f"{df.loc[i,'asin']} • {df.loc[i,'doc_type']} • {df.loc[i,'status']}")
if row is not None:
    asin = df.loc[row,"asin"]
    doc = df.loc[row,"doc_type"]
    ex = df.loc[row,"expires_on"]
    body = templ.format(asin=asin, doc=doc, date=ex)
    subject = f"Compliance update request — ASIN {asin}"
    if st.button("Open mail draft"):
        url = f"mailto:{urllib.parse.quote(default_to)}?subject={urllib.parse.quote(subject)}&body={urllib.parse.quote(body)}"
        st.markdown(f"[Click to open email draft]({url})", unsafe_allow_html=True)
