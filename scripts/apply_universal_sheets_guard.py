#!/usr/bin/env python3
"""
Universal Sheets Guard + Global Sidebar CSS (idempotent).
- Guards all occurrences of `from infra.sheets_client import SheetsClient` in /pages/*.py and app.py
  with a try/except fallback to `infra.sheets_safe.SheetsClient`.
- Patches infra/sheets_client.py to lazy-import gspread and expose a valid SheetsClient even if missing,
  with an env override `VEGA_DISABLE_SHEETS=1`.
- Ensures requirements.txt has gspread + google-auth lines (add-only).
- Injects early CSS + set_page_config at the top of every page to keep the custom folder sidebar.
Run from the repo root.
"""
import os, sys, re

CSS_BLOCK = (
    "import streamlit as st\n"
    "st.set_page_config(page_title='Vega Cockpit', layout='wide', initial_sidebar_state='expanded')\n"
    "st.markdown('''\\\n<style>[data-testid=\"stSidebarNav\"] { display:none !important; }</style>\n''' , unsafe_allow_html=True)\n"
)

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

def ensure_safe_stub():
    p="infra/sheets_safe.py"
    if not os.path.exists(p):
        os.makedirs("infra", exist_ok=True)
        with open(p,"w",encoding="utf-8") as f:
            f.write("from __future__ import annotations\nclass SheetsClient:\n    def __init__(self,*a,**k): self.available=False; self.reason='gspread not installed or disabled'\n    def test_connection(self): return {'ok':False,'reason':self.reason}\n")
        print("infra/sheets_safe.py: added")
    else:
        print("infra/sheets_safe.py: ok")

def patch_sheets_client():
    path="infra/sheets_client.py"
    try:
        src=open(path,"r",encoding="utf-8",errors="ignore").read()
    except FileNotFoundError:
        print("infra/sheets_client.py: missing (skip)"); return
    changed=False
    if "import gspread" in src and "VEGA_DISABLE_SHEETS" not in src:
        src = src.replace(
            "import gspread",
            "import os\ntry:\n    import gspread\nexcept Exception:\n    gspread=None"
        ); changed=True
    # make sure class has a disabled path
    if "def __init__(self" in src and "_disabled" not in src:
        src = re.sub(
            r"(class\s+SheetsClient\s*\(.*?\):\s*\n\s*def\s+__init__\(self,.*?\):)",
            r"\1\n        import os\n        self._disabled = (os.getenv('VEGA_DISABLE_SHEETS') == '1') or (gspread is None)",
            src, flags=re.S
        ); changed=True
    if changed:
        with open(path,"w",encoding="utf-8") as f: f.write(src)
        print("infra/sheets_client.py: guarded")
    else:
        print("infra/sheets_client.py: ok")

def guard_import_in_file(path):
    try:
        src=open(path,"r",encoding="utf-8",errors="ignore").read()
    except FileNotFoundError:
        return False, "missing"
    changed=False
    # Guard the SheetsClient import
    if "from infra.sheets_client import SheetsClient" in src and "sheets_safe" not in src:
        src = src.replace(
            "from infra.sheets_client import SheetsClient",
            "try:\n    from infra.sheets_client import SheetsClient\nexcept Exception:\n    from infra.sheets_safe import SheetsClient"
        )
        changed=True
    # Inject CSS at the very top if missing
    if "[data-testid=\"stSidebarNav\"] { display:none !important; }" not in src:
        # Prepend CSS
        src = CSS_BLOCK + "\n" + src
        changed=True
    if changed:
        with open(path,"w",encoding="utf-8") as f: f.write(src)
    return changed, "patched" if changed else "ok"

def patch_all_pages():
    patched=0
    root="pages"
    if not os.path.isdir(root):
        print("pages/: missing (skip)"); return 0
    for f in os.listdir(root):
        if not f.endswith(".py"): continue
        p=os.path.join(root,f)
        ok,msg=guard_import_in_file(p)
        if ok: patched+=1
        print(f"{p}: {msg}")
    return patched

def patch_app():
    ok,msg=guard_import_in_file("app.py")
    print(f"app.py: {msg}")

def main():
    ensure_requirements()
    ensure_safe_stub()
    patch_sheets_client()
    patch_all_pages()
    patch_app()
    print("DONE")
    return 0

if __name__=='__main__':
    sys.exit(main())
