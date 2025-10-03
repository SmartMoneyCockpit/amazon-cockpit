
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

def load_base() -> pd.DataFrame:
    """Load profitability_monthly (and join units if present)."""
    df = _read_tab("profitability_monthly")
    if df.empty:
        return pd.DataFrame(columns=["month","sku","revenue","fees","other","units"])
    # Ensure numerics
    for c in ["revenue","fees","other","units"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0.0)
    return df

def simulate(df: pd.DataFrame,
             price_change_pct: float = 0.0,
             cogs_per_unit_change_pct: float = 0.0,
             fees_change_pct: float = 0.0,
             ppc_change_pct: float = 0.0,
             cogs_per_unit_map: pd.DataFrame | None = None) -> pd.DataFrame:
    """
    Apply scenario deltas:
      revenue' = revenue * (1 + price_change_pct/100)
      fees'    = fees * (1 + fees_change_pct/100)
      other'   = other + (ppc_delta)  (assume PPC sits in 'other')
      cogs'    = units * cogs_per_unit * (1 + cogs_per_unit_change_pct/100)  (if data available)

    Returns wide table with base vs scenario and deltas.
    """
    out = df.copy()
    # Base
    base_rev = out.get("revenue", pd.Series(0.0, index=out.index))
    base_fees = out.get("fees", pd.Series(0.0, index=out.index))
    base_other = out.get("other", pd.Series(0.0, index=out.index))
    base_units = out.get("units", pd.Series(0.0, index=out.index))

    # Assume PPC adjustments affect 'other'
    other_ppc = base_other * (1 + float(ppc_change_pct)/100.0)

    # Apply fee & price changes
    rev_new = base_rev * (1 + float(price_change_pct)/100.0)
    fees_new = base_fees * (1 + float(fees_change_pct)/100.0)
    other_new = other_ppc

    # COGS per unit if available
    cogs_per_unit = pd.Series(0.0, index=out.index)
    if isinstance(cogs_per_unit_map, pd.DataFrame) and not cogs_per_unit_map.empty:
        m = cogs_per_unit_map.copy()
        m.columns = [c.strip().lower() for c in m.columns]
        if "sku" in out.columns and "sku" in m.columns and "cogs_per_unit" in m.columns:
            out = out.merge(m[["sku","cogs_per_unit"]], on="sku", how="left")
            cogs_per_unit = pd.to_numeric(out["cogs_per_unit"], errors="coerce").fillna(0.0)
    cogs_new = base_units * cogs_per_unit * (1 + float(cogs_per_unit_change_pct)/100.0)

    # Net & margins (base)
    net_base = base_rev - base_fees - base_other
    net_new = rev_new - fees_new - other_new
    gm_base = (base_rev - (base_units * cogs_per_unit)) if "units" in df.columns else pd.Series([None]*len(out))
    try:
        gm_base_pct = (gm_base / base_rev.replace(0, pd.NA)).astype(float) * 100
    except Exception:
        gm_base_pct = pd.Series([None]*len(out))

    gm_new = (rev_new - cogs_new) if "units" in df.columns else pd.Series([None]*len(out))
    try:
        gm_new_pct = (gm_new / rev_new.replace(0, pd.NA)).astype(float) * 100
    except Exception:
        gm_new_pct = pd.Series([None]*len(out))

    # Assemble
    out["revenue_base"] = base_rev
    out["fees_base"] = base_fees
    out["other_base"] = base_other
    out["net_base"] = net_base
    out["gm_base_pct"] = gm_base_pct

    out["revenue_new"] = rev_new
    out["fees_new"] = fees_new
    out["other_new"] = other_new
    out["net_new"] = net_new
    out["gm_new_pct"] = gm_new_pct

    out["net_delta"] = out["net_new"] - out["net_base"]
    out["gm_delta_pct"] = out["gm_new_pct"] - out["gm_base_pct"]

    keep = ["month","sku","revenue_base","fees_base","other_base","net_base","gm_base_pct",
            "revenue_new","fees_new","other_new","net_new","gm_new_pct","net_delta","gm_delta_pct"]
    keep = [c for c in keep if c in out.columns]
    return out[keep]
