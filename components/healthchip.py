
from __future__ import annotations
import streamlit as st
def _check_sheets():
    try:
        from infra.sheets_client import SheetsClient
        sc=SheetsClient(); sc.read_table("Settings"); return "ok","Google Sheets: OK"
    except Exception as e:
        msg=str(e).lower()
        if any(k in msg for k in ["missing","not configured","credential","key","not found"]): return "warn","Google Sheets: not configured"
        return "error", f"Google Sheets: {e}"
def render_healthchip():
    status,msg=_check_sheets(); color={"ok":"#16a34a","warn":"#f59e0b","error":"#ef4444"}.get(status,"#6b7280"); label={"ok":"Healthy","warn":"Needs Setup","error":"Issue"}.get(status,"Unknown")
    chip=f"""<div style='display:inline-flex;align-items:center;gap:.5rem;padding:.25rem .5rem;border-radius:999px;background-color:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.08);'><span style='display:inline-block;width:.6rem;height:.6rem;border-radius:999px;background:{color};'></span><span style='font-size:.85rem;'>{label}</span></div>"""
    st.markdown(chip, unsafe_allow_html=True); st.caption(msg)
