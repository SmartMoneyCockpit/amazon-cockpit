
from __future__ import annotations
import pandas as pd
from typing import Dict, Any

def _read_tab(name: str):
    try:
        from utils import sheets_bridge as SB
        return SB.read_tab(name)
    except Exception:
        return pd.DataFrame()

def load_thresholds() -> Dict[str, Any]:
    """Read thresholds from `alerts_settings` tab if present; otherwise defaults."""
    df = _read_tab("alerts_settings")
    out = {
        "doc_days_low": 10,
        "compliance_due_days": 30,
        "ppc_min_spend": 10.0,
        "ppc_min_clicks": 12,
    }
    if isinstance(df, pd.DataFrame) and not df.empty:
        df.columns = [c.strip().lower() for c in df.columns]
        for k in out.keys():
            if k in df.columns and not df[k].isna().all():
                # take first non-null
                val = df[k].dropna().iloc[0]
                out[k] = val
    return out

def low_doc_alerts(threshold: int = 10) -> pd.DataFrame:
    inv = _read_tab("inventory")
    if inv.empty: 
        return pd.DataFrame(columns=["sku","asin","days_of_cover"])
    inv.columns = [c.strip().lower() for c in inv.columns]
    doc_col = next((c for c in inv.columns if c.lower() in ["days of cover","daysofcover","doc","days_of_cover"]), None)
    if not doc_col:
        return pd.DataFrame(columns=["sku","asin","days_of_cover"])
    doc = pd.to_numeric(inv[doc_col], errors="coerce")
    out = inv.loc[doc.lt(threshold)].copy()
    out.rename(columns={doc_col: "days_of_cover"}, inplace=True)
    return out[["sku"] + (["asin"] if "asin" in out.columns else []) + ["days_of_cover"]]

def compliance_due_alerts(due_days: int = 30) -> pd.DataFrame:
    df = _read_tab("compliance")
    if df.empty: 
        return pd.DataFrame(columns=["asin","doc_type","expires_on","days_to_expiry"])
    df.columns = [c.strip().lower() for c in df.columns]
    if "expires_on" not in df.columns:
        return pd.DataFrame(columns=["asin","doc_type","expires_on","days_to_expiry"])
    d = df.copy()
    d["expires_on"] = pd.to_datetime(d["expires_on"], errors="coerce")
    today = pd.Timestamp.utcnow().normalize()
    d["days_to_expiry"] = (d["expires_on"] - today).dt.days
    out = d.loc[d["days_to_expiry"].le(due_days)].copy()
    keep = [c for c in ["asin","doc_type","expires_on","days_to_expiry"] if c in out.columns]
    return out[keep].sort_values("days_to_expiry")

def ppc_negatives_surge(min_spend: float = 10.0, min_clicks: int = 12) -> pd.DataFrame:
    """Surface recent negatives from `ppc_negatives` and any rows meeting surge criteria in `ppc_import`.

    This is a heuristic until Ads API is live."""
    negs = _read_tab("ppc_negatives")
    imp = _read_tab("ppc_import")
    out_list = []

    if isinstance(negs, pd.DataFrame) and not negs.empty:
        negs.columns = [c.strip().lower() for c in negs.columns]
        k = [c for c in negs.columns if c in ("keyword","search term","search_term","query")]
        if k:
            tmp = negs.copy()
            tmp["source"] = "manual_negative"
            tmp.rename(columns={k[0]:"keyword"}, inplace=True)
            out_list.append(tmp[["keyword","source"]])

    if isinstance(imp, pd.DataFrame) and not imp.empty:
        imp.columns = [c.strip().lower() for c in imp.columns]
        spend = imp.get("spend") or imp.get("cost")
        clicks = imp.get("clicks")
        orders = imp.get("orders") or imp.get("purchases") or imp.get("conversions")
        kw = None
        for c in ["keyword","search term","search_term","query"]:
            if c in imp.columns: kw = c; break
        if kw is not None and spend is not None and clicks is not None and orders is not None:
            cond = (orders.fillna(0)==0) & ((spend.fillna(0) >= float(min_spend)) | (clicks.fillna(0) >= int(min_clicks)))
            tmp = imp.loc[cond, [kw]].copy()
            tmp["source"] = "surge_spend_or_clicks"
            tmp.rename(columns={kw:"keyword"}, inplace=True)
            out_list.append(tmp)

    if not out_list:
        return pd.DataFrame(columns=["keyword","source"])
    return pd.concat(out_list, ignore_index=True).drop_duplicates().sort_values("keyword")
