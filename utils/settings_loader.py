
from __future__ import annotations
from typing import Dict, Tuple, Any
import os, datetime as dt

FIELDS = ["timezone", "base_currency", "report_start_date", "ads_enabled", "auto_snapshot_pdf"]

def _get_secret(key: str, default=None):
    try:
        import streamlit as st
        if key in st.secrets:
            return st.secrets.get(key, default), "secrets"
    except Exception:
        pass
    val = os.getenv(key.upper(), default)
    if val is not None:
        return val, "env"
    return default, "default"

def read_from_sheets() -> Dict[str, Any]:
    # Return dict from Google Sheets 'Settings' worksheet if available; else empty.
    try:
        from infra.sheets_client import SheetsClient
        sc = SheetsClient()
        rows = sc.read_table("Settings")  # expects key/value
        out: Dict[str, Any] = {}
        for r in rows:
            k = str(r.get("key","")).strip()
            v = r.get("value", None)
            if not k:
                continue
            out[k] = v
        return out
    except Exception:
        return {}

def load_settings() -> Tuple[Dict[str, Any], Dict[str, str], str]:
    # Returns (values, sources, last_sync_utc_iso). Priority: Sheets -> secrets/env -> defaults.
    last_sync = dt.datetime.utcnow().isoformat() + "Z"
    values: Dict[str, Any] = {}
    sources: Dict[str, str] = {}

    sheet_vals = read_from_sheets()
    for key in FIELDS:
        if key in sheet_vals and sheet_vals[key] not in (None, ""):
            values[key] = sheet_vals[key]
            sources[key] = "sheets"
        else:
            val, origin = _get_secret(key, None)
            if val is not None and val != "":
                values[key] = val
                sources[key] = "secrets" if origin == "secrets" else "env"
            else:
                defaults = {
                    "timezone": "America/Los_Angeles",
                    "base_currency": "USD",
                    "report_start_date": "2025-01-01",
                    "ads_enabled": True,
                    "auto_snapshot_pdf": True,
                }
                values[key] = defaults.get(key, None)
                sources[key] = "default"
    return values, sources, last_sync
