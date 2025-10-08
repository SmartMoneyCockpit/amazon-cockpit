#!/usr/bin/env python3
"""
Hotfix for missing 'gspread' on Render and to prevent app crash at import-time.

What it does:
1) requirements.txt: ensure gspread + google-auth deps are present
2) app.py: guard 'SheetsClient' import so missing gspread won't crash the UI
3) add infra/sheets_safe.py (stub) and fall back to it if gspread isn't available

Idempotent: safe to run multiple times.
"""
import os, re, sys

APP = "app.py"
REQ = "requirements.txt"
SAFE = os.path.join("infra","sheets_safe.py")

REQ_LINES = [
    "gspread>=5.7.0",
    "google-auth>=2.20.0",
    "google-auth-oauthlib>=1.0.0"
]

SAFE_IMPL = """# Auto-generated safe stub (no gspread import required)
from __future__ import annotations
class SheetsClient:
    def __init__(self, *args, **kwargs):
        self.available = False
        self.reason = "gspread not installed or Google credentials not configured"
    def test_connection(self):
        return {"ok": False, "reason": self.reason}
"""

def ensure_requirements():
    changed = False
    if not os.path.exists(REQ):
        with open(REQ, "w", encoding="utf-8") as f:
            f.write("\n".join(REQ_LINES) + "\n")
        return True, "created requirements.txt with gsheets deps"
    with open(REQ, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.read().splitlines()
    for need in REQ_LINES:
        if not any(l.strip().startswith(need.split(">=")[0]) for l in lines):
            lines.append(need)
            changed = True
    if changed:
        with open(REQ, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        return True, "appended gsheets deps to requirements.txt"
    return False, "requirements already OK"

def ensure_safe_stub():
    os.makedirs(os.path.dirname(SAFE), exist_ok=True)
    if not os.path.exists(SAFE):
        with open(SAFE, "w", encoding="utf-8") as f:
            f.write(SAFE_IMPL)
        return True, "added infra/sheets_safe.py"
    return False, "stub already exists"

def patch_app_py():
    if not os.path.exists(APP):
        return False, "app.py missing"
    with open(APP, "r", encoding="utf-8", errors="ignore") as f:
        src = f.read()

    # 1) Guard import of SheetsClient
    if "from infra.sheets_client import SheetsClient" in src and "sheets_safe" not in src:
        src = src.replace(
            "from infra.sheets_client import SheetsClient",
            "try:\n    from infra.sheets_client import SheetsClient\nexcept Exception:\n    from infra.sheets_safe import SheetsClient"
        )
        guarded = True
    else:
        guarded = False

    # 2) Early CSS hide so default nav doesn't take over if later code fails
    css_snip = "[data-testid=\"stSidebarNav\"] { display:none !important; }"
    if css_snip not in src:
        prepend = (
            "import streamlit as st\n"
            "st.set_page_config(page_title=\"Vega Cockpit\", layout=\"wide\", initial_sidebar_state=\"expanded\")\n"
            "st.markdown(\"\"\"\n"
            "<style>\n"
            "[data-testid=\\\"stSidebarNav\\\"] { display:none !important; }\n"
            "</style>\n"
            "\"\"\", unsafe_allow_html=True)\n"
        )
        if "st.set_page_config" not in src.splitlines()[0:10]:
            src = prepend + "\n" + src
            css_added = True
        else:
            src = src.replace("st.set_page_config", prepend + "st.set_page_config", 1)
            css_added = True
    else:
        css_added = False

    if guarded or css_added:
        with open(APP, "w", encoding="utf-8") as f:
            f.write(src)
        return True, f"patched app.py (guarded import={'yes' if guarded else 'no'}, css={'yes' if css_added else 'no'})"
    return False, "app.py already patched"

def main():
    r1 = ensure_requirements()
    r2 = ensure_safe_stub()
    r3 = patch_app_py()
    for label, res in [("requirements", r1), ("safe_stub", r2), ("app_py", r3)]:
        print(f"{label}: {'OK' if res[0] else 'skip'} — {res[1]}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
