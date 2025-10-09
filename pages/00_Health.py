
import streamlit as st
from services.amazon_ads_service import get_profiles, _db
st.set_page_config(page_title='Vega Health', layout='wide')
st.title('Vega Health')
ok=True
try:
    st.json(get_profiles())
    st.success('✔️ Ads token & profile OK')
except Exception as e:
    ok=False; st.error(e)
try:
    con=_db(); con.execute('select 1'); con.close()
    st.success('✔️ DB OK')
except Exception as e:
    ok=False; st.error(e)
st.write('Healthy' if ok else 'Issues found')
