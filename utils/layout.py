import streamlit as st

def section_header(title: str):
    st.markdown(f"### {title}")

def kpi(label: str, value, help: str = None):
    with st.container():
        cols = st.columns([1,1])
        with cols[0]:
            st.metric(label, value, help=help if help else None)
