
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

def load_critical_thresholds() -> dict:
    """Reads critical thresholds from alerts_settings, with defaults."""
    df = _read_tab("alerts_settings")
    out = {
        "net_crit": 0.0,        # net margin < 0%
        "gross_crit": 10.0,     # gross margin < 10%
        "ppc_spend_crit": 25.0, # spend >= 25 with 0 orders
        "ppc_clicks_crit": 20,  # clicks >= 20 with 0 orders
        "ppc_lookback_days": 7,
    }
    if isinstance(df, pd.DataFrame) and not df.empty:
        df.columns = [c.strip().lower() for c in df.columns]
        mapping = {
            "net_margin_min_pct_critical": "net_crit",
            "gross_margin_min_pct_critical": "gross_crit",
            "ppc_surge_spend_critical": "ppc_spend_crit",
            "ppc_surge_clicks_critical": "ppc_clicks_crit",
            "lookback_days_ppc_critical": "ppc_lookback_days",
        }
        for src, dst in mapping.items():
            if src in df.columns and not df[src].isna().all():
                out[dst] = df[src].dropna().iloc[0]
    return out

def build_revenue_protection_critical() -> pd.DataFrame:
    """
    Produces a tab 'alerts_out_revenue_protection_critical' with red items where both:
      - margin breach (net < net_crit or gross < gross_crit), AND
      - PPC surge (spend >= ppc_spend_crit OR clicks >= ppc_clicks_crit with 0 orders)
    Joins on SKU/ASIN via inventory mapping.
    """
    th = load_critical_thresholds()
    margins = _read_tab("alerts_out_margins")
    ppc = _read_tab("alerts_out_ppc")
    inv = _read_tab("inventory")

    if margins.empty and ppc.empty:
        return pd.DataFrame(columns=["sku","asin","month","net_margin_pct","gross_margin_pct","ppc_spend","ppc_clicks","reason","severity","suggested_action"])

    # Harmonize keys
    for df in [margins, ppc, inv]:
        try: df.columns = [c.strip().lower() for c in df.columns]
        except Exception: pass

    # Minimal columns for PPC surge detection
    # (we'll try to find columns for spend/clicks/orders)
    spend_col = next((c for c in ["spend","cost"] if c in ppc.columns), None)
    clicks_col = "clicks" if "clicks" in ppc.columns else None
    orders_col = next((c for c in ["orders","conversions","purchases"] if c in ppc.columns), None)

    # Map SKU/ASIN
    map_df = inv[["sku","asin"]].dropna().drop_duplicates() if not inv.empty and {"sku","asin"} <= set(inv.columns) else pd.DataFrame()

    def ensure_keys(df: pd.DataFrame):
        d = df.copy()
        if d.empty: return d
        if "sku" not in d.columns and "asin" in d.columns and not map_df.empty:
            d = d.merge(map_df, on="asin", how="left")
        if "asin" not in d.columns and "sku" in d.columns and not map_df.empty:
            d = d.merge(map_df, on="sku", how="left")
        return d

    margins = ensure_keys(margins)
    ppc = ensure_keys(ppc)

    # Margin breach flag
    if not margins.empty:
        margins["margin_flag"] = (
            (pd.to_numeric(margins.get("net_margin_pct"), errors="coerce") < float(th["net_crit"])) |
            (pd.to_numeric(margins.get("gross_margin_pct"), errors="coerce") < float(th["gross_crit"]))
        )
    else:
        margins["margin_flag"] = False

    # PPC surge flag
    if not ppc.empty:
        spend_ok = True if spend_col is None else (pd.to_numeric(ppc[spend_col], errors="coerce") >= float(th["ppc_spend_crit"]))
        clicks_ok = True if clicks_col is None else (pd.to_numeric(ppc[clicks_col], errors="coerce") >= float(th["ppc_clicks_crit"]))
        orders_zero = True if orders_col is None else (pd.to_numeric(ppc[orders_col], errors="coerce") == 0)
        ppc["ppc_flag"] = (orders_zero & (spend_ok | clicks_ok))
    else:
        ppc["ppc_flag"] = False

    # Join & filter
    if margins.empty and ppc.empty:
        return pd.DataFrame(columns=["sku","asin","month","net_margin_pct","gross_margin_pct","ppc_spend","ppc_clicks","reason","severity","suggested_action"])

    if not margins.empty and not ppc.empty:
        join_keys = [c for c in ["sku","asin"] if c in margins.columns and c in ppc.columns]
        rp = pd.merge(margins, ppc, on=join_keys, how="inner", suffixes=("_m","_p"))
    else:
        return pd.DataFrame(columns=["sku","asin","month","net_margin_pct","gross_margin_pct","ppc_spend","ppc_clicks","reason","severity","suggested_action"])

    # Keep only where both flags true
    rp = rp[rp["margin_flag"] & rp["ppc_flag"]].copy()
    if rp.empty:
        return pd.DataFrame(columns=["sku","asin","month","net_margin_pct","gross_margin_pct","ppc_spend","ppc_clicks","reason","severity","suggested_action"])

    # Build output
    out = pd.DataFrame()
    out["sku"] = rp.get("sku")
    out["asin"] = rp.get("asin")
    out["month"] = rp.get("month") or rp.get("month_m") or rp.get("month_p")
    out["net_margin_pct"] = pd.to_numeric(rp.get("net_margin_pct"), errors="coerce")
    out["gross_margin_pct"] = pd.to_numeric(rp.get("gross_margin_pct"), errors="coerce")
    out["ppc_spend"] = pd.to_numeric(rp.get(spend_col), errors="coerce") if spend_col else pd.NA
    out["ppc_clicks"] = pd.to_numeric(rp.get(clicks_col), errors="coerce") if clicks_col else pd.NA
    out["reason"] = (f"net<{th['net_crit']}% or gross<{th['gross_crit']}%") + " & PPC surge"
    out["severity"] = "red"
    out["suggested_action"] = "Cut PPC bids now + review COGS/fees/price"

    out = out.dropna(how="all").drop_duplicates()
    return out[["sku","asin","month","net_margin_pct","gross_margin_pct","ppc_spend","ppc_clicks","reason","severity","suggested_action"]]
