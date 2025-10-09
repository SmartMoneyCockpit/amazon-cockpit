import streamlit as st
from services.amazon_ads_service import get_profiles, _db, DATA_DIR

st.set_page_config(page_title="Vega Health", layout="wide")
st.title("Vega Cockpit — Health Check")

st.info(f"Data directory in use: **{DATA_DIR}**")

ok = True
try:
    prof = get_profiles()
    st.success("✔️ Amazon token & profile OK")
    st.json(prof)
except Exception as e:
    ok = False
    st.error(f"Amazon auth error: {e}")

try:
    con = _db()
    con.execute("select 1")
    con.close()
    st.success("✔️ DB OK")
except Exception as e:
    ok = False
    st.error(f"DB error: {e}")

if ok:
    st.success("System healthy.")
else:
    st.warning("Something needs attention.")
