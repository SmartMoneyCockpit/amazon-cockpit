#!/usr/bin/env python3
# Auto-apply Modules 1–12 fragments (menu-safe). Idempotent.
import os, sys

APP = "app.py"
DR  = "utils/digest_runner.py"

APP_BLOCK = r"""# --- Modules 1–12 (one panel for quick access, menu-safe) ---
try:
    import streamlit as _st
    with _st.expander("Modules 1–12", expanded=False):
        _st.markdown("**Product & Ads**")
        _st.page_link("pages/60_Reviews_Ratings_Monitor.py", label="Reviews & Ratings Monitor")
        _st.page_link("pages/64_BuyBox_Price_Intel.py", label="Buy Box & Price Intelligence")
        _st.page_link("pages/65_Keyword_Rank_Tracker.py", label="Keyword Rank Tracker & Competitor Gap")
        _st.page_link("pages/66_Promotions_Calendar.py", label="Promotions / Coupons Calendar")
        _st.markdown("**Orders & Catalog**")
        _st.page_link("pages/61_Returns_Defect_Analyzer.py", label="Returns / Defect Rate Analyzer")
        _st.page_link("pages/62_FBA_Inventory_Restock.py", label="FBA Inventory & Restock Planner")
        _st.page_link("pages/69_Shipment_Builder_Tracker.py", label="Shipment Builder & Tracker (FBA)")
        _st.page_link("pages/70_Customer_Messages_Triage.py", label="Customer Messages Triage")
        _st.markdown("**Finance**")
        _st.page_link("pages/67_FBA_Fee_Storage_Forecaster.py", label="FBA Fee & Storage Cost Forecaster")
        _st.page_link("pages/68_Seasonality_Demand_Forecast.py", label="Seasonality & Demand Forecast")
        _st.page_link("pages/71_US_MX_CA_Aggregator.py", label="US–MX–CA Aggregator (FX-aware)")
        _st.markdown("**Compliance**")
        _st.page_link("pages/63_Policy_Account_Health.py", label="Policy & Account Health Watch")
except Exception as _e:
    pass
"""

DR_BLOCK = r"""# --- [Modules 1–12] include digest queue items if present ---
try:
    from utils.digest_queue import list_summaries as _dq_list
    _dq = _dq_list()
    if _dq:
        # build independent HTML chunk; don't assume 'html' exists
        parts = ["<h4>Module Summaries</h4><ul>"]
        for item in _dq:
            title = item.get("title") or item.get("module","module")
            rows = item.get("rows") or []
            parts.append(f"<li><b>{title}</b> — {len(rows)} rows</li>")
        parts.append("</ul>")
        _queue_html = "".join(parts)
        try:
            html = (html or "") + _queue_html  # if html exists
        except Exception:
            # no global 'html' variable in scope; expose chunk via a stable name
            _MODULE_SUMMARIES_HTML = _queue_html
except Exception:
    pass
"""

def append_once(path, block, marker_snip):
    try:
        with open(path, "r", encoding="utf-8") as f:
            src = f.read()
    except FileNotFoundError:
        print(f"{path}: missing")
        return False
    if marker_snip in src:
        print(f"{path}: skip — already applied")
        return False
    with open(path, "w", encoding="utf-8") as f:
        f.write(src + "\n" + block + "\n")
    print(f"{path}: OK — fragment appended")
    return True

def main():
    ok1 = append_once(APP, APP_BLOCK, "Modules 1–12 (one panel for quick access")
    ok2 = append_once(DR,  DR_BLOCK,  "[Modules 1–12] include digest queue items")
    return 0 if (ok1 or ok2) else 0

if __name__ == "__main__":
    sys.exit(main())
