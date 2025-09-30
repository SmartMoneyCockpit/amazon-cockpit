import os
import streamlit as st
from db import health_check, get_session
from models import Product
from sqlalchemy import select

st.set_page_config(page_title="Amazon Cockpit", layout="wide")

st.title("Amazon Cockpit — Core + DB Health Check")

with st.sidebar:
    st.header("Setup Checklist")
    st.markdown("""
1. **Render Web Service** points to this repo  
2. **Build Command**: `pip install -r requirements.txt`  
3. **Start Command**: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`  
4. **Environment**: set `DATABASE_URL` to your Render **Internal Database URL**  
""")

col1, col2, col3 = st.columns(3)
with col1:
    st.subheader("DB Connection")
    try:
        ok = health_check()
        st.metric("DATABASE_URL present", "Yes" if os.getenv("DATABASE_URL") else "No")
        if ok:
            st.success("DB connection OK")
        else:
            st.error("DB ping failed")
    except Exception as e:
        st.error(f"DB error: {e}")

with col2:
    st.subheader("Quick Init")
    if st.button("Initialize DB Tables"):
        from init_db import init
        try:
            init()
            st.success("Tables created (or already exist).")
        except Exception as e:
            st.error(f"Init failed: {e}")

with col3:
    st.subheader("Sample Write")
    if st.button("Insert Sample Product"):
        try:
            sess = get_session()
            p = Product(sku="DEMO-SKU", asin=None, title="Demo Product", marketplace="US")
            sess.add(p)
            sess.commit()
            st.success("Inserted DEMO-SKU.")
        except Exception as e:
            st.error(f"Insert failed: {e}")

st.divider()

st.subheader("Products (first 20)")
try:
    sess = get_session()
    rows = sess.execute(select(Product).limit(20)).scalars().all()
    if rows:
        st.dataframe([{"id": r.id, "sku": r.sku, "asin": r.asin, "title": r.title, "marketplace": r.marketplace} for r in rows])
    else:
        st.info("No products yet. Click 'Insert Sample Product'.")
except Exception as e:
    st.error(f"Query failed: {e}")
