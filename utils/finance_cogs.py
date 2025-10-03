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

    # Join COGS per unit
    if not cogs_map.empty and "sku" in cogs_map.columns and "cogs_per_unit" in cogs_map.columns:
        df = df.merge(cogs_map[["sku","cogs_per_unit"]], on="sku", how="left")
    else:
        df["cogs_per_unit"] = 0.0

    # Compute COGS if units exist
    if "units" in df.columns:
        df["cogs"] = pd.to_numeric(df["units"], errors="coerce").fillna(0) * pd.to_numeric(df["cogs_per_unit"], errors="coerce").fillna(0.0)
        df["gross_margin"] = df["revenue"].fillna(0) - df["cogs"].fillna(0)
        df["gross_margin_pct"] = (df["gross_margin"] / df["revenue"].replace(0, pd.NA)).astype(float) * 100
    else:
        df["cogs"] = pd.NA
        df["gross_margin"] = pd.NA
        df["gross_margin_pct"] = pd.NA

    return df
