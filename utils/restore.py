
from __future__ import annotations
import os, zipfile, pathlib, datetime as dt
from typing import List, Dict, Any
def list_zip_contents(zip_path: str, max_items: int=200)->List[str]:
    out=[]; 
    if not os.path.exists(zip_path): return out
    with zipfile.ZipFile(zip_path,"r") as z:
        for n in z.namelist()[:max_items]: out.append(n)
    return out
def restore_to_staging(zip_path: str, staging_root: str="restore_staging")->str:
    ts=dt.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    target=pathlib.Path(staging_root)/f"restore_{ts}"; target.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path,"r") as z: z.extractall(target.as_posix())
    return target.as_posix()
def tree_preview(path: str, max_entries: int=500)->List[Dict[str,Any]]:
    base=pathlib.Path(path); out=[]; 
    if not base.exists(): return out
    count=0
    for p in base.rglob("*"):
        if p.is_file():
            try: rel=p.relative_to(base).as_posix(); size=p.stat().st_size
            except Exception: continue
            out.append({"path": rel, "size": size}); count+=1
            if count>=max_entries: break
    return out
