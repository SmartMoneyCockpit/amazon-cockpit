
import os
import streamlit as st

st.set_page_config(page_title="App Menu", layout="wide")
st.title("🗂️ App Menu")

# --- Hide the default sidebar page list (Streamlit multipage nav) ---
st.markdown("""
<style>
/* Hide the auto-generated page list in the sidebar */
section[data-testid="stSidebar"] div[data-testid="stSidebarNav"] { display: none !important; }
</style>
""", unsafe_allow_html=True)

st.sidebar.header("Navigation")
st.sidebar.caption("Compact accordion-style menu")

# Helper: link to a page by its file (relative path inside /pages) or by name
def link(label, page):
    try:
        # Streamlit 1.25+
        st.sidebar.page_link(page=page, label=label, icon=None)
    except Exception:
        # Fallback: anchor (works when running from Home; may reload)
        st.sidebar.markdown(f"- [{label}]({page})", unsafe_allow_html=True)

# ---- Accordions (Amazon-style) ----
with st.sidebar.expander("🏠 Overview", expanded=True):
    link("Home Global Overview", "pages/00_Home_Global_Overview.py")
    link("About and Health", "pages/00_About_and_Health.py")
    link("Settings Controls", "pages/44_Settings_Controls.py")

with st.sidebar.expander("💰 Finance", expanded=False):
    link("Finance Dashboard v2", "pages/27_Finance_Dashboard_v2.py")
    link("Finance Heatmap", "pages/33_Finance_Heatmap.py")
    link("Finance Monthly Export", "pages/26_Finance_Monthly_Export.py")
    link("Daily Digest", "pages/34_Daily_Digest.py")
    link("Weekly Digest", "pages/43_Weekly_Digest.py")

with st.sidebar.expander("📦 Catalog & SEO", expanded=False):
    link("Product Tracker", "pages/10_Product_Tracker.py")
    link("Catalog Enrichment", "pages/29_Catalog_Enrichment.py")
    link("A+ & SEO Panel", "pages/21_Aplus_SEO_Panel.py")

with st.sidebar.expander("🎯 PPC", expanded=False):
    link("PPC Manager (Safe)", "pages/14_PPC_Manager_Safe.py")
    link("PPC Import Wizard", "pages/15_PPC_Import_Wizard.py")
    link("PPC Live (Ads API)", "pages/42_PPC_Live.py")

with st.sidebar.expander("🚨 Alerts & Actions", expanded=False):
    link("Alerts Center", "pages/31_Alerts_Center.py")
    link("Trade Action Hub", "pages/32_Trade_Action_Hub.py")
    link("Revenue Protection", "pages/37_Revenue_Protection.py")
    link("Alerts Notifications", "pages/41_Alerts_Notifications.py")

with st.sidebar.expander("🧮 Planning", expanded=False):
    link("COGS Manager", "pages/36_COGS_Manager.py")
    link("Reorder Forecast", "pages/38_Reorder_Forecast.py")
    link("Margin Scenario", "pages/39_Margin_Scenario.py")

with st.sidebar.expander("🛠️ System / Admin", expanded=False):
    link("Data Sync", "pages/25_Data_Sync.py")
    link("Digest Distribution", "pages/40_Digest_Distribution.py")
    link("Drive Upload Test", "pages/35_Drive_Upload_Test.py")
    link("Admin • Error Log Viewer", "pages/45_Admin_Log_Viewer.py")

st.success("Use the sidebar accordions to navigate. The default page list is hidden for a compact UX.")
st.caption("Tip: You can still keep all existing pages; this menu simply hides the long list and organizes links by section.")
