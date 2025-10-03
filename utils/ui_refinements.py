
from __future__ import annotations
import os
import streamlit as st

# ---- Light CSS injection (call once at top of a page) ----
def inject_css():
    st.markdown("""
    <style>
    .badge { display:inline-block; padding:2px 8px; border-radius:999px; font-size:12px; font-weight:600; }
    .sev-red { background:#ffe6e6; color:#b30000; }
    .sev-yellow { background:#fff6e6; color:#8a5a00; }
    .sev-green { background:#e7f7ee; color:#0b7a3b; }
    .pill { background:#eef2f7; color:#334155; }
    .muted { color:#6b7280; font-size:12px; }
    .link-btn a { text-decoration:none; padding:6px 10px; border:1px solid #e5e7eb; border-radius:8px; }
    </style>
    """, unsafe_allow_html=True)

# ---- Severity badge ----
def sev_badge(sev: str) -> str:
    sev = (sev or "").lower()
    cls = "sev-yellow"
    if sev == "red": cls = "sev-red"
    elif sev == "green": cls = "sev-green"
    return f'<span class="badge {cls}">{sev or "—"}</span>'

# ---- Generic pill ----
def pill(text: str) -> str:
    return f'<span class="badge pill">{text}</span>'

# ---- Jump to Google Sheet tab (if SB exposes display_url) ----
def sheet_link(tab_name: str) -> str:
    """Returns an HTML anchor link to open the Google Sheet tab, if possible; else a muted label."""
    try:
        from utils import sheets_bridge as SB  # expected to have display_url(tab) or doc url
        url = None
        if hasattr(SB, "display_url"):
            try:
                url = SB.display_url(tab_name)
            except Exception:
                url = None
        if not url:
            # Fallback to DOC url and mention tab name
            doc_id = os.getenv("SHEETS_DOC_ID","")
            if doc_id:
                url = f"https://docs.google.com/spreadsheets/d/{doc_id}"
        if url:
            return f'<span class="link-btn"><a href="{url}" target="_blank">Open Sheet: {tab_name}</a></span>'
    except Exception:
        pass
    return f'<span class="muted">Sheet: {tab_name}</span>'
