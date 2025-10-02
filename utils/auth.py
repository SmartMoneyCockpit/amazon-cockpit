
from __future__ import annotations
import os
import streamlit as st
from typing import Optional

ADMIN_EMAIL = os.getenv("APP_ADMIN_EMAIL", "").strip().lower()
LOGIN_EMAIL = os.getenv("APP_LOGIN_EMAIL", "").strip().lower()
LOGIN_PASSWORD = os.getenv("APP_LOGIN_PASSWORD", "")

def _login_form():
    with st.form("login_form", clear_on_submit=False):
        st.subheader("Sign in")
        email = st.text_input("Email", value=st.session_state.get("_login_email",""))
        password = st.text_input("Password", type="password")
        ok = st.form_submit_button("Log in")
    if ok:
        st.session_state["_login_email"] = email
        return {"email": email.strip().lower(), "password": password}
    return None

def _role_for(email: str) -> str:
    if email and ADMIN_EMAIL and email.lower() == ADMIN_EMAIL:
        return "admin"
    return "viewer"

def _check_creds(email: str, password: str) -> bool:
    if LOGIN_EMAIL and LOGIN_PASSWORD:
        return (email.lower() == LOGIN_EMAIL and password == LOGIN_PASSWORD)
    return bool(email and password)

def gate(required_admin: bool = False) -> bool:
    user = st.session_state.get("_auth_user")
    if user:
        if required_admin and user.get("role") != "admin":
            st.error("Admin access required.")
            return False
        with st.sidebar:
            st.caption(f"Signed in as **{user.get('email','')}** ({user.get('role')})")
            if st.button("Log out"):
                st.session_state.pop("_auth_user", None)
                st.rerun()
        return True

    creds = _login_form()
    if creds:
        if _check_creds(creds["email"], creds["password"]):
            role = _role_for(creds["email"])
            st.session_state["_auth_user"] = {"email": creds["email"], "role": role}
            st.experimental_rerun()
        else:
            st.error("Invalid credentials.")
    return False
