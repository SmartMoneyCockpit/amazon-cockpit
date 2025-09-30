import streamlit as st

st.set_page_config(page_title="Amazon Cockpit", layout="wide")

st.title("Amazon Cockpit — Core Smoke Test")
st.write("✅ If you can see this on Render, your deployment wiring is good.")

with st.sidebar:
    st.header("Quick Links")
    st.write("This is a placeholder sidebar. We'll swap in real modules next.")

col1, col2 = st.columns(2)
with col1:
    st.subheader("KPIs (placeholder)")
    st.metric("Products Tracked", 0)
    st.metric("Keywords Tracked", 0)
with col2:
    st.subheader("System Status")
    st.success("Streamlit app running on Render")
