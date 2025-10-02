
from __future__ import annotations
import pandas as pd
from typing import Dict, List
from utils.alerts import load_thresholds, low_doc_alerts, compliance_due_alerts, ppc_negatives_surge

def build_actions(th: Dict) -> pd.DataFrame:
    """Unify alerts into a single actions table.
    Columns: type, key, detail, severity, suggested_action, extra_json
    """
    out: List[pd.DataFrame] = []

    # Low DoC
    try:
        doc_df = low_doc_alerts(int(th.get("doc_days_low", 10)))
        if isinstance(doc_df, pd.DataFrame) and not doc_df.empty:
            d = doc_df.copy()
            d["type"] = "inventory_low_doc"
            d["key"] = d.get("sku", d.get("asin", "unknown"))
            d["detail"] = d.apply(lambda r: f"DoC={r.get('days_of_cover')}", axis=1)
            d["severity"] = d["days_of_cover"].apply(lambda x: "red" if pd.to_numeric(x, errors="coerce")<=5 else "yellow")
            d["suggested_action"] = "Review reorder: check lead time & MOQ"
            out.append(d[["type","key","detail","severity","suggested_action"]])
    except Exception:
        pass

    # Compliance
    try:
        comp_df = compliance_due_alerts(int(th.get("compliance_due_days", 30)))
        if isinstance(comp_df, pd.DataFrame) and not comp_df.empty:
            c = comp_df.copy()
            c["type"] = "compliance_due"
            c["key"] = c.get("asin", "unknown")
            c["detail"] = c.apply(lambda r: f"{r.get('doc_type','Doc')} expiring in {r.get('days_to_expiry')}d", axis=1)
            c["severity"] = c["days_to_expiry"].apply(lambda x: "red" if pd.to_numeric(x, errors="coerce")<=7 else "yellow")
            c["suggested_action"] = "Email vendor for updated docs"
            out.append(c[["type","key","detail","severity","suggested_action"]])
    except Exception:
        pass

    # PPC negatives
    try:
        ppc_df = ppc_negatives_surge(float(th.get("ppc_min_spend", 10.0)), int(th.get("ppc_min_clicks", 12)))
        if isinstance(ppc_df, pd.DataFrame) and not ppc_df.empty:
            p = ppc_df.copy()
            p["type"] = "ppc_negative_candidate"
            p["key"] = p["keyword"]
            p["detail"] = p["source"]
            p["severity"] = "yellow"
            p["suggested_action"] = "Add as negative (review match type)"
            out.append(p[["type","key","detail","severity","suggested_action"]])
    except Exception:
        pass

    if not out:
        return pd.DataFrame(columns=["type","key","detail","severity","suggested_action"])
    actions = pd.concat(out, ignore_index=True)
    # Order by severity: red first, then yellow
    severity_order = pd.Categorical(actions["severity"], categories=["red","yellow","green"], ordered=True)
    actions = actions.assign(severity=severity_order).sort_values(["severity","type","key"]).reset_index(drop=True)
    actions["severity"] = actions["severity"].astype(str)
    return actions
