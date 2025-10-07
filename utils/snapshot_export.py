"""
Snapshot helpers for saving CSV/Markdown/text outputs into snapshots/ folder.
"""
import os, io, csv, time
from typing import List, Dict

SNAPDIR = "snapshots"

def _ensure_dir(d=SNAPDIR):
    if not os.path.exists(d):
        os.makedirs(d, exist_ok=True)

def save_csv(rows: List[Dict[str,object]], name_prefix="snapshot") -> str:
    _ensure_dir()
    ts = time.strftime("%Y%m%d_%H%M%S")
    path = os.path.join(SNAPDIR, f"{name_prefix}_{ts}.csv")
    if not rows:
        open(path, "w", encoding="utf-8").close()
        return path
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    return path

def save_md_table(rows: List[Dict[str,object]], name_prefix="snapshot") -> str:
    _ensure_dir()
    ts = time.strftime("%Y%m%d_%H%M%S")
    path = os.path.join(SNAPDIR, f"{name_prefix}_{ts}.md")
    if not rows:
        open(path, "w", encoding="utf-8").close()
        return path
    headers = list(rows[0].keys())
    line1 = "| " + " | ".join(headers) + " |"
    line2 = "| " + " | ".join(["---"]*len(headers)) + " |"
    body = ["| " + " | ".join(str(r.get(h,'')) for h in headers) + " |" for r in rows]
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join([line1, line2] + body))
    return path

def save_txt(rows: List[Dict[str,object]], name_prefix="snapshot") -> str:
    _ensure_dir()
    ts = time.strftime("%Y%m%d_%H%M%S")
    path = os.path.join(SNAPDIR, f"{name_prefix}_{ts}.txt")
    with open(path, "w", encoding="utf-8") as f:
        for r in rows or []:
            f.write(" ; ".join(f"{k}={r.get(k,'')}" for k in r.keys()) + "\n")
    return path
