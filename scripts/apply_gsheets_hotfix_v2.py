#!/usr/bin/env python3
"""Hotfix v2 for 'gspread' import crash + sidebar layout."""
import os, sys, re

REQ_LINES = [
    "gspread>=5.7.0",
    "google-auth>=2.20.0",
    "google-auth-oauthlib>=1.0.0",
]

def ensure_requirements():
    path="requirements.txt"
    try:
        lines=open(path,"r",encoding="utf-8",errors="ignore").read().splitlines()
    except FileNotFoundError:
        lines=[]
    changed=False
    for need in REQ_LINES:
        base=need.split(">=")[0]
        if not any(l.strip().startswith(base) for l in lines):
            lines.append(need); changed=True
    if changed:
        with open(path,"w",encoding="utf-8") as f: f.write("\n".join(lines)+"\n")
    print(f"requirements.txt: {'updated' if changed else 'ok'}")

def patch_sheets_client():
    path="infra/sheets_client.py"
    try:
        src=open(path,"r",encoding="utf-8",errors="ignore").read()
    except FileNotFoundError:
        print("infra/sheets_client.py: missing (skip)"); return
    if "import gspread" in src and "VEGA_DISABLE_SHEETS" not in src:
        src = src.replace(
            "import gspread",
            "import os\ntry:\n    import gspread\nexcept Exception:\n    gspread=None"
        )
        src = re.sub(
            r"(class\s+SheetsClient\s*\(.*?\):\s*\n\s*def\s+__init__\(self,.*?\):)",
            r"\1\n        if os.getenv('VEGA_DISABLE_SHEETS') == '1' or gspread is None:\n            self._disabled = True\n        else:\n            self._disabled = False",
            src, flags=re.S
        )
        with open(path,"w",encoding="utf-8") as f: f.write(src)
        print("infra/sheets_client.py: guarded import + env switch")
    else:
        print("infra/sheets_client.py: already guarded or no import found")

def ensure_safe_stub():
    p="infra/sheets_safe.py"
    if not os.path.exists(p):
        os.makedirs("infra", exist_ok=True)
        with open(p,"w",encoding="utf-8") as f:
            f.write("from __future__ import annotations\nclass SheetsClient:\n    def __init__(self,*a,**k): self.available=False; self.reason='gspread not installed or disabled'\n    def test_connection(self): return {'ok':False,'reason':self.reason}\n")
        print("infra/sheets_safe.py: added")
    else:
        print("infra/sheets_safe.py: ok")

def patch_app_py():
    path="app.py"
    try:
        src=open(path,"r",encoding="utf-8",errors="ignore").read()
    except FileNotFoundError:
        print("app.py: missing"); return
    changed=False
    if "from infra.sheets_client import SheetsClient" in src and "sheets_safe" not in src:
        src = src.replace(
            "from infra.sheets_client import SheetsClient",
            "try:\n    from infra.sheets_client import SheetsClient\nexcept Exception:\n    from infra.sheets_safe import SheetsClient"
        ); changed=True
    css_snip='[data-testid="stSidebarNav"] { display:none !important; }'
    if css_snip not in src:
        prepend = (            "import streamlit as st\n"
            "st.set_page_config(page_title='Vega Cockpit', layout='wide', initial_sidebar_state='expanded')\n"
            "st.markdown('''\\\n<style>[data-testid=\"stSidebarNav\"] { display:none !important; }</style>\n''' , unsafe_allow_html=True)\n"        )
        if "st.set_page_config" not in src.splitlines()[:15]:
            src = prepend + "\n" + src
        else:
            src = src.replace("st.set_page_config", prepend + "st.set_page_config", 1)
        changed=True
    if changed:
        with open(path,"w",encoding="utf-8") as f: f.write(src)
        print("app.py: patched (guarded import / CSS)")
    else:
        print("app.py: ok")

def main():
    ensure_requirements()
    ensure_safe_stub()
    patch_sheets_client()
    patch_app_py()
    print("DONE")
    return 0

if __name__=='__main__':
    sys.exit(main())
