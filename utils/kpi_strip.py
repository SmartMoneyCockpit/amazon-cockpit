
from __future__ import annotations
import pandas as pd
import streamlit as st

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

def _mtd_ytd(fin: pd.DataFrame) -> dict:
    if fin.empty:
        return {"rev_mtd":0.0,"net_mtd":0.0,"units_mtd":0.0,"rev_ytd":0.0,"net_ytd":0.0,"units_ytd":0.0}
    df = fin.copy()
    if "month" not in df.columns:
        # try best-effort from date if available
        if "date" in df.columns:
            df["month"] = pd.to_datetime(df["date"], errors="coerce").dt.to_period("M").astype(str)
        else:
            return {"rev_mtd":0.0,"net_mtd":0.0,"units_mtd":0.0,"rev_ytd":0.0,"net_ytd":0.0,"units_ytd":0.0}
    for c in ["revenue","fees","other","units"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0.0)
    df["net"] = df.get("revenue",0) - df.get("fees",0) - df.get("other",0)
    today = pd.Timestamp.now(tz="America/Mazatlan")
    mtd_key = today.strftime("%Y-%m")
    ytd_year = today.year
    mtd = df[df["month"] == mtd_key]
    ytd = df[pd.to_datetime(df["month"], errors="coerce").dt.year == ytd_year]
    return {
        "rev_mtd": float(mtd["revenue"].sum()) if "revenue" in df.columns else 0.0,
        "net_mtd": float(mtd["net"].sum()),
        "units_mtd": float(mtd["units"].sum()) if "units" in df.columns else 0.0,
        "rev_ytd": float(ytd["revenue"].sum()) if "revenue" in df.columns else 0.0,
        "net_ytd": float(ytd["net"].sum()),
        "units_ytd": float(ytd["units"].sum()) if "units" in df.columns else 0.0,
    }

def _critical_count() -> int:
    a = _read_tab("actions_out")
    if a.empty or "severity" not in a.columns:
        return 0
    return int((a["severity"].astype(str).str.lower() == "red").sum())

def render():
    """Render a compact KPI strip at top of page (MTD/YTD + Critical count)."""
    fin = _read_tab("profitability_monthly")
    k = _mtd_ytd(fin)
    critical = _critical_count()
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Revenue (MTD)", f"${k['rev_mtd']:,.2f}")
    c2.metric("Net (MTD)", f"${k['net_mtd']:,.2f}")
    c3.metric("Revenue (YTD)", f"${k['rev_ytd']:,.2f}")
    c4.metric("Critical Actions", f"{critical}")
