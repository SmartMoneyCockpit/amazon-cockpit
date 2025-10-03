
from __future__ import annotations
import pandas as pd

def _read_tab(name: str) -> pd.DataFrame:
    try:
        from utils import sheets_bridge as SB
        df = SB.read_tab(name)
        if isinstance(df, pd.DataFrame):
            df.columns = [c.strip().lower() for c in df.columns]
            return df
    except Exception:
        pass
    return pd.DataFrame()

def build_reorder_plan(lookback_days: int = 60,
                       lead_time_days: int = 21,
                       moq_units: int = 0,
                       safety_stock_days: int = 7) -> pd.DataFrame:
    """
    Compute basic reorder signals:
      - daily_velocity = units_sold_last_N / N
      - projected_demand = daily_velocity * (lead_time_days + safety_stock_days)
      - reorder_qty = max(0, projected_demand - inventory) rounded up to MOQ
      - days_of_cover = inventory / max(daily_velocity, 1e-9)

    Requires:
      orders tab with columns: purchase_date/order_date/date, sku, qty/quantity
      inventory tab with columns: sku, inventory
    """
    # Orders -> units per SKU in lookback window
    ords = _read_tab("orders")
    if not ords.empty:
        # date column
        dcol = None
        for c in ["purchase_date","order_date","date"]:
            if c in ords.columns:
                dcol = c; break
        if dcol is None:
            ords = pd.DataFrame(columns=["sku","qty"])
        else:
            ords["dt"] = pd.to_datetime(ords[dcol], errors="coerce")
            cutoff = pd.Timestamp.utcnow() - pd.Timedelta(days=lookback_days)
            ords = ords.loc[ords["dt"] >= cutoff]
            qcol = "qty" if "qty" in ords.columns else ("quantity" if "quantity" in ords.columns else None)
            if qcol is None: 
                ords = pd.DataFrame(columns=["sku","qty"])
            else:
                ords = ords.groupby("sku", as_index=False).agg(units_sold=(qcol,"sum"))
    else:
        ords = pd.DataFrame(columns=["sku","units_sold"])

    # Inventory
    inv = _read_tab("inventory")
    if inv.empty or "sku" not in inv.columns:
        inv = pd.DataFrame(columns=["sku","inventory"])
    else:
        inv = inv.rename(columns={"qty":"inventory","stock":"inventory"})

    # Merge
    df = inv.merge(ords, on="sku", how="left")
    df["units_sold"] = pd.to_numeric(df["units_sold"], errors="coerce").fillna(0.0)
    df["inventory"] = pd.to_numeric(df["inventory"], errors="coerce").fillna(0.0)

    # Velocity
    N = max(lookback_days, 1)
    df["daily_velocity"] = df["units_sold"] / float(N)

    # Days of cover
    df["days_of_cover"] = df["inventory"] / df["daily_velocity"].replace(0, pd.NA)

    # Projected demand for window (lead + safety)
    window_days = max(int(lead_time_days) + int(safety_stock_days), 0)
    df["proj_demand_window"] = df["daily_velocity"] * window_days

    # Reorder qty
    df["raw_reorder"] = (df["proj_demand_window"] - df["inventory"]).clip(lower=0)
    moq = max(int(moq_units), 0)
    if moq > 0:
        df["reorder_qty"] = ((df["raw_reorder"] + moq - 1) // moq) * moq
    else:
        df["reorder_qty"] = df["raw_reorder"].round(0)

    # Priority band
    def band(row):
        if pd.isna(row["days_of_cover"]): return "unknown"
        if row["days_of_cover"] <= lead_time_days: return "red"
        if row["days_of_cover"] <= lead_time_days + safety_stock_days: return "yellow"
        return "green"
    df["priority"] = df.apply(band, axis=1)

    cols = ["sku","inventory","units_sold","daily_velocity","days_of_cover","proj_demand_window","reorder_qty","priority"]
    # Keep extra useful columns if they exist (asin/title)
    for c in ["asin","title"]:
        if c in inv.columns and c not in cols:
            cols.insert(1, c)
    return df[cols].sort_values(["priority","days_of_cover","reorder_qty"], na_position="last")
