
"""SP-API non-Ads stubs.
Replace these with real calls tomorrow (Orders, Inventory, Finances).
Return empty DataFrames for now so pages can import without errors.
"""
import pandas as pd

def list_orders(*args, **kwargs) -> pd.DataFrame:
    return pd.DataFrame(columns=["order_id","purchase_date","status","sku","asin","qty","price"])

def list_inventory(*args, **kwargs) -> pd.DataFrame:
    return pd.DataFrame(columns=["sku","asin","fnsku","on_hand","available","inbound"])

def list_finances(*args, **kwargs) -> pd.DataFrame:
    return pd.DataFrame(columns=["date","sku","asin","revenue","fees","other"])
