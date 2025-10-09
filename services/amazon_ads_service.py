import os, time, json, gzip, io, sqlite3, requests, pathlib, datetime

ADS_BASE   = os.getenv("AMZ_ADS_API_BASE", "https://advertising-api.amazon.com")
CLIENT_ID  = os.getenv("AMZ_ADS_CLIENT_ID")
CLIENT_SEC = os.getenv("AMZ_ADS_CLIENT_SECRET")
REFRESH    = os.getenv("AMZ_ADS_REFRESH_TOKEN")
PROFILE_ID = os.getenv("AMZ_ADS_PROFILE_ID")
INCLUDE_ARCHIVED = os.getenv("VEGA_ADS_INCLUDE_ARCHIVED", "false").lower() == "true"
CACHE_DAYS = int(os.getenv("VEGA_ADS_CACHE_DAYS", "35"))
DATA_DIR = os.getenv("VEGA_DATA_DIR", "/data")
DB_PATH = os.path.join(DATA_DIR, "vega_ads.db")

pathlib.Path(DATA_DIR).mkdir(parents=True, exist_ok=True)

_token = {"val": None, "exp": 0}

def _now(): return int(time.time())

def _access_token():
    if _token["val"] and _token["exp"] > _now() + 60:
        return _token["val"]
    r = requests.post("https://api.amazon.com/auth/o2/token", data={
        "grant_type": "refresh_token",
        "refresh_token": REFRESH,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SEC,
    }, timeout=60)
    r.raise_for_status()
    j = r.json()
    _token["val"] = j["access_token"]
    _token["exp"] = _now() + int(j.get("expires_in", 3600))
    return _token["val"]

def _base_headers():
    return {
        "Authorization": f"Bearer {_access_token()}",
        "Amazon-Advertising-API-ClientId": CLIENT_ID,
        "Amazon-Advertising-API-Scope": str(PROFILE_ID),
        "Accept": "application/json",
    }

# ---------------- DB helpers ----------------
def _db():
    con = sqlite3.connect(DB_PATH, check_same_thread=False)
    con.row_factory = sqlite3.Row
    return con

def _init_db():
    con = _db()
    cur = con.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS metrics(
        adType TEXT, date TEXT, campaignId TEXT, campaignName TEXT,
        impressions REAL, clicks REAL, cost REAL, purchases14d REAL, sales14d REAL,
        profileId TEXT, createdAt TEXT DEFAULT (datetime('now'))
    )""")
    cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS ux_metrics ON metrics(adType,date,campaignId,profileId)")
    cur.execute("""CREATE TABLE IF NOT EXISTS job_meta(
        adType TEXT, reportId TEXT, status TEXT, url TEXT, startedAt TEXT, completedAt TEXT
    )""")
    cur.execute("""CREATE TABLE IF NOT EXISTS saved_views(
        name TEXT PRIMARY KEY, payload TEXT
    )""")
    con.commit()
    con.close()

_init_db()

# -------- Profiles --------
def get_profiles():
    r = requests.get(f"{ADS_BASE}/v2/profiles", headers=_base_headers(), timeout=60)
    if r.status_code == 401:
        _token["val"] = None
        r = requests.get(f"{ADS_BASE}/v2/profiles", headers=_base_headers(), timeout=60)
    r.raise_for_status()
    return r.json()

# -------- Campaign lists --------
def _filter_archived(rows):
    if INCLUDE_ARCHIVED: return rows
    out = []
    for c in rows:
        st = (c.get("state") or "").lower()
        if st != "archived":
            out.append(c)
    return out

def list_sp_campaigns(count=1000, start_index=0):
    h = _base_headers()
    h["Accept"] = "application/vnd.spcampaign.v3+json"
    h["Content-Type"] = "application/vnd.spcampaign.v3+json"
    body = {"startIndex": start_index, "count": count}
    r = requests.post(f"{ADS_BASE}/sp/campaigns/list", headers=h, json=body, timeout=60)
    r.raise_for_status()
    data = r.json().get("campaigns", [])
    return _filter_archived(data)

def list_sb_campaigns():
    h = _base_headers()
    h["Accept"] = "application/vnd.sbcampaignresource.v4+json"
    r = requests.post(f"{ADS_BASE}/sb/v4/campaigns/list", headers=h, timeout=60)
    r.raise_for_status()
    data = r.json().get("campaigns", [])
    return _filter_archived(data)

def list_sd_campaigns(count=1000, start_index=0, state_filter="enabled,paused"):
    h = _base_headers()
    h["Amazon-Advertising-API-Version"] = "3"
    params = {"startIndex": start_index, "count": count, "stateFilter": state_filter}
    r = requests.get(f"{ADS_BASE}/sd/campaigns", headers=h, params=params, timeout=60)
    r.raise_for_status()
    data = r.json()
    return _filter_archived(data)

def list_all_campaigns():
    rows = []
    try:
        for c in list_sp_campaigns():
            rows.append({"type":"SP","campaignId":c.get("campaignId"),"name":c.get("name"),
                         "state":c.get("state"),"budget":c.get("budget"),"startDate":c.get("startDate")})
    except Exception as e:
        rows.append({"type":"SP","error":str(e)})
    try:
        for c in list_sb_campaigns():
            rows.append({"type":"SB","campaignId":c.get("campaignId"),"name":c.get("name"),
                         "state":c.get("state"),"budget":c.get("budget", None),"startDate":c.get("startDate")})
    except Exception as e:
        rows.append({"type":"SB","error":str(e)})
    try:
        for c in list_sd_campaigns():
            rows.append({"type":"SD","campaignId":c.get("campaignId"),"name":c.get("name"),
                         "state":c.get("state"),"budget":c.get("budget"),"startDate":c.get("startDate")})
    except Exception as e:
        rows.append({"type":"SD","error":str(e)})
    return rows

# ---------- Reporting API ----------
def _post_report(url, body, media_candidates):
    last = None
    for accept, content in media_candidates:
        h = _base_headers()
        h["Accept"] = accept
        h["Content-Type"] = content
        r = requests.post(url, headers=h, json=body, timeout=90)
        if r.status_code in (406, 415):
            last = r
            continue
        r.raise_for_status()
        return r
    if last is not None: last.raise_for_status()
    raise RuntimeError("All media-type attempts failed")

def create_sp_report(start_date, end_date, time_unit="DAILY"):
    body = {
        "name": "vega-sp-campaigns",
        "startDate": str(start_date),
        "endDate": str(end_date),
        "configuration": {
            "adProduct": "SPONSORED_PRODUCTS",
            "groupBy": ["campaign"],
            "columns": ["date","campaignId","campaignName","impressions","clicks","cost","purchases14d","sales14d"],
            "timeUnit": time_unit,
            "format": "GZIP_JSON",
        },
    }
    media = [("application/vnd.spreport.v3+json", "application/json"),
             ("application/vnd.spreport.v3+json", "application/vnd.spreport.v3+json")]
    return _post_report(f"{ADS_BASE}/sp/reports", body, media).json().get("reportId")

def create_sb_report(start_date, end_date, time_unit="DAILY"):
    body = {
        "name": "vega-sb-campaigns",
        "startDate": str(start_date),
        "endDate": str(end_date),
        "configuration": {
            "adProduct": "SPONSORED_BRANDS",
            "groupBy": ["campaign"],
            "columns": ["date","campaignId","campaignName","impressions","clicks","cost","purchases14d","sales14d"],
            "timeUnit": time_unit,
            "format": "GZIP_JSON",
        },
    }
    media = [("application/vnd.sbreport.v4+json", "application/json")]
    return _post_report(f"{ADS_BASE}/sb/reports", body, media).json().get("reportId")

def create_sd_report(start_date, end_date, time_unit="DAILY"):
    body = {
        "name": "vega-sd-campaigns",
        "startDate": str(start_date),
        "endDate": str(end_date),
        "configuration": {
            "adProduct": "SPONSORED_DISPLAY",
            "groupBy": ["campaign"],
            "columns": ["date","campaignId","campaignName","impressions","clicks","cost","purchases14d","sales14d"],
            "timeUnit": time_unit,
            "format": "GZIP_JSON",
        },
    }
    media = [("application/vnd.sdreport.v3+json", "application/json")]
    return _post_report(f"{ADS_BASE}/sd/reports", body, media).json().get("reportId")

def _poll_report(ad_type, report_id, timeout_sec=240, interval=3):
    paths = [
        f"{ADS_BASE}/{ad_type.lower()}/reports/{report_id}",
        f"{ADS_BASE}/reports/{report_id}",
    ]
    start = time.time()
    while time.time() - start < timeout_sec:
        for p in paths:
            h = _base_headers()
            r = requests.get(p, headers=h, timeout=60)
            if r.status_code == 404:
                continue
            r.raise_for_status()
            j = r.json()
            status = (j.get("status") or j.get("processingStatus") or "").upper()
            if status in ("SUCCESS","COMPLETED"):
                return j
            if status in ("FAILURE","FAILED"):
                raise RuntimeError(f"Report failed: {j}")
        time.sleep(interval)
    raise TimeoutError(f"{ad_type} report not ready after {timeout_sec}s")

def _download_report(url):
    r = requests.get(url, timeout=180)
    r.raise_for_status()
    data = r.content
    try:
        import gzip
        with gzip.GzipFile(fileobj=io.BytesIO(data)) as gz:
            data = gz.read()
    except Exception:
        pass
    txt = data.decode("utf-8", errors="ignore").strip()
    if txt.startswith("["):
        return json.loads(txt)
    return [json.loads(line) for line in txt.splitlines() if line.strip()]

def upsert_metrics(rows):
    con = _db()
    cur = con.cursor()
    for r in rows:
        cur.execute("""INSERT OR REPLACE INTO metrics
            (adType,date,campaignId,campaignName,impressions,clicks,cost,purchases14d,sales14d,profileId)
            VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (r.get("adType"), str(r.get("date")), str(r.get("campaignId")), r.get("campaignName"),
             r.get("impressions",0), r.get("clicks",0), r.get("cost",0),
             r.get("purchases14d",0), r.get("sales14d",0), str(PROFILE_ID)))
    con.commit()
    con.close()

def fetch_metrics(start_date, end_date, which=("SP","SB","SD"), persist=True):
    jobs = []
    if "SP" in which:
        rid = create_sp_report(start_date, end_date); 
        if rid: jobs.append(("sp", rid))
    if "SB" in which:
        rid = create_sb_report(start_date, end_date); 
        if rid: jobs.append(("sb", rid))
    if "SD" in which:
        rid = create_sd_report(start_date, end_date); 
        if rid: jobs.append(("sd", rid))

    out = []
    for ad_type, rid in jobs:
        meta = _poll_report(ad_type, rid)
        url = meta.get("url") or meta.get("location")
        rows = _download_report(url) if url else []
        for r in rows:
            r["adType"] = ad_type.upper()
        out.extend(rows)
    if persist and out:
        upsert_metrics(out)
    return out