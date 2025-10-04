from __future__ import annotations
import pandas as pd
from typing import List, Dict, Any, Tuple

EXPECTED_COLS = ["date","order_id","asin","sku","country","qty","price","revenue"]

def demo_orders(days: int = 30) -> pd.DataFrame:
    import datetime as dt, random
    base = pd.date_range(end=dt.date.today(), periods=days, freq="D")
    rows = []
    countries = ["US","CA","MX"]
    asins = ["B00DEMOUS","B00DEMOCAN","B00DEMOMX"]
    for d in base:
        for i in range(4):
            qty = random.choice([1,1,1,2])
            price = random.choice([14.99,19.99,24.99,29.99,39.99])
            rev = qty*price
            rows.append({
                "date": d.date(),
                "order_id": f"ORD-{d.strftime('%Y%m%d')}-{i:03d}",
                "asin": random.choice(asins),
                "sku": f"SKU-{i:03d}",
                "country": random.choice(countries),
                "qty": qty,
                "price": price,
                "revenue": rev
            })
    return pd.DataFrame(rows)

def normalize(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame(columns=EXPECTED_COLS)
    d = df.copy()
    d.columns = [str(c).strip().lower() for c in d.columns]
    # Backfill revenue if missing
    if "revenue" not in d.columns and {"qty","price"} <= set(d.columns):
        d["revenue"] = pd.to_numeric(d["qty"], errors="coerce") * pd.to_numeric(d["price"], errors="coerce")
    # Ensure all expected columns exist
    for c in EXPECTED_COLS:
        if c not in d.columns:
            d[c] = None
    # Coerce types
    d["date"] = pd.to_datetime(d["date"], errors="coerce").dt.date
    for c in ["qty"]:
        d[c] = pd.to_numeric(d[c], errors="coerce")
    for c in ["price","revenue"]:
        d[c] = pd.to_numeric(d[c], errors="coerce")
    d = d[EXPECTED_COLS]
    d = d.dropna(subset=["date"])
    return d

def kpis(d: pd.DataFrame) -> Dict[str, Any]:
    if d is None or d.empty:
        return {"orders": 0, "revenue": 0.0, "aov": 0.0}
    orders = len(d)
    revenue = float(d["revenue"].sum())
    aov = (revenue / orders) if orders > 0 else 0.0
    return {"orders": orders, "revenue": revenue, "aov": aov}
