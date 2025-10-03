from __future__ import annotations
import pandas as pd

def read_tab(name: str) -> pd.DataFrame:
    try:
        from utils import sheets_bridge as SB
        df = SB.read_tab(name)
        if isinstance(df, pd.DataFrame):
            df.columns = [c.strip().lower() for c in df.columns]
            return df
    except Exception:
        pass
    return pd.DataFrame()

def margin_breaches(net_margin_pct_thresh: float = 0.0, gross_margin_pct_thresh: float = 15.0) -> pd.DataFrame:
    fin = read_tab("profitability_monthly")
    if fin.empty:
        return pd.DataFrame(columns=["month","sku","revenue","fees","other","net","gross_margin_pct","net_margin_pct","reason"])
    fin["revenue"] = pd.to_numeric(fin.get("revenue"), errors="coerce").fillna(0.0)
    fin["fees"] = pd.to_numeric(fin.get("fees"), errors="coerce").fillna(0.0)
    fin["other"] = pd.to_numeric(fin.get("other"), errors="coerce").fillna(0.0)
    fin["net"] = fin["revenue"] - fin["fees"] - fin["other"]
    fin["net_margin_pct"] = (fin["net"] / fin["revenue"].replace(0, pd.NA)).astype(float) * 100
    cogs_map = read_tab("cogs_map")
    if not cogs_map.empty and "sku" in cogs_map.columns and "cogs_per_unit" in cogs_map.columns:
        merged = fin.merge(cogs_map[["sku","cogs_per_unit"]], on="sku", how="left")
        if "units" in merged.columns:
            merged["cogs"] = pd.to_numeric(merged["units"], errors="coerce").fillna(0) * pd.to_numeric(merged["cogs_per_unit"], errors="coerce").fillna(0.0)
        else:
            merged["cogs"] = pd.NA
        merged["gross_margin"] = (merged["revenue"] - merged["cogs"]).where(merged["cogs"].notna())
        merged["gross_margin_pct"] = (merged["gross_margin"] / merged["revenue"].replace(0, pd.NA)).astype(float) * 100
    else:
        merged = fin.copy()
        merged["gross_margin_pct"] = pd.NA

    alerts = []
    nm = merged[merged["net_margin_pct"].fillna(0) < float(net_margin_pct_thresh)].copy()
    if not nm.empty:
        nm["reason"] = f"net < {net_margin_pct_thresh:.1f}%"
        alerts.append(nm[["month","sku","revenue","fees","other","net","gross_margin_pct","net_margin_pct","reason"]])
    if "gross_margin_pct" in merged.columns:
        gm = merged[merged["gross_margin_pct"].notna() & (merged["gross_margin_pct"] < float(gross_margin_pct_thresh))].copy()
        if not gm.empty:
            gm["reason"] = f"gross < {gross_margin_pct_thresh:.1f}%"
            alerts.append(gm[["month","sku","revenue","fees","other","net","gross_margin_pct","net_margin_pct","reason"]])
    if not alerts:
        return pd.DataFrame(columns=["month","sku","revenue","fees","other","net","gross_margin_pct","net_margin_pct","reason"])
    out = pd.concat(alerts, ignore_index=True).drop_duplicates().sort_values(["month","sku"])
    return out
