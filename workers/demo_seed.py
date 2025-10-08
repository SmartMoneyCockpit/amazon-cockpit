"""
Create minimal demo artifacts: snapshot CSV, digest files, and jobs log entries.
"""
import os, time, json, csv
from typing import List

def _ensure(d): os.makedirs(d, exist_ok=True)

def main() -> List[str]:
    created = []
    _ensure("snapshots"); _ensure("backups"); _ensure("logs")
    ts = time.strftime("%Y%m%d_%H%M%S")
    # snapshot
    snap = os.path.join("snapshots", f"snapshot_{ts}.csv")
    with open(snap, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f); w.writerow(["section","key","value"]); w.writerow(["demo","hello","world"])
    created.append(snap)
    # digest artifacts
    for ext, body in [("csv","a,b\n1,2\n"), ("md","# Demo Digest\n- ok\n"), ("txt","demo digest\n")]:
        p = os.path.join("backups", f"digest_{ts}.{ext}")
        with open(p, "w", encoding="utf-8") as f: f.write(body)
        created.append(p)
    # jobs log entries
    jl = os.path.join("logs","vega_jobs.jsonl")
    for job, status in [("snapshot_heartbeat","ok"), ("digest_run","ok"), ("alerts_flush","no_change")]:
        rec = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S")+"Z", "job": job, "status": status, "details": {}}
        with open(jl, "a", encoding="utf-8") as f: f.write(json.dumps(rec, ensure_ascii=False)+"\n")
    return created
