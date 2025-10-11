import streamlit as st
st.set_page_config(page_title="health", layout="centered", initial_sidebar_state="collapsed")
# Quick 'health' view; useful if you point Render's health check to '/?health=1' or similar.
st.write("ok")
