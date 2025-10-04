
from __future__ import annotations
import os, shutil, hashlib, datetime as dt
from pathlib import Path
from typing import Dict, List, Tuple

STAGING_ROOT = Path("restore_staging")
AUTO_BACKUP_ROOT = Path("auto_backups")

def list_staging_dirs() -> List[str]:
    if not STAGING_ROOT.exists():
        return []
    items = [p for p in STAGING_ROOT.iterdir() if p.is_dir() and p.name.startswith("restore_")]
    items.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return [p.as_posix() for p in items]

def _sha1(p: Path, block: int = 65536) -> str:
    h = hashlib.sha1()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(block), b""):
            h.update(chunk)
    return h.hexdigest()

def scan_diff(staging_dir: str, roots: List[str] | None = None) -> Dict[str, int]:
    """
    Compares files in staging vs live. Returns counters:
    {'new': X, 'updated': Y, 'same': Z, 'total_staging_files': N}
    roots: optional subpaths (e.g., ['pages','utils']) to restrict scan.
    """
    sd = Path(staging_dir)
    if not sd.exists():
        return {"new": 0, "updated": 0, "same": 0, "total_staging_files": 0}

    new = updated = same = total = 0
    for sp in sd.rglob("*"):
        if not sp.is_file():
            continue
        if roots:
            # restrict to given roots relative to staging root
            try:
                rel = sp.relative_to(sd)
            except Exception:
                continue
            if not any(str(rel).startswith(r + "/") or str(rel) == r for r in roots):
                continue

        total += 1
        rel_live = sp.relative_to(sd)
        live_path = Path(rel_live)
        if not live_path.exists():
            new += 1
        else:
            try:
                if live_path.stat().st_size != sp.stat().st_size:
                    updated += 1
                else:
                    # compare checksums if sizes equal
                    updated += int(_sha1(live_path) != _sha1(sp))
                    same     += int(_sha1(live_path) == _sha1(sp))
            except Exception:
                updated += 1
    return {"new": new, "updated": updated, "same": same, "total_staging_files": total}

def _ensure_parent(p: Path):
    p.parent.mkdir(parents=True, exist_ok=True)

def promote_to_live(staging_dir: str, roots: List[str] | None = None) -> Tuple[str, Dict[str, int]]:
    """
    Copies files from staging into live repo. Backs up overwritten files to auto_backups/<ts>/.
    Returns (backup_folder_path, counters).
    """
    sd = Path(staging_dir)
    assert sd.exists(), f"Staging dir not found: {staging_dir}"
    ts = dt.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    backup_dir = AUTO_BACKUP_ROOT / f"pre_promote_{ts}"
    backup_dir.mkdir(parents=True, exist_ok=True)

    counts = {"copied_new": 0, "copied_updated": 0, "skipped_same": 0}

    for sp in sd.rglob("*"):
        if not sp.is_file():
            continue
        rel = sp.relative_to(sd)
        # Respect roots filter
        if roots and not any(str(rel).startswith(r + "/") or str(rel) == r for r in roots):
            continue

        live_path = Path(rel)
        if live_path.exists():
            # backup existing
            backup_path = backup_dir / rel
            _ensure_parent(backup_path)
            shutil.copy2(live_path, backup_path)

        # ensure parent and copy
        _ensure_parent(live_path)
        if live_path.exists():
            # decide if updated or same
            try:
                same_size = live_path.stat().st_size == sp.stat().st_size
                same_hash = _sha1(live_path) == _sha1(sp) if same_size else False
                if same_hash:
                    counts["skipped_same"] += 1
                else:
                    shutil.copy2(sp, live_path)
                    counts["copied_updated"] += 1
            except Exception:
                shutil.copy2(sp, live_path)
                counts["copied_updated"] += 1
        else:
            shutil.copy2(sp, live_path)
            counts["copied_new"] += 1

    return (backup_dir.as_posix(), counts)
