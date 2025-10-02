from vega.infra.sheets_client import SheetsClient
from datetime import datetime
from typing import List, Dict, Any

def list_jobs() -> List[Dict[str, Any]]:
    sc = SheetsClient()
    return sc.read_table("Jobs")

def upsert_job(job_id: str, name: str, schedule_cron: str, status: str = "idle", notes: str = ""):
    sc = SheetsClient()
    rows = [{
        "job_id": job_id,
        "name": name,
        "schedule_cron": schedule_cron,
        "last_run": "",
        "status": status,
        "notes": notes
    }]
    sc.upsert_rows("Jobs", keys=["job_id"], rows=rows)

def mark_job_run(job_id: str, status: str = "success", notes: str = ""):
    sc = SheetsClient()
    rows = [{
        "job_id": job_id,
        "name": "",
        "schedule_cron": "",
        "last_run": datetime.utcnow().isoformat(),
        "status": status,
        "notes": notes
    }]
    sc.upsert_rows("Jobs", keys=["job_id"], rows=rows)