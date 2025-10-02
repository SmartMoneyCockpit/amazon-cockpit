
from __future__ import annotations
import pandas as pd

def read_cogs_map() -> pd.DataFrame:
    """Reads `cogs_map` tab: columns sku,cogs_per_unit"""
    try:
        from utils import sheets_bridge as SB
        df = SB.read_tab("cogs_map")
        if isinstance(df, pd.DataFrame):
            return df
    except Exception:
        pass
    return pd.DataFrame(columns=["sku","cogs_per_unit"])

def apply_margins(roll: pd.DataFrame, cogs_map: pd.DataFrame) -> pd.DataFrame:
    df = roll.copy()
    for col in ["revenue","fees","other"]:
        if col not in df.columns: df[col] = 0.0
    df["net"] = df["revenue"].fillna(0) - df["fees"].fillna(0) - df["other"].fillna(0)
    if not cogs_map.empty and "sku" in cogs_map.columns and "cogs_per_unit" in cogs_map.columns:
        try:
            df = df.merge(cogs_map, on="sku", how="left")
            # approximate units = (revenue / avg selling price)? We don't have price here,
            # so treat COGS per unit as blended and infer units if provided separately.
            # Better: if `units` exists in roll later, use it. For now, allow optional column.
            if "units" in df.columns:
                df["cogs"] = df["units"].fillna(0) * df["cogs_per_unit"].fillna(0)
            else:
                df["cogs"] = 0.0  # placeholder until units available
            df["gross_margin"] = (df["revenue"] - df["cogs"]).fillna(0)
            df["gross_margin_pct"] = (df["gross_margin"] / df["revenue"].replace(0, pd.NA)).astype(float) * 100
            df["net_margin_pct"] = (df["net"] / df["revenue"].replace(0, pd.NA)).astype(float) * 100
        except Exception:
            pass
    return df
