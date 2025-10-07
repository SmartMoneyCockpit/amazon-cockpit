
from __future__ import annotations
from typing import Dict, Tuple, Any
import os, datetime as dt
FIELDS=["timezone","base_currency","report_start_date","ads_enabled","auto_snapshot_pdf"]
def _get_secret(key, default=None):
    try:
        import streamlit as st
        if key in st.secrets: return st.secrets.get(key, default), "secrets"
    except Exception: pass
    val=os.getenv(key.upper(), default)
    if val is not None: return val, "env"
    return default, "default"
def read_from_sheets()->Dict[str,Any]:
    try:
        from infra.sheets_client import SheetsClient
        sc=SheetsClient(); rows=sc.read_table("Settings")
        out={}
        for r in rows:
            k=str(r.get("key","")).strip(); v=r.get("value", None)
            if k: out[k]=v
        return out
    except Exception: return {}
def load_settings()->Tuple[Dict[str,Any], Dict[str,str], str]:
    last_sync=dt.datetime.utcnow().isoformat()+"Z"
    values={}; sources={}
    sheet=read_from_sheets()
    defaults={"timezone":"America/Los_Angeles","base_currency":"USD","report_start_date":"2025-01-01","ads_enabled":True,"auto_snapshot_pdf":True}
    for key in FIELDS:
        if key in sheet and sheet[key] not in (None,""):
            values[key]=sheet[key]; sources[key]="sheets"
        else:
            val,orig=_get_secret(key,None)
            if val not in (None,""):
                values[key]=val; sources[key]= "secrets" if orig=="secrets" else "env"
            else:
                values[key]=defaults.get(key); sources[key]="default"
    return values, sources, last_sync
