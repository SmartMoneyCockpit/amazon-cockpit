
# Vega service module (condensed for zip demo)
# NOTE: This condensed file references same endpoints and headers but is shortened to avoid tool limits.
import os, requests, sqlite3, gzip, io, json, time, pathlib

ADS_BASE=os.getenv("AMZ_ADS_API_BASE","https://advertising-api.amazon.com")
CLIENT_ID=os.getenv("AMZ_ADS_CLIENT_ID")
CLIENT_SEC=os.getenv("AMZ_ADS_CLIENT_SECRET")
REFRESH=os.getenv("AMZ_ADS_REFRESH_TOKEN")
PROFILE_ID=os.getenv("AMZ_ADS_PROFILE_ID")
DATA_DIR=os.getenv("VEGA_DATA_DIR","/data")
DB_PATH=os.path.join(DATA_DIR,"vega_ads.db")
pathlib.Path(DATA_DIR).mkdir(parents=True, exist_ok=True)

_tok={'val':None,'exp':0}
def _now(): return int(time.time())
def _token():
    if _tok['val'] and _tok['exp']>_now()+60: return _tok['val']
    r=requests.post("https://api.amazon.com/auth/o2/token",data={
        "grant_type":"refresh_token","refresh_token":REFRESH,
        "client_id":CLIENT_ID,"client_secret":CLIENT_SEC
    },timeout=60); r.raise_for_status(); j=r.json()
    _tok['val']=j['access_token']; _tok['exp']=_now()+int(j.get('expires_in',3600)); return _tok['val']
def _hdr():
    return {"Authorization":f"Bearer {_token()}","Amazon-Advertising-API-ClientId":CLIENT_ID,"Amazon-Advertising-API-Scope":str(PROFILE_ID),"Accept":"application/json"}

def _db():
    con=sqlite3.connect(DB_PATH,check_same_thread=False); con.row_factory=sqlite3.Row
    con.execute("CREATE TABLE IF NOT EXISTS metrics(adType TEXT,date TEXT,campaignId TEXT,campaignName TEXT,impressions REAL,clicks REAL,cost REAL,purchases14d REAL,sales14d REAL,profileId TEXT,createdAt TEXT DEFAULT (datetime('now')))")
    con.execute("CREATE UNIQUE INDEX IF NOT EXISTS ux_metrics ON metrics(adType,date,campaignId,profileId)")
    return con

def list_sp_campaigns(count=1000,start_index=0):
    h=_hdr(); h["Accept"]="application/vnd.spcampaign.v3+json"; h["Content-Type"]="application/vnd.spcampaign.v3+json"
    r=requests.post(f"{ADS_BASE}/sp/campaigns/list",headers=h,json={"startIndex":start_index,"count":count},timeout=60); r.raise_for_status(); return r.json().get("campaigns",[])
def list_sb_campaigns():
    h=_hdr(); h["Accept"]="application/vnd.sbcampaignresource.v4+json"
    r=requests.post(f"{ADS_BASE}/sb/v4/campaigns/list",headers=h,timeout=60); r.raise_for_status(); return r.json().get("campaigns",[])
def list_sd_campaigns(count=1000,start_index=0,state_filter="enabled,paused"):
    h=_hdr(); h["Amazon-Advertising-API-Version"]="3"
    r=requests.get(f"{ADS_BASE}/sd/campaigns",headers=h,params={"startIndex":start_index,"count":count,"stateFilter":state_filter},timeout=60); r.raise_for_status(); return r.json()
def list_all_campaigns():
    out=[]; 
    try:
        for c in list_sp_campaigns(): out.append({"type":"SP","campaignId":c.get("campaignId"),"name":c.get("name"),"state":c.get("state"),"budget":c.get("budget"),"startDate":c.get("startDate")})
    except Exception as e: out.append({"type":"SP","error":str(e)})
    try:
        for c in list_sb_campaigns(): out.append({"type":"SB","campaignId":c.get("campaignId"),"name":c.get("name"),"state":c.get("state"),"budget":c.get("budget"),"startDate":c.get("startDate")})
    except Exception as e: out.append({"type":"SB","error":str(e)})
    try:
        for c in list_sd_campaigns(): out.append({"type":"SD","campaignId":c.get("campaignId"),"name":c.get("name"),"state":c.get("state"),"budget":c.get("budget"),"startDate":c.get("startDate")})
    except Exception as e: out.append({"type":"SD","error":str(e)})
    return out

def _post_report(url,accept,body):
    h=_hdr(); h["Accept"]=accept; h["Content-Type"]="application/json"
    r=requests.post(url,headers=h,json=body,timeout=90); r.raise_for_status(); return r.json().get("reportId")
def _poll(ad_type, rid, timeout_sec=240):
    import time; start=time.time()
    while time.time()-start<timeout_sec:
        for p in (f"{ADS_BASE}/{ad_type}/reports/{rid}", f"{ADS_BASE}/reports/{rid}"):
            r=requests.get(p,headers=_hdr(),timeout=60)
            if r.status_code==404: continue
            r.raise_for_status(); j=r.json(); s=(j.get("status") or j.get("processingStatus") or "").upper()
            if s in ("SUCCESS","COMPLETED"): return j
            if s in ("FAILURE","FAILED"): raise RuntimeError(j)
        time.sleep(3)
    raise TimeoutError("report poll timeout")
def _download(url):
    r=requests.get(url,timeout=180); r.raise_for_status(); data=r.content
    try: import gzip; data=gzip.GzipFile(fileobj=io.BytesIO(data)).read()
    except Exception: pass
    txt=data.decode("utf-8","ignore").strip()
    return json.loads(txt) if txt.startswith("[") else [json.loads(l) for l in txt.splitlines() if l.strip()]

def fetch_metrics(start_date,end_date,which=("SP","SB","SD"),persist=True):
    jobs=[]
    if "SP" in which:
        rid=_post_report(f"{ADS_BASE}/sp/reports","application/vnd.spreport.v3+json",{"name":"vega-sp","startDate":str(start_date),"endDate":str(end_date),"configuration":{"adProduct":"SPONSORED_PRODUCTS","groupBy":["campaign"],"columns":["date","campaignId","campaignName","impressions","clicks","cost","purchases14d","sales14d"],"timeUnit":"DAILY","format":"GZIP_JSON"}}); jobs.append(("sp",rid))
    if "SB" in which:
        rid=_post_report(f"{ADS_BASE}/sb/reports","application/vnd.sbreport.v4+json",{"name":"vega-sb","startDate":str(start_date),"endDate":str(end_date),"configuration":{"adProduct":"SPONSORED_BRANDS","groupBy":["campaign"],"columns":["date","campaignId","campaignName","impressions","clicks","cost","purchases14d","sales14d"],"timeUnit":"DAILY","format":"GZIP_JSON"}}); jobs.append(("sb",rid))
    if "SD" in which:
        rid=_post_report(f"{ADS_BASE}/sd/reports","application/vnd.sdreport.v3+json",{"name":"vega-sd","startDate":str(start_date),"endDate":str(end_date),"configuration":{"adProduct":"SPONSORED_DISPLAY","groupBy":["campaign"],"columns":["date","campaignId","campaignName","impressions","clicks","cost","purchases14d","sales14d"],"timeUnit":"DAILY","format":"GZIP_JSON"}}); jobs.append(("sd",rid))
    out=[]
    for t,rid in jobs:
        if not rid: continue
        meta=_poll(t,rid); url=meta.get("url") or meta.get("location")
        rows=_download(url) if url else []
        for r in rows: r["adType"]=t.upper()
        out.extend(rows)
    if persist and out:
        con=_db(); cur=con.cursor()
        for r in out:
            cur.execute("INSERT OR REPLACE INTO metrics(adType,date,campaignId,campaignName,impressions,clicks,cost,purchases14d,sales14d,profileId) VALUES (?,?,?,?,?,?,?,?,?,?)",
                (r.get("adType"),str(r.get("date")),str(r.get("campaignId")),r.get("campaignName"),r.get("impressions",0),r.get("clicks",0),r.get("cost",0),r.get("purchases14d",0),r.get("sales14d",0),str(PROFILE_ID)))
        con.commit(); con.close()
    return out

def get_profiles():
    r=requests.get(f"{ADS_BASE}/v2/profiles",headers=_hdr(),timeout=60); 
    if r.status_code==401: _tok['val']=None; r=requests.get(f"{ADS_BASE}/v2/profiles",headers=_hdr(),timeout=60)
    r.raise_for_status(); return r.json()
