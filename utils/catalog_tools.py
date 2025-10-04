from __future__ import annotations
import pandas as pd

EXPECTED_COLS = ["asin","sku","title","description","price"]

def demo_catalog(n: int = 25) -> pd.DataFrame:
    rows = []
    for i in range(n):
        rows.append({
            "asin": f"B00CAT{i:03d}",
            "sku": f"SKU-{i:03d}",
            "title": f"Demo Product {i} — Premium Quality",
            "description": "" if i % 5 == 0 else "This is a solid product with features...",
            "price": 19.99 + (i % 7) * 2.0
        })
    return pd.DataFrame(rows)

def normalize(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame(columns=EXPECTED_COLS)
    d = df.copy()
    d.columns = [str(c).strip().lower() for c in d.columns]
    for c in EXPECTED_COLS:
        if c not in d.columns:
            d[c] = None
    d = d[EXPECTED_COLS]
    return d

def validation_badges(d: pd.DataFrame) -> pd.DataFrame:
    if d is None or d.empty:
        return pd.DataFrame(columns=EXPECTED_COLS + ["title_ok","desc_ok","price_ok"])
    out = d.copy()
    out["title_ok"] = out["title"].astype(str).str.len().fillna(0).ge(60)
    out["desc_ok"] = out["description"].fillna("").astype(str).str.len().gt(0)
    out["price_ok"] = pd.to_numeric(out["price"], errors="coerce").fillna(-1).gt(0)
    return out
