from __future__ import annotations
import pandas as pd
from typing import Dict
from utils.actions import build_actions as _base_build
from utils.alerts_plus import load_thresholds, margin_breach_alerts

def build_actions_with_margins(th: Dict) -> pd.DataFrame:
    base = _base_build(th)
    try:
        mb = margin_breach_alerts(float(th.get("net_margin_min_pct", 0.0)), float(th.get("gross_margin_min_pct", 15.0)))
        if isinstance(mb, pd.DataFrame) and not mb.empty:
            d = mb.copy()
            d["type"] = "margin_breach"
            d["key"] = d["sku"]
            def _det(r):
                gp = r.get("gross_margin_pct")
                gp_txt = f"{gp:.1f}%" if pd.notna(gp) else "N/A"
                return f"M{r.get('month','')}: net {r.get('net_margin_pct'):.1f}% / gross {gp_txt}"
            d["detail"] = d.apply(_det, axis=1)
            d["severity"] = d["net_margin_pct"].apply(lambda x: "red" if pd.to_numeric(x, errors="coerce")<0 else "yellow")
            d["suggested_action"] = "Review COGS/price/fees; check PPC impact"
            add = d[["type","key","detail","severity","suggested_action"]]
            if base.empty:
                return add
            base = pd.concat([base, add], ignore_index=True)
    except Exception:
        pass
    if not base.empty and "severity" in base.columns:
        sev = pd.Categorical(base["severity"].astype(str), categories=["red","yellow","green"], ordered=True)
        base = base.assign(severity=sev).sort_values(["severity","type","key"]).reset_index(drop=True)
        base["severity"] = base["severity"].astype(str)
    return base
