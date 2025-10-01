"""
Amazon Advertising Reporting API v3 helper.
- Creates Sponsored Products (SP) performance reports
- Polls until READY
- Downloads and parses report into a pandas DataFrame
- Falls back to sample if anything fails

Requires the same LWA secrets used by utils.ads_api.AdsClient.
"""
from __future__ import annotations
import io
import gzip
import json
import time
import typing as T
import pandas as pd
import requests
import streamlit as st
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from utils.ads_api import AdsClient, AdsAuthError, AdsApiError, ADS_API_BASE

REPORTS_BASE = f"{ADS_API_BASE}/v3/reports"

class AdsReportError(Exception): ...

def _headers(access_token: str, profile_id: str) -> dict:
    return {
        "Authorization": f"Bearer {access_token}",
        "Amazon-Advertising-API-ClientId": st.secrets.get("sp_api_client_id",""),
        "Amazon-Advertising-API-Scope": str(profile_id),
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

def _sample_df() -> pd.DataFrame:
    from utils.ads_api import AdsClient
    return AdsClient().get_sample_metrics()

def _normalize_rows(rows: T.List[dict]) -> pd.DataFrame:
    """Expect fields like date, campaignName, impressions, clicks, cost, attributableConversions14d, attributableSales14d"""
    if not rows:
        return pd.DataFrame()
    df = pd.json_normalize(rows)
    # Canonicalize columns
    rename = {
        "date": "Date",
        "campaignName": "Campaign",
        "impressions": "Impressions",
        "clicks": "Clicks",
        "cost": "Spend",
        "attributableConversions14d": "Orders",
        "attributableSales14d": "Sales"
    }
    for k, v in rename.items():
        if k in df.columns:
            df.rename(columns={k: v}, inplace=True)
    # Compute ratios
    if "Spend" in df.columns and "Sales" in df.columns:
        df["ROAS"] = (df["Sales"] / df["Spend"]).replace([float("inf"), -float("inf")], 0.0).fillna(0.0)
    else:
        df["ROAS"] = 0.0
    if "Spend" in df.columns and "Sales" in df.columns:
        # ACOS% = Spend / Sales * 100
        df["ACoS%"] = (df["Spend"] / df["Sales"]).replace([float("inf"), -float("inf")], 0.0).fillna(0.0) * 100.0
    else:
        df["ACoS%"] = 0.0
    # Ensure proper dtypes
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    for c in ["Impressions", "Clicks", "Orders"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0).astype(int)
    for c in ["Spend", "Sales", "ROAS", "ACoS%"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0.0)
    if "Campaign" not in df.columns:
        df["Campaign"] = "(unknown)"
    # Sort by date
    if "Date" in df.columns:
        df = df.sort_values("Date")
    return df[["Date","Campaign","Impressions","Clicks","Spend","Orders","ACoS%","ROAS"]].copy()

def _build_sp_report_body(start_date: str, end_date: str) -> dict:
    """
    Build a Sponsored Products campaigns placement performance report over a date range.
    Dates must be ISO yyyy-mm-dd.
    """
    # Basic report definition — campaign level
    return {
        "name": "cockpit_sp_campaign_performance",
        "version": "3.4",  # as of 2025
        "timeUnit": "DAILY",
        "reportTypeId": "spCampaigns",
        "configuration": {
            "columns": [
                "date",
                "campaignName",
                "impressions",
                "clicks",
                "cost",
                "attributableConversions14d",
                "attributableSales14d"
            ],
            "timeRange": {
                "start": start_date,
                "end": end_date
            },
            "filters": [
                {"field": "campaignStatus", "values": ["ENABLED","PAUSED"]}
            ]
        }
    }

@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=20), reraise=True)
def create_report(profile_id: str, start_date: str, end_date: str) -> str:
    ads = AdsClient()
    if not ads.available():
        raise AdsReportError("Missing LWA/SP-API secrets")
    tok = ads._token()
    body = _build_sp_report_body(start_date, end_date)
    r = requests.post(REPORTS_BASE, headers=_headers(tok, profile_id), json=body, timeout=30)
    if r.status_code not in (200, 202):
        raise AdsReportError(f"Create report failed: {r.status_code} {r.text[:200]}")
    return r.json().get("reportId")

@retry(stop=stop_after_attempt(20), wait=wait_exponential(min=2, max=30), reraise=True)
def wait_for_report(profile_id: str, report_id: str) -> dict:
    ads = AdsClient()
    tok = ads._token()
    r = requests.get(f"{REPORTS_BASE}/{report_id}", headers=_headers(tok, profile_id), timeout=20)
    if r.status_code != 200:
        raise AdsReportError(f"Get report failed: {r.status_code} {r.text[:200]}")
    js = r.json()
    status = js.get("status")
    if status not in ("COMPLETED", "SUCCESS", "READY"):
        # Will retry by raising
        raise AdsReportError(f"Not ready yet: {status}")
    return js

def download_report(profile_id: str, report_id: str) -> pd.DataFrame:
    ads = AdsClient()
    tok = ads._token()
    # get metadata to find url
    meta = requests.get(f"{REPORTS_BASE}/{report_id}", headers=_headers(tok, profile_id), timeout=20)
    if meta.status_code != 200:
        raise AdsReportError(f"Get meta failed: {meta.status_code} {meta.text[:200]}")
    url = meta.json().get("url")
    if not url:
        raise AdsReportError("No download url in report metadata.")
    # download gz
    gz = requests.get(url, timeout=60)
    gz.raise_for_status()
    buf = io.BytesIO(gz.content)
    with gzip.GzipFile(fileobj=buf, mode="rb") as f:
        data = f.read()
    # parse JSON rows
    try:
        js = json.loads(data.decode("utf-8"))
        if isinstance(js, dict) and "report" in js:
            rows = js["report"]
        elif isinstance(js, list):
            rows = js
        else:
            rows = []
    except Exception:
        # Sometimes report is TSV
        try:
            import pandas as pd
            df = pd.read_csv(io.BytesIO(data), sep="\t")
            return _normalize_rows(df.to_dict(orient="records"))
        except Exception:
            rows = []
    return _normalize_rows(rows)

def fetch_sp_metrics(profile_id: str, start_date: str, end_date: str) -> pd.DataFrame:
    """High-level convenience: create → wait → download → normalize. Fallback to sample on failure."""
    try:
        rid = create_report(profile_id, start_date, end_date)
        wait_for_report(profile_id, rid)
        df = download_report(profile_id, rid)
        if df is None or df.empty:
            return _sample_df()
        return df
    except Exception as e:
        st.warning(f"Reporting fell back to sample data: {e}")
        return _sample_df()
