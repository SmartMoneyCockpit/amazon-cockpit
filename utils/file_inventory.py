
from __future__ import annotations
import hashlib, pathlib, datetime as dt
from typing import Iterable, Dict, Any, List
def _sha1(p: pathlib.Path, block_size=65536)->str:
    h=hashlib.sha1()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(block_size), b""):
            h.update(chunk)
    return h.hexdigest()
def iter_files(roots: Iterable[str]):
    out=[]
    for r in roots:
        base=pathlib.Path(r)
        if not base.exists(): continue
        for p in base.rglob("*"):
            if p.is_file():
                try:
                    stat=p.stat()
                    out.append({"path": p.as_posix(), "size": stat.st_size, "modified": dt.datetime.fromtimestamp(stat.st_mtime).isoformat()})
                except Exception: continue
    return out
def add_checksums(rows: List[Dict[str,Any]], max_bytes=5_000_000):
    res=[]
    for r in rows:
        p=pathlib.Path(r["path"]); sz=int(r.get("size") or 0)
        try:
            r["sha1"] = _sha1(p) if sz<=max_bytes else "(skipped)"
        except Exception:
            r["sha1"] = "(error)"
        res.append(r)
    return res
