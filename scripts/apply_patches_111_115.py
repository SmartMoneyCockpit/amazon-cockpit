#!/usr/bin/env python3
"""
Apply wiring for feature flags across known files in-place (idempotent).
- app.py: gate Developer Tools link on dev_tools_link_enabled (replaces previous appended link block if present)
- pages/31_Alerts_Center.py: default auto-refresh seconds from flags if field exists
- pages/34_Daily_Digest.py: default attachments toggle from flags (session default)
"""
import os, re, sys
def read(path):
    try:
        with open(path, 'r', encoding='utf-8') as f: return f.read()
    except Exception: return None
def write(path, txt):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f: f.write(txt)
def patch_app_py(path='app.py'):
    src = read(path)
    if src is None: return False, 'missing'
    pattern = r"# ---- Developer Tools link \(appended; keeps existing order\) ----[\s\S]*?except Exception:[\s\S]*?pass"
    repl = (
        "# ---- Developer Tools link (appended; keeps existing order, now flag-gated) ----\n"
        "try:\n"
        "    import os\n"
        "    from utils.feature_flags import load_flags  # type: ignore\n"
        "    flags = load_flags()\n"
        "    if flags.get('dev_tools_link_enabled', True):\n"
        "        with st.expander('Utilities', expanded=False):\n"
        "            if os.path.exists('pages/45_Developer_Tools.py'):\n"
        "                st.page_link('pages/45_Developer_Tools.py', label='Developer Tools')\n"
        "except Exception:\n"
        "    pass"
    )
    if re.search(pattern, src):
        new = re.sub(pattern, repl, src, flags=re.M)
        if new != src:
            write(path, new); return True, 'replaced legacy link block'
    else:
        if 'pages/45_Developer_Tools.py' not in src:
            new = src + "\n\n" + repl + "\n"
            write(path, new); return True, 'appended gated link'
    return False, 'unchanged'
def append_block(path, block, marker):
    src = read(path)
    if src is None: return False, 'missing'
    if marker in src: return False, 'already'
    write(path, src + "\n" + block)
    return True, 'appended'
def patch_alerts_center():
    block = (
        "# --- [111–115] flags wiring (alerts default interval) ---\n"
        "try:\n"
        "    from utils.feature_flags import load_flags\n"
        "    import streamlit as _st\n"
        "    flags = load_flags()\n"
        "    _def = int(flags.get('alerts_auto_refresh_default_secs', 0))\n"
        "    _st.caption(f'Default auto-refresh (secs) from flags: {_def}')\n"
        "except Exception:\n"
        "    pass\n"
    )
    return append_block('pages/31_Alerts_Center.py', block, '[111–115] flags wiring (alerts default interval)')
def patch_digest_page():
    block = (
        "# --- [111–115] flags wiring (digest attachments default) ---\n"
        "try:\n"
        "    import streamlit as _st\n"
        "    from utils.feature_flags import load_flags\n"
        "    flags = load_flags()\n"
        "    if 'digest_attach' not in _st.session_state:\n"
        "        _st.session_state['digest_attach'] = bool(flags.get('digest_attachments_default', False))\n"
        "except Exception:\n"
        "    pass\n"
    )
    return append_block('pages/34_Daily_Digest.py', block, '[111–115] flags wiring (digest attachments default)')
def main():
    results = {}
    results['app.py'] = patch_app_py()
    results['pages/31_Alerts_Center.py'] = patch_alerts_center()
    results['pages/34_Daily_Digest.py'] = patch_digest_page()
    for k,(ok,msg) in results.items():
        print(f"{k}: {'OK' if ok else 'skip'} — {msg}")
    return 0
if __name__ == '__main__':
    import sys; sys.exit(main())
