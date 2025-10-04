
from __future__ import annotations
import os
from dataclasses import dataclass
from typing import Optional
import streamlit as st

@dataclass
class AppConfig:
    timezone: str = "America/Los_Angeles"
    base_currency: str = "USD"
    report_start_date: str = "2025-01-01"
    ads_enabled: bool = True
    auto_snapshot_pdf: bool = True

def _get_secret(key: str, default=None):
    # Read from st.secrets first, then env, then default
    try:
        return st.secrets.get(key, default)
    except Exception:
        return os.getenv(key.upper(), default)

def load_config() -> AppConfig:
    tz = _get_secret("timezone", "America/Los_Angeles")
    cur = _get_secret("base_currency", "USD")
    rsd = _get_secret("report_start_date", "2025-01-01")
    ads = _get_secret("ads_enabled", True)
    snap = _get_secret("auto_snapshot_pdf", True)

    # simple validation
    if not isinstance(tz, str) or "/" not in tz:
        tz = "America/Los_Angeles"
    if not isinstance(cur, str) or len(cur) not in (3,):
        cur = "USD"
    if not isinstance(rsd, str) or len(rsd) < 8:
        rsd = "2025-01-01"
    ads = bool(ads)
    snap = bool(snap)

    return AppConfig(
        timezone=tz,
        base_currency=cur,
        report_start_date=rsd,
        ads_enabled=ads,
        auto_snapshot_pdf=snap,
    )
