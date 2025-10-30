import os, requests, pandas as pd, streamlit as st
API_URL = os.getenv("API_URL","").rstrip("/")
def api_get(path, **params):
    url = f"{API_URL}{path if path.startswith('/') else '/'+path}"
    r = requests.get(url, params=params, timeout=25); r.raise_for_status(); return r.json()
st.title("Product Tracker"); st.caption("DB-backed product view (no Sheets).")
q = st.text_input("Search (ASIN, SKU, Title, Brand)", ""); limit = st.number_input("Max rows", 10, 500, 100, 10)
if not API_URL: st.error("API_URL not set"); 
else:
    try:
        data = api_get("/v1/products", limit=int(limit), q=q or None)
        df = pd.DataFrame(data)
        if df.empty: st.info("No products yet. Insert into `products` table."); 
        else:
            if {"price","cost"}.issubset(df.columns):
                df["gross_margin"] = (df["price"] - df["cost"]).astype(float).round(2)
                df["gm%"] = ((df["price"] - df["cost"]) / df["price"] * 100).astype(float).round(1)
            cols = [c for c in ["asin","sku","title","brand","price","cost","gross_margin","gm%","inventory","reviews","stars","updated_at"] if c in df.columns]
            st.dataframe(df[cols], use_container_width=True, height=560)
    except requests.HTTPError as e: st.error(f"API error: {e.response.status_code} {e.response.text[:280]}")
    except Exception as e: st.error(f"Failed to load products: {e}")
