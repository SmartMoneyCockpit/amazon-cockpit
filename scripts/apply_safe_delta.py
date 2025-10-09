#!/usr/bin/env python3
# Safe additive patcher: applies fragments and ensures requirements lines.
import os, sys

def ensure_lines(path, lines):
    changed=False
    try:
        with open(path,'r',encoding='utf-8',errors='ignore') as f:
            src=f.read().splitlines()
    except FileNotFoundError:
        src=[]
    existing=set([l.strip() for l in src])
    for ln in lines:
        key=ln.split(">=")[0].strip() if ">=" in ln else ln.strip()
        if not any(x.strip().startswith(key) for x in src):
            src.append(ln)
            changed=True
    if changed:
        with open(path,'w',encoding='utf-8') as f: f.write("\n".join(src)+"\n")
    print(f"requirements.txt: {'updated' if changed else 'ok'}")
    return changed

def append_once(path, marker, block):
    try:
        src=open(path,'r',encoding='utf-8',errors='ignore').read()
    except FileNotFoundError:
        print(f"{path}: missing"); return False
    if marker in src:
        print(f"{path}: skip (already contains marker)")
        return False
    with open(path,'w',encoding='utf-8') as f:
        f.write(src+"\n"+block+"\n")
    print(f"{path}: appended")
    return True

def main():
    # 1) requirements
    ensure_lines('requirements.txt', ["gspread>=5.7.0", "google-auth>=2.20.0", "google-auth-oauthlib>=1.0.0", "streamlit>=1.31", "pandas>=2.0", "PyYAML>=6.0", "streamlit-autorefresh>=1.0; python_version >= \"3.8\""])
    # 2) app.py: ensure early CSS and modules panel
    try:
        app_src=open('app.py','r',encoding='utf-8',errors='ignore').read()
    except FileNotFoundError:
        print('app.py: missing'); app_src=None
    if app_src is not None:
        if '[data-testid="stSidebarNav"] { display:none !important; }' not in app_src:
            css_block = "import streamlit as st\nst.set_page_config(page_title='Vega Cockpit', layout='wide', initial_sidebar_state='expanded')\nst.markdown('''\\\n<style>[data-testid=\"stSidebarNav\"] { display:none !important; }</style>\n''', unsafe_allow_html=True)\n"
            open('app.py','w',encoding='utf-8').write(css_block + "\n" + app_src)
            print("app.py: injected early CSS")
        else:
            print("app.py: CSS already present")
        append_once('app.py', 'Modules 1–12 (one panel for quick access', "# --- Modules 1\u201312 (one panel for quick access, menu-safe) ---\ntry:\n    import streamlit as _st\n    with _st.expander(\"Modules 1\u201312\", expanded=False):\n        _st.markdown(\"**Product & Ads**\")\n        _st.page_link(\"pages/60_Reviews_Ratings_Monitor.py\", label=\"Reviews & Ratings Monitor\")\n        _st.page_link(\"pages/64_BuyBox_Price_Intel.py\", label=\"Buy Box & Price Intelligence\")\n        _st.page_link(\"pages/65_Keyword_Rank_Tracker.py\", label=\"Keyword Rank Tracker & Competitor Gap\")\n        _st.page_link(\"pages/66_Promotions_Calendar.py\", label=\"Promotions / Coupons Calendar\")\n        _st.markdown(\"**Orders & Catalog**\")\n        _st.page_link(\"pages/61_Returns_Defect_Analyzer.py\", label=\"Returns / Defect Rate Analyzer\")\n        _st.page_link(\"pages/62_FBA_Inventory_Restock.py\", label=\"FBA Inventory & Restock Planner\")\n        _st.page_link(\"pages/69_Shipment_Builder_Tracker.py\", label=\"Shipment Builder & Tracker (FBA)\")\n        _st.page_link(\"pages/70_Customer_Messages_Triage.py\", label=\"Customer Messages Triage\")\n        _st.markdown(\"**Finance**\")\n        _st.page_link(\"pages/67_FBA_Fee_Storage_Forecaster.py\", label=\"FBA Fee & Storage Cost Forecaster\")\n        _st.page_link(\"pages/68_Seasonality_Demand_Forecast.py\", label=\"Seasonality & Demand Forecast\")\n        _st.page_link(\"pages/71_US_MX_CA_Aggregator.py\", label=\"US\u2013MX\u2013CA Aggregator (FX-aware)\")\n        _st.markdown(\"**Compliance**\")\n        _st.page_link(\"pages/63_Policy_Account_Health.py\", label=\"Policy & Account Health Watch\")\nexcept Exception as _e:\n    pass\n")
    # 3) digest_runner: include queue
    append_once('utils/digest_runner.py', '[Modules 1–12] include digest queue items', "# --- [Modules 1\u201312] include digest queue items if present ---\ntry:\n    from utils.digest_queue import list_summaries as _dq_list\n    _dq = _dq_list()\n    if _dq:\n        try:\n            parts = [\"<h4>Module Summaries</h4><ul>\"]\n            for item in _dq:\n                title = item.get(\"title\") or item.get(\"module\",\"module\")\n                rows = item.get(\"rows\") or []\n                parts.append(f\"<li><b>{title}</b> \u2014 {len(rows)} rows</li>\")\n            parts.append(\"</ul>\")\n            html = (html or \"\") + \"\".join(parts)\n        except Exception:\n            pass\nexcept Exception:\n    pass\n")
    # 4) Settings flags panel (only append if missing)
    try:
        settings_src=open('pages/44_Settings_Controls.py','r',encoding='utf-8',errors='ignore').read()
    except FileNotFoundError:
        settings_src='import streamlit as st\nst.title("Settings Controls")\n'
        open('pages/44_Settings_Controls.py','w',encoding='utf-8').write(settings_src)
    if 'Feature Flags' not in open('pages/44_Settings_Controls.py','r',encoding='utf-8',errors='ignore').read():
        with open('pages/44_Settings_Controls.py','a',encoding='utf-8') as f: f.write("\n"+"# --- Feature Flags panel (auto) ---\nimport os as _os, yaml as _yaml, streamlit as _st\n_cfg_dir='config'; _cfg_path=_os.path.join(_cfg_dir,'feature_flags.yaml')\n_st.subheader('Feature Flags')\ntry:\n  _os.makedirs(_cfg_dir, exist_ok=True)\n  _flags=_yaml.safe_load(open(_cfg_path,'r',encoding='utf-8')) if _os.path.exists(_cfg_path) else {}\n  _flags=_flags or {'dev_tools_link_enabled':True,'alerts_auto_refresh_default_secs':0,'digest_attachments_default':False}\n  c1,c2,c3=_st.columns(3)\n  _flags['dev_tools_link_enabled']=c1.toggle('Show Developer Tools link', value=bool(_flags.get('dev_tools_link_enabled',True)))\n  _flags['alerts_auto_refresh_default_secs']=int(c2.number_input('Alerts default auto-refresh (secs)', min_value=0, max_value=600, value=int(_flags.get('alerts_auto_refresh_default_secs',0)), step=5))\n  _flags['digest_attachments_default']=bool(c3.toggle('Digest: attachments default ON', value=bool(_flags.get('digest_attachments_default',False))))\n  if _st.button('Save Feature Flags', use_container_width=True):\n    with open(_cfg_path,'w',encoding='utf-8') as f: _yaml.safe_dump(_flags,f,sort_keys=True)\n    _st.success('Saved feature flags.')\nexcept Exception as _e:\n  _st.error(f'Feature flags failed: {_e}')\n"+"\n")
        print("Settings Controls: added Feature Flags panel")
    else:
        print("Settings Controls: Feature Flags present")
    print("DONE")
    return 0

if __name__=='__main__':
    sys.exit(main())
