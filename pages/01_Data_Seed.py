
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Data Seed", layout="wide")
st.title("🌱 One-Click Data Seed")
st.caption("Seeds minimal tabs in your Google Sheet so the cockpit lights up in a new environment. If Sheets isn't available, download CSVs and paste them manually.")

def make_samples():
    inventory = pd.DataFrame([
        {"sku":"NOPAL-120","asin":"B00NOPAL01","title":"Nopal Cactus 120ct","inventory":420,"price":24.95,"stars":4.6,"reviews":812,"sessions":1500,"cvr%":6.2,"days of cover":28},
        {"sku":"MANGO-120","asin":"B00MANGO01","title":"Mangosteen Pericarp 120ct","inventory":180,"price":29.95,"stars":4.4,"reviews":365,"sessions":900,"cvr%":4.9,"days of cover":19},
        {"sku":"NOPAL-240","asin":"B00NOPAL02","title":"Nopal Cactus 240ct","inventory":95,"price":39.95,"stars":4.5,"reviews":145,"sessions":600,"cvr%":5.1,"days of cover":12},
    ])
    orders = pd.DataFrame([
        {"order_id":"112-000001-000001","purchase_date":"2025-09-28T18:12:00Z","status":"Shipped","sku":"NOPAL-120","asin":"B00NOPAL01","qty":1,"price":24.95},
        {"order_id":"112-000002-000002","purchase_date":"2025-09-29T15:02:00Z","status":"Shipped","sku":"MANGO-120","asin":"B00MANGO01","qty":2,"price":59.90},
    ])
    finances = pd.DataFrame([
        {"date":"2025-09-28","sku":"NOPAL-120","asin":"B00NOPAL01","revenue":24.95,"fees":7.10,"other":0.0},
        {"date":"2025-09-29","sku":"MANGO-120","asin":"B00MANGO01","revenue":59.90,"fees":14.50,"other":0.0},
    ])
    keywords = pd.DataFrame([
        {"keyword":"nopal cactus","priority":"High","est_search_volume":12000,"cpc_usd":0.62,"indexed":"TRUE","rank":7},
        {"keyword":"mangosteen pericarp","priority":"High","est_search_volume":6500,"cpc_usd":0.55,"indexed":"TRUE","rank":12},
        {"keyword":"nopal capsules","priority":"High","est_search_volume":2100,"cpc_usd":0.42,"indexed":"FALSE","rank":None},
    ])
    competitors = pd.DataFrame([
        {"asin":"C001","title":"Brand X Nopal 120ct","price":22.95,"stars":4.4,"reviews":421,"a+":True,"mainimagequality":"Good"},
        {"asin":"C002","title":"Brand Y Mangosteen","price":27.95,"stars":4.2,"reviews":310,"a+":False,"mainimagequality":"Fair"},
        {"asin":"C003","title":"Brand Z Nopal 240ct","price":37.95,"stars":4.5,"reviews":256,"a+":True,"mainimagequality":"Good"},
    ])
    compliance = pd.DataFrame([
        {"asin":"B00NOPAL01","doc_type":"COA","issuer":"Lab ABC","issued_on":"2025-07-01","expires_on":"2026-07-01","link":"https://example.com/coa.pdf","notes":""},
        {"asin":"B00MANGO01","doc_type":"GMP","issuer":"Cert Org","issued_on":"2024-09-10","expires_on":"2025-10-12","link":"https://example.com/gmp.pdf","notes":"Renew soon"},
    ])
    ppc_import = pd.DataFrame([
        {"date":"2025-09-28","campaign":"Auto","ad_group":"Core","keyword":"nopal supplement","match_type":"exact","impressions":1200,"clicks":90,"spend":45.20,"orders":8,"sales":320.50},
        {"date":"2025-09-28","campaign":"Generic","ad_group":"Test","keyword":"mangosteen capsules","match_type":"phrase","impressions":980,"clicks":50,"spend":38.10,"orders":0,"sales":0.0},
    ])
    cogs_map = pd.DataFrame([
        {"sku":"NOPAL-120","cogs_per_unit":6.50},
        {"sku":"MANGO-120","cogs_per_unit":7.80},
        {"sku":"NOPAL-240","cogs_per_unit":11.00},
    ])
    alerts_settings = pd.DataFrame([{
        "doc_days_low":10,"compliance_due_days":30,"ppc_min_spend":10.0,"ppc_min_clicks":12,
        "net_margin_min_pct":0.0,"gross_margin_min_pct":15.0
    }])
    return {
        "inventory": inventory,"orders": orders,"finances": finances,"keywords": keywords,
        "competitors": competitors,"compliance": compliance,"ppc_import": ppc_import,
        "cogs_map": cogs_map,"alerts_settings": alerts_settings
    }

samples = make_samples()

# Sheets writer
try:
    from utils.sheets_writer import write_df
    HAVE_WRITER = True
except Exception:
    HAVE_WRITER = False

tabs = st.multiselect("Choose tabs to seed", list(samples.keys()), default=list(samples.keys()))
if st.button("🚀 Seed selected tabs to Google Sheets"):
    if not HAVE_WRITER:
        st.error("Sheets writer not available. Use the CSV downloads below.")
    else:
        results = []
        for t in tabs:
            try:
                res = write_df(t, pd.DataFrame(samples[t]))
                results.append(f"{t}: {res}")
            except Exception as e:
                results.append(f"{t}: ERROR {e}")
        st.success("Done: " + "; ".join(results))

st.subheader("CSV Downloads (manual paste)")
for name, df in samples.items():
    st.download_button(f"⬇️ {name}.csv", data=df.to_csv(index=False).encode("utf-8"),
                       file_name=f"{name}.csv", mime="text/csv")
