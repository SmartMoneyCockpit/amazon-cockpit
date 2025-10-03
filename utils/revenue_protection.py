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

def build_revenue_protection() -> pd.DataFrame:
    mb = _read_tab('alerts_out_margins')
    ppc = _read_tab('alerts_out_ppc')
    inv = _read_tab('inventory')
    for df in [mb, ppc, inv]:
        try:
            df.columns = [c.strip().lower() for c in df.columns]
        except Exception:
            pass
    map_df = inv[['sku','asin']].dropna().drop_duplicates() if not inv.empty and {'sku','asin'} <= set(inv.columns) else pd.DataFrame()
    def ensure_keys(df: pd.DataFrame):
        if df.empty: return df
        d = df.copy()
        if 'sku' not in d.columns and 'asin' in d.columns and not map_df.empty:
            d = d.merge(map_df, on='asin', how='left')
        if 'asin' not in d.columns and 'sku' in d.columns and not map_df.empty:
            d = d.merge(map_df, on='sku', how='left')
        return d
    mb = ensure_keys(mb)
    ppc = ensure_keys(ppc)
    if mb.empty and ppc.empty:
        return pd.DataFrame(columns=['sku','asin','cause','severity','suggested_action'])
    keys = list(set([k for k in ['sku','asin'] if (k in mb.columns) or (k in ppc.columns)]))
    if not mb.empty and not ppc.empty:
        rp = pd.merge(mb, ppc, on=keys, how='outer', suffixes=('_m','_p'))
    elif not mb.empty:
        rp = mb.copy()
    else:
        rp = ppc.copy()
    rp['has_margin'] = (~rp.filter(regex='net_margin_pct|reason').isna().all(axis=1)) if not rp.empty else False
    rp['has_ppc'] = (rp.filter(regex='keyword|source').notna().any(axis=1)) if not rp.empty else False
    def _cause(row):
        if row.get('has_margin') and row.get('has_ppc'): return 'both'
        if row.get('has_margin'): return 'margin_only'
        if row.get('has_ppc'): return 'ppc_only'
        return 'unknown'
    rp['cause'] = rp.apply(_cause, axis=1) if not rp.empty else None
    rp['severity'] = rp['cause'].map({'both':'red','margin_only':'yellow','ppc_only':'yellow'}).fillna('yellow')
    rp['suggested_action'] = rp['cause'].map({
        'both': 'Cut PPC bids & review COGS/fees; check SKU economics',
        'margin_only': 'Review COGS/fees; adjust price if needed',
        'ppc_only': 'Add negatives or reduce bids'
    }).fillna('Review details')
    out_cols = [c for c in ['sku','asin','cause','severity','suggested_action'] if c in rp.columns]
    for c in ['net_margin_pct','gross_margin_pct','keyword','source','month','revenue','fees','other','net']:
        cols = [col for col in rp.columns if col == c or col.endswith(f'_{c}')]
        out_cols += [col for col in cols if col not in out_cols]
    return rp[out_cols].drop_duplicates()
