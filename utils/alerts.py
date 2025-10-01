
from dataclasses import dataclass, asdict
from typing import List
import pandas as pd

@dataclass
class Alert:
    severity: str   # e.g., crit|warn|info
    message: str
    source: str = "system"

def alerts_to_df(items: List['Alert']) -> pd.DataFrame:
    if not items:
        return pd.DataFrame(columns=["severity","message","source"])
    return pd.DataFrame([asdict(a) for a in items])

def product_alerts(df: pd.DataFrame) -> List['Alert']:
    """Generate basic product alerts from the Product Tracker dataframe.
    Expected columns: SKU, Days of Cover, Inventory, Suppressed?, CVR%, Stars
    """
    items: List[Alert] = []
    if df is None or df.empty:
        return items
    # Normalize columns in case of mismatched names
    cols = {c.lower(): c for c in df.columns}
    def col(name):
        return cols.get(name.lower(), name)
    for _, r in df.iterrows():
        sku = str(r.get(col("SKU"), ""))
        # Suppressed listing
        suppressed = r.get(col("Suppressed?"), False)
        try:
            suppressed = bool(suppressed)
        except Exception:
            suppressed = False
        if suppressed:
            items.append(Alert(severity="crit", message=f"Suppressed listing: {sku}", source="Product"))
        # Low cover
        cov = r.get(col("Days of Cover"))
        try:
            cov_val = float(cov) if pd.notna(cov) else None
        except Exception:
            cov_val = None
        if cov_val is not None and cov_val < 14:
            items.append(Alert(severity="warn", message=f"Low cover (<14d): {sku} has {int(cov_val)} days", source="Inventory"))
        # Ratings
        stars = r.get(col("Stars"))
        try:
            stars_val = float(stars) if pd.notna(stars) else None
        except Exception:
            stars_val = None
        if stars_val is not None and stars_val < 4.2:
            items.append(Alert(severity="info", message=f"Rating below 4.2: {sku} at {stars_val:.2f}", source="Reviews"))
        # Conversion
        cvr = r.get(col("CVR%"))
        try:
            cvr_val = float(cvr) if pd.notna(cvr) else None
        except Exception:
            cvr_val = None
        if cvr_val is not None and cvr_val < 4.5:
            items.append(Alert(severity="info", message=f"Low CVR: {sku} at {cvr_val:.1f}%", source="Conversion"))
    return items
