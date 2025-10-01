from dataclasses import dataclass
from typing import List, Dict, Any
import pandas as pd

@dataclass
class Alert:
    severity: str   # "info" | "warn" | "crit"
    message: str
    source: str     # e.g., "Product", "PPC"

def product_alerts(df: pd.DataFrame) -> List[Alert]:
    alerts: List[Alert] = []
    if df is None or df.empty:
        return alerts
    # Low stock / low days of cover
    low_doc = df[df.get("Days of Cover", 999) < 10]
    for _, r in low_doc.iterrows():
        alerts.append(Alert("warn", f"{r.get('SKU','?')} running low: {r.get('Days of Cover')} days of cover", "Product"))
    # Suppressed flag
    suppressed = df[df.get("Suppressed?", False) == True]
    for _, r in suppressed.iterrows():
        alerts.append(Alert("crit", f"{r.get('ASIN','?')} is suppressed", "Product"))
    return alerts

def ppc_alerts(df: pd.DataFrame, acos_threshold: float = 35.0) -> List[Alert]:
    alerts: List[Alert] = []
    if df is None or df.empty:
        return alerts
    high_acos = df[df.get("ACoS%", 0) > acos_threshold]
    if not high_acos.empty:
        last = float(high_acos["ACoS%"].tail(1).values[0])
        alerts.append(Alert("warn", f"ACoS breach: latest {last:.1f}% > {acos_threshold:.1f}%", "PPC"))
    return alerts

def alerts_to_df(items: List[Alert]) -> pd.DataFrame:
    return pd.DataFrame([a.__dict__ for a in items]) if items else pd.DataFrame(columns=["severity","message","source"])
