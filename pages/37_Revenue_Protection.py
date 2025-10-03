import streamlit as st
import pandas as pd
from utils.auth import gate
import utils.security as sec
from utils.revenue_protection import build_revenue_protection
from utils.sheets_writer import write_df

st.set_page_config(page_title='Revenue Protection', layout='wide')
sec.enforce()
if not gate(required_admin=False):
    st.stop()

st.title('🛡️ Revenue Protection')
st.caption('Correlates margin breaches with PPC surge candidates to protect profits.')

df = build_revenue_protection()
if df.empty:
    st.info('No revenue protection alerts yet. Ensure alerts_out_margins and alerts_out_ppc exist and inventory has SKU/ASIN mapping.')
else:
    red = int((df['severity']=='red').sum()) if 'severity' in df.columns else 0
    yellow = int((df['severity']=='yellow').sum()) if 'severity' in df.columns else 0
    c1,c2,c3 = st.columns(3)
    c1.metric('Critical', red)
    c2.metric('Attention', yellow)
    c3.metric('Total', len(df))

    st.subheader('Alerts')
    st.dataframe(df, use_container_width=True, hide_index=True)

    cA, cB = st.columns(2)
    if cA.button('📤 Export to Sheet → alerts_out_revenue_protection'):
        st.success(write_df('alerts_out_revenue_protection', df))
    cB.download_button('⬇️ Download CSV', data=df.to_csv(index=False).encode('utf-8'), file_name='alerts_out_revenue_protection.csv', mime='text/csv')
