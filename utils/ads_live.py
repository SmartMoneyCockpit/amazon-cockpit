
from __future__ import annotations
import os, time, json, typing as t

API_BASE = os.getenv("ADS_API_BASE", "https://advertising-api.amazon.com")

def _env(k: str, default: str = "") -> str:
    return os.getenv(k, default).strip()

def have_creds() -> bool:
    return all([_env("ADS_LWA_CLIENT_ID"), _env("ADS_LWA_CLIENT_SECRET"), _env("ADS_REFRESH_TOKEN"), _env("ADS_PROFILE_ID")])

def get_access_token() -> t.Tuple[str, str]:
    """
    Exchanges ADS_REFRESH_TOKEN for an LWA access token (Advertising scope).
    Returns (status, token_or_message)
    """
    import requests
    cid = _env("ADS_LWA_CLIENT_ID")
    secret = _env("ADS_LWA_CLIENT_SECRET")
    refresh = _env("ADS_REFRESH_TOKEN")
    if not all([cid, secret, refresh]):
        return ("skipped", "Missing ADS_LWA_CLIENT_ID / ADS_LWA_CLIENT_SECRET / ADS_REFRESH_TOKEN")
    try:
        resp = requests.post("https://api.amazon.com/auth/o2/token", data={
            "grant_type": "refresh_token",
            "refresh_token": refresh,
            "client_id": cid,
            "client_secret": secret
        }, timeout=20)
        if resp.status_code == 200:
            tok = resp.json().get("access_token")
            if tok:
                return ("ok", tok)
            return ("error", "no access_token in response")
        return ("error", f"token status {resp.status_code}: {resp.text[:200]}")
    except Exception as e:
        return ("error", str(e))

def _headers(token: str) -> dict:
    return {
        "Authorization": f"Bearer {token}",
        "Amazon-Advertising-API-ClientId": _env("ADS_LWA_CLIENT_ID"),
        "Amazon-Advertising-API-Scope": _env("ADS_PROFILE_ID"),  # v3 uses Scope; v2 uses ProfileId header, keep both
        "Content-Type": "application/json"
    }

def list_campaigns(state_filter: str = "enabled") -> t.Tuple[str, t.Any]:
    """
    Lists Sponsored Products campaigns (v2). Returns (status, data).
    Note: not all regions support the same endpoints; this is best-effort.
    """
    import requests
    st, tok = get_access_token()
    if st != "ok":
        return (st, tok)
    url = f"{API_BASE}/v2/sp/campaigns?stateFilter={state_filter}"
    try:
        resp = requests.get(url, headers=_headers(tok), timeout=30)
        if resp.status_code == 200:
            return ("ok", resp.json())
        return ("error", f"{resp.status_code}: {resp.text[:200]}")
    except Exception as e:
        return ("error", str(e))

def list_adgroups(campaign_id: int) -> t.Tuple[str, t.Any]:
    import requests
    st, tok = get_access_token()
    if st != "ok":
        return (st, tok)
    url = f"{API_BASE}/v2/sp/adGroups?campaignIdFilter={campaign_id}"
    try:
        resp = requests.get(url, headers=_headers(tok), timeout=30)
        if resp.status_code == 200:
            return ("ok", resp.json())
        return ("error", f"{resp.status_code}: {resp.text[:200]}")
    except Exception as e:
        return ("error", str(e))

def request_campaign_report(report_date: str) -> t.Tuple[str, t.Any]:
    """
    Creates a Sponsored Products campaigns report for a given date (YYYYMMDD).
    Returns (status, reportId_or_message)
    """
    import requests
    st, tok = get_access_token()
    if st != "ok":
        return (st, tok)
    url = f"{API_BASE}/v2/sp/campaigns/report"
    body = {
        "reportDate": report_date,
        "metrics": "impressions,clicks,cost,attributedSales14d,attributedConversions14d"
    }
    try:
        resp = requests.post(url, json=body, headers=_headers(tok), timeout=30)
        if resp.status_code in (200, 202):
            j = resp.json()
            rid = j.get("reportId") or j.get("reportId".lower())
            return ("ok", rid or j)
        return ("error", f"{resp.status_code}: {resp.text[:200]}")
    except Exception as e:
        return ("error", str(e))

def get_report_status(report_id: str) -> t.Tuple[str, t.Any]:
    import requests
    st, tok = get_access_token()
    if st != "ok":
        return (st, tok)
    url = f"{API_BASE}/v2/reports/{report_id}"
    try:
        resp = requests.get(url, headers=_headers(tok), timeout=30)
        if resp.status_code == 200:
            return ("ok", resp.json())
        return ("error", f"{resp.status_code}: {resp.text[:200]}")
    except Exception as e:
        return ("error", str(e))

def download_report(report_id: str, out_dir: str = "/tmp") -> t.Tuple[str, str]:
    """
    Downloads a ready report to CSV path under out_dir. Returns (status, path_or_message)
    """
    import requests, gzip, io, csv
    st, tok = get_access_token()
    if st != "ok":
        return (st, tok)
    # First get status to fetch location
    s, meta = get_report_status(report_id)
    if s != "ok":
        return (s, str(meta))
    loc = meta.get("location") or meta.get("url")
    if not loc:
        return ("error", "no location in report meta (still processing?)")
    try:
        r = requests.get(loc, headers=_headers(tok), timeout=60)
        if r.status_code != 200:
            return ("error", f"download {r.status_code}: {r.text[:200]}")
        # Most Ads reports are gzipped JSON; convert basic metrics to CSV
        buf = io.BytesIO(r.content)
        try:
            with gzip.GzipFile(fileobj=buf) as gz:
                data = json.loads(gz.read().decode("utf-8"))
        except Exception:
            # Not gzipped
            data = json.loads(r.content.decode("utf-8"))
        rows = data if isinstance(data, list) else data.get("report", data)
        if not isinstance(rows, list):
            return ("error", "unexpected report format")
        # Write CSV
        if not rows:
            return ("ok", f"{out_dir}/ads_campaign_report_{report_id}.csv (empty)")
        keys = sorted(set().union(*(row.keys() for row in rows)))
        path = os.path.join(out_dir, f"ads_campaign_report_{report_id}.csv")
        import csv
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=keys)
            w.writeheader()
            for row in rows:
                w.writerow(row)
        return ("ok", path)
    except Exception as e:
        return ("error", str(e))
