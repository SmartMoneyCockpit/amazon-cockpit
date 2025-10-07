
from __future__ import annotations
import os, shutil, hashlib, datetime as dt
from pathlib import Path
STAGING_ROOT=Path("restore_staging"); AUTO_BACKUP_ROOT=Path("auto_backups")
def list_staging_dirs():
    if not STAGING_ROOT.exists(): return []
    items=[p for p in STAGING_ROOT.iterdir() if p.is_dir() and p.name.startswith("restore_")]
    items.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return [p.as_posix() for p in items]
def _sha1(p: Path, block=65536):
    import hashlib
    h=hashlib.sha1()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(block), b""): h.update(chunk)
    return h.hexdigest()
def scan_diff(staging_dir, roots=None):
    sd=Path(staging_dir); new=updated=same=total=0
    if not sd.exists(): return {"new":0,"updated":0,"same":0,"total_staging_files":0}
    for sp in sd.rglob("*"):
        if not sp.is_file(): continue
        if roots:
            rel=sp.relative_to(sd)
            if not any(str(rel).startswith(r + "/") or str(rel)==r for r in roots): continue
        total+=1; rel_live=sp.relative_to(sd); live=Path(rel_live)
        if not live.exists(): new+=1
        else:
            try:
                if live.stat().st_size != sp.stat().st_size: updated+=1
                else: 
                    updated += int(_sha1(live)!=_sha1(sp)); same += int(_sha1(live)==_sha1(sp))
            except Exception: updated+=1
    return {"new":new,"updated":updated,"same":same,"total_staging_files":total}
def _ensure_parent(p: Path): p.parent.mkdir(parents=True, exist_ok=True)
def promote_to_live(staging_dir, roots=None):
    sd=Path(staging_dir); assert sd.exists(), f"Staging not found: {staging_dir}"
    ts=dt.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ"); backup_dir=AUTO_BACKUP_ROOT/f"pre_promote_{ts}"; backup_dir.mkdir(parents=True, exist_ok=True)
    counts={"copied_new":0,"copied_updated":0,"skipped_same":0}
    for sp in sd.rglob("*"):
        if not sp.is_file(): continue
        rel=sp.relative_to(sd)
        if roots and not any(str(rel).startswith(r + "/") or str(rel)==r for r in roots): continue
        live=Path(rel)
        if live.exists():
            backup=backup_dir/rel; _ensure_parent(backup); shutil.copy2(live, backup)
        _ensure_parent(live)
        if live.exists():
            try:
                same=(live.stat().st_size==sp.stat().st_size) and (_sha1(live)==_sha1(sp))
                if same: counts["skipped_same"]+=1
                else: shutil.copy2(sp, live); counts["copied_updated"]+=1
            except Exception: shutil.copy2(sp, live); counts["copied_updated"]+=1
        else:
            shutil.copy2(sp, live); counts["copied_new"]+=1
    return (backup_dir.as_posix(), counts)
