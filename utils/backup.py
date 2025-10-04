from __future__ import annotations
import os, io, zipfile, pathlib, datetime as dt
from typing import List, Tuple, Optional

DEFAULT_INCLUDE = [
    "pages", "modules", "components", "utils", "tools",
    "app.py", "infra", ".streamlit/secrets.toml", "render.yaml"
]
BACKUP_DIR = "backups"

def _iter_paths(include: List[str]) -> List[pathlib.Path]:
    paths: List[pathlib.Path] = []
    for p in include:
        path = pathlib.Path(p)
        if path.exists():
            paths.append(path)
    return paths

def create_backup(include: Optional[List[str]] = None, out_dir: str = BACKUP_DIR) -> str:
    include = include or DEFAULT_INCLUDE
    ts = dt.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    out_base = pathlib.Path(out_dir)
    out_base.mkdir(parents=True, exist_ok=True)
    zip_path = out_base / f"vega_backup_{ts}.zip"

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for path in _iter_paths(include):
            if path.is_dir():
                for subroot, _, files in os.walk(path):
                    for f in files:
                        abs_path = pathlib.Path(subroot) / f
                        arc = abs_path.as_posix()
                        z.write(abs_path, arc)
            else:
                z.write(path, path.as_posix())
    return str(zip_path)

def list_backups(out_dir: str = BACKUP_DIR) -> List[str]:
    base = pathlib.Path(out_dir)
    if not base.exists():
        return []
    zips = sorted([p.as_posix() for p in base.glob("vega_backup_*.zip")], reverse=True)
    return zips

def latest_backup(out_dir: str = BACKUP_DIR) -> Optional[str]:
    zips = list_backups(out_dir)
    return zips[0] if zips else None
