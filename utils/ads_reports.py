
"""Amazon Advertising Reporting API v3 helper (clean/compatible).
Creates Sponsored Products (SP) performance reports, polls until READY, downloads and parses.
Falls back to sample metrics if anything fails.
"""
from __future__ import annotations
import io
import gzip
import json
import time
import typing as T
import requests
import pandas as pd
import streamlit as st
from tenacity import retry, stop_after_attempt, wait_exponential

from utils.ads_api import load_creds, fetch_access_token, region_base, headers
from utils.ads_api import AdsClient

class AdsReportError(Exception): ...
class AdsReportTimeout(AdsReportError): ...

def _headers(access_token: str, profile_id: str) -> dict:
    h = headers(access_token, load_creds().client_id if load_creds() else "", profile_id)
    return h

def _sample_df() -> pd.DataFrame:
    return AdsClient().get_sample_metrics()

def _normalize_rows(rows: T.List[dict]) -> pd.DataFrame:
    if not rows:
        return pd.DataFrame()
    df = pd.json_normalize(rows)
    rename = {
        "date": "Date",
        "campaignName": "Campaign",
        "impressions": "Impressions",
        "clicks": "Clicks",
        "cost": "Spend",
        "attributableConversions14d": "Orders",
        "attributableSales14d": "Sales",
    }
    for k, v in rename.items():
        if k in df.columns and v not in df.columns:
            df[v] = df[k]
    if "Sales" in df.columns and "Spend" in df.columns:
        df["ROAS"] = (df["Sales"].replace(0, 0.0) / df["Spend"].replace(0, 0.0)).replace([float("inf")], 0.0)
        df["ACoS%"] = (df["Spend"].replace(0, 0.0) / df["Sales"].replace(0, 0.0)).replace([float("inf")], 0.0) * 100
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    for c in ["Impressions","Clicks","Orders"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0).astype(int)
    for c in ["Spend","Sales","ROAS","ACoS%"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0.0)
    if "Campaign" not in df.columns:
        df["Campaign"] = "(unknown)"
    if "Date" in df.columns:
        df = df.sort_values("Date")
    cols = [c for c in ["Date","Campaign","Impressions","Clicks","Spend","Orders","ACoS%","ROAS"] if c in df.columns]
    return df[cols].copy()

def _build_sp_report_body(start_date: str, end_date: str) -> dict:
    return {
        "name": "cockpit_sp_campaign_performance",
        "version": "3.4",
        "timeUnit": "DAILY",
        "reportTypeId": "spCampaigns",
        "configuration": {
            "columns": [
                "date","campaignName","impressions","clicks","cost",
                "attributableConversions14d","attributableSales14d"
            ],
            "timeRange": {"start": start_date, "end": end_date},
            "filters": [{"field": "campaignStatus", "values": ["ENABLED","PAUSED"]}],
        },
    }

def _token() -> str:
    creds = load_creds()
    if not creds:
        raise AdsReportError("Missing client/secret/refresh_token")
    return fetch_access_token(creds)

def create_report(profile_id: str, start_date: str, end_date: str) -> str:
    tok = _token()
    body = _build_sp_report_body(start_date, end_date)
    r = requests.post(f"{region_base()}/reporting/reports", headers=_headers(tok, profile_id), json=body, timeout=30)
    if r.status_code not in (200, 202):
        raise AdsReportError(f"create_report {r.status_code}: {r.text[:200]}")
    js = r.json()
    return js.get("reportId") or js.get("reportId".lower()) or list(js.values())[0]

@retry(stop=stop_after_attempt(30), wait=wait_exponential(min=1, max=20), reraise=True)
def wait_for_report(profile_id: str, report_id: str) -> None:
    tok = _token()
    while True:
        r = requests.get(f"{region_base()}/reporting/reports/{report_id}", headers=_headers(tok, profile_id), timeout=20)
        if r.status_code != 200:
            raise AdsReportError(f"report status {r.status_code}: {r.text[:200]}")
        status = r.json().get("status", "").upper()
        if status == "READY":
            return
        if status in {"CANCELLED","FAILED"}:
            raise AdsReportError(f"report status {status}")
        time.sleep(2)

def download_report(profile_id: str, report_id: str) -> pd.DataFrame:
    tok = _token()
    meta = requests.get(f"{region_base()}/reporting/reports/{report_id}/download", headers=_headers(tok, profile_id), timeout=30)
    if meta.status_code != 200:
        raise AdsReportError(f"download meta {meta.status_code}: {meta.text[:200]}")
    url = meta.json().get("url")
    if not url:
        raise AdsReportError("No download url in report metadata")
    gz = requests.get(url, timeout=60)
    gz.raise_for_status()
    buf = io.BytesIO(gz.content)
    with gzip.GzipFile(fileobj=buf, mode="rb") as f:
        data = f.read()
    try:
        js = json.loads(data.decode("utf-8"))
        rows = js.get("report") if isinstance(js, dict) else (js if isinstance(js, list) else [])
    except Exception:
        try:
            df = pd.read_csv(io.BytesIO(data), sep="\t")
            return _normalize_rows(df.to_dict(orient="records"))
        except Exception:
            rows = []
    return _normalize_rows(rows)

def fetch_sp_metrics(profile_id: str, start_date: str, end_date: str) -> pd.DataFrame:
    try:
        rid = create_report(profile_id, start_date, end_date)
        wait_for_report(profile_id, rid)
        df = download_report(profile_id, rid)
        return df if df is not None and not df.empty else _sample_df()
    except Exception as e:
        st.warning(f"Reporting fell back to sample data: {e}")
        return _sample_df()
