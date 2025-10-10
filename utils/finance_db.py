# utils/finance_db.py
from __future__ import annotations
import pandas as pd
from typing import Tuple
from utils.api_client import list_products

def fetch_finance_snapshot(limit: int = 500) -> pd.DataFrame:
    """
    Temporary finance snapshot built from products until a dedicated /v1/finance
    endpoint is available. Produces a minimal frame with columns expected by KPIs.
    """
    ok, data = list_products(limit=limit)
    if not ok or not isinstance(data, list):
        return pd.DataFrame(columns=["SKU","ASIN","Title","Units","Revenue","COGS","Fees","AdSpend","NetProfit"])

    df = pd.DataFrame(data)
    # Normalize columns we have → finance-like shape with safe defaults
    df.rename(columns={"asin": "ASIN", "title": "Title", "price": "Price"}, inplace=True)
    if "Price" not in df.columns:
        df["Price"] = 0.0

    # Minimal computed fields (until real order/finance ingestion fills these)
    df["Units"] = 0
    df["Revenue"] = df["Price"] * df["Units"]
    df["COGS"] = 0.0
    df["Fees"] = 0.0
    df["AdSpend"] = 0.0
    df["NetProfit"] = df["Revenue"] - df["COGS"] - df["Fees"] - df["AdSpend"]

    # Arrange columns
    cols = ["ASIN","Title","Units","Revenue","COGS","Fees","AdSpend","NetProfit"]
    for c in cols:
        if c not in df.columns:
            df[c] = 0 if c in ("Units",) else 0.0
    return df[cols]

def kpis(summary: pd.DataFrame) -> Tuple[float, float, float, float]:
    """Return (Revenue, GrossProfit, NetProfit, ACoS%)."""
    rev = float(summary["Revenue"].sum())
    gp  = float((summary["Revenue"] - summary["COGS"] - summary["Fees"]).sum())
    np  = float((summary["Revenue"] - summary["COGS"] - summary["Fees"] - summary["AdSpend"]).sum())
    acos = float((summary["AdSpend"].sum() / rev) * 100.0) if rev > 0 else 0.0
    return rev, gp, np, acos
