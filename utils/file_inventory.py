
from __future__ import annotations
import os, hashlib, pathlib, datetime as dt
from typing import Iterable, Dict, Any, List

DEFAULT_ROOTS = ["."]  # you can limit to specific dirs if desired

def _sha1(path: pathlib.Path, block_size: int = 65536) -> str:
    h = hashlib.sha1()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(block_size), b""):
            h.update(chunk)
    return h.hexdigest()

def iter_files(roots: Iterable[str] = DEFAULT_ROOTS) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for r in roots:
        base = pathlib.Path(r)
        if not base.exists():
            continue
        for p in base.rglob("*"):
            if p.is_file():
                try:
                    stat = p.stat()
                    out.append({
                        "path": p.as_posix(),
                        "size": stat.st_size,
                        "modified": dt.datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    })
                except Exception:
                    continue
    return out

def add_checksums(rows: List[Dict[str, Any]], max_bytes: int = 5_000_000) -> List[Dict[str, Any]]:
    # Add SHA-1 checksum to rows for files up to max_bytes (skip very large files by default).
    result: List[Dict[str, Any]] = []
    for r in rows:
        p = pathlib.Path(r["path"])
        sz = int(r.get("size") or 0)
        try:
            if sz <= max_bytes:
                r["sha1"] = _sha1(p)
            else:
                r["sha1"] = "(skipped)"
        except Exception:
            r["sha1"] = "(error)"
        result.append(r)
    return result
