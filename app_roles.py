import streamlit as st

from utils.data import get_data_sources
from utils.layout import section_header
from utils.roles import get_roles_list, get_role_config

# Import module views
from modules.home import dashboard_home_view
from modules.product_tracker import product_tracker_view
from modules.ppc_manager import ppc_manager_view
from modules.a_plus_seo import a_plus_seo_view
from modules.compliance_vault import compliance_vault_view
from modules.finance_dashboard import finance_dashboard_view
from modules.alerts_hub import alerts_hub_view

st.set_page_config(page_title="Amazon Cockpit", page_icon="🛒", layout="wide")

# Sidebar
with st.sidebar:
    st.title("🛒 Amazon Cockpit")
    st.caption("Role‑Scoped Views")
    st.divider()
    roles = get_roles_list()
    sel = st.selectbox("Role", roles, index=0, key="role_select")
    rcfg = get_role_config(sel)
    st.caption(rcfg.label)
    st.divider()
    st.write("Data Sources")
    st.json(get_data_sources(), expanded=False)
    st.divider()
    if st.button("🔄 Clear Cache"):
        st.cache_data.clear()
        st.success("Cache cleared.")

# Tabs filtered by role
tabs_allowed = rcfg.tabs
section_header(f"Amazon Cockpit — {rcfg.label}")
tab_objs = st.tabs(tabs_allowed)

# Render allowed tabs only
tab_render_map = {
    "Home": dashboard_home_view,
    "Product Tracker": product_tracker_view,
    "PPC Manager": ppc_manager_view,
    "A+ & SEO": a_plus_seo_view,
    "Compliance Vault": compliance_vault_view,
    "Finance Dashboard": finance_dashboard_view,
    "Alerts Hub": alerts_hub_view,
}

for tab_name, tab_obj in zip(tabs_allowed, tab_objs):
    with tab_obj:
        render = tab_render_map.get(tab_name)
        if render:
            render()

st.divider()
st.caption("© 2025 Amazon Cockpit — Role‑Scoped Edition")
