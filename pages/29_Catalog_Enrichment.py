import streamlit as st
import pandas as pd
from utils.auth import gate
import utils.security as sec

st.set_page_config(page_title='Catalog Enrichment', layout='wide')
sec.enforce()
if not gate(required_admin=False):
    st.stop()

st.title('🗂️ Catalog Enrichment')
st.caption('Fetch title/brand/category/dimensions for your ASINs and cache them to catalog_cache. Sources: orders, inventory, or manual list.')

SB = None
try:
    from utils import sheets_bridge as SB
except Exception:
    SB = None

def read_tab(name: str) -> pd.DataFrame:
    if SB is not None:
        try:
            return SB.read_tab(name)
        except Exception:
            pass
    return pd.DataFrame()

src = st.radio('ASIN source', ['Orders (last N days)', 'Inventory (all)', 'Manual paste/list'])

asins = []
if src == 'Orders (last N days)':
    days = st.slider('Days back', 7, 120, 30, 1)
    orders = read_tab('orders')
    if orders.empty:
        st.info('No orders tab found or it is empty. Run Data Sync first.')
    else:
        orders.columns = [c.strip().lower() for c in orders.columns]
        if 'purchase_date' in orders.columns:
            orders['purchase_date'] = pd.to_datetime(orders['purchase_date'], errors='coerce')
            cutoff = pd.Timestamp.utcnow() - pd.Timedelta(days=days)
            orders = orders[orders['purchase_date'] >= cutoff]
        asins = sorted(orders.get('asin', pd.Series([], dtype=str)).dropna().astype(str).unique().tolist())
        st.write(f'Found **{len(asins)}** unique ASINs from orders.')
elif src == 'Inventory (all)':
    inv = read_tab('inventory')
    if inv.empty:
        st.info('No inventory tab found or it is empty. Run Data Sync first.')
    else:
        inv.columns = [c.strip().lower() for c in inv.columns]
        asins = sorted(inv.get('asin', pd.Series([], dtype=str)).dropna().astype(str).unique().tolist())
        st.write(f'Found **{len(asins)}** unique ASINs from inventory.')
else:
    text = st.text_area('Paste ASINs (comma/space/newline separated)', '')
    if text.strip():
        raw = [t.strip() for t in text.replace(',', ' ').split() if t.strip()]
        asins = sorted(list(dict.fromkeys(raw)))
        st.write(f'Parsed **{len(asins)}** ASINs.')

if asins:
    st.subheader('Preview ASINs')
    st.code(', '.join(asins[:50]) + (' ...' if len(asins) > 50 else ''))

    if st.button('🚀 Enrich & Cache to catalog_cache'):
        try:
            from integrations.catalog import enrich_asins
            df = enrich_asins(asins)
            if df is not None and not df.empty:
                st.success(f'Enriched and cached {len(df)} rows to catalog_cache.')
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.warning('No details returned (lib not installed, creds not present, or API empty).')
        except Exception as e:
            st.error(f'Failed to enrich: {e}')
else:
    st.info('Select a source and load ASINs to enable enrichment.')
