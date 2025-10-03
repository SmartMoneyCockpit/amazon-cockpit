from __future__ import annotations
import pandas as pd
from typing import Dict, Any
from utils.margins_guard import margin_breaches

def _read_tab(name: str):
    try:
        from utils import sheets_bridge as SB
        return SB.read_tab(name)
    except Exception:
        return pd.DataFrame()

def load_thresholds() -> Dict[str, Any]:
    df = _read_tab("alerts_settings")
    out = {
        "doc_days_low": 10,
        "compliance_due_days": 30,
        "ppc_min_spend": 10.0,
        "ppc_min_clicks": 12,
        "net_margin_min_pct": 0.0,
        "gross_margin_min_pct": 15.0,
    }
    if isinstance(df, pd.DataFrame) and not df.empty:
        df.columns = [c.strip().lower() for c in df.columns]
        for k in out.keys():
            if k in df.columns and not df[k].isna().all():
                out[k] = df[k].dropna().iloc[0]
    return out

def low_doc_alerts(threshold: int = 10) -> pd.DataFrame:
    from utils.alerts import low_doc_alerts as _low
    return _low(threshold)

def compliance_due_alerts(due_days: int = 30) -> pd.DataFrame:
    from utils.alerts import compliance_due_alerts as _comp
    return _comp(due_days)

def ppc_negatives_surge(min_spend: float = 10.0, min_clicks: int = 12) -> pd.DataFrame:
    from utils.alerts import ppc_negatives_surge as _ppc
    return _ppc(min_spend, min_clicks)

def margin_breach_alerts(net_min: float, gross_min: float) -> pd.DataFrame:
    return margin_breaches(net_margin_pct_thresh=net_min, gross_margin_pct_thresh=gross_min)
