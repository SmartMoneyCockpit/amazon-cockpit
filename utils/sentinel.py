"""
Vega Sentinel — environment & directory checks.
"""
import os, sys
from typing import Dict, List

RECOMMENDED_DIRS = ["logs", "backups", "snapshots", "data", ".streamlit"]

def check_env(vars_list: List[str]) -> Dict[str, str]:
    status = {}
    for k in vars_list or []:
        v = os.getenv(k)
        status[k] = "SET" if v else "MISSING"
    return status

def check_dirs(dirs: List[str]=None) -> Dict[str, str]:
    dirs = dirs or RECOMMENDED_DIRS
    out = {}
    for d in dirs:
        try:
            if not os.path.exists(d):
                os.makedirs(d, exist_ok=True)
                out[d] = "CREATED"
            else:
                out[d] = "OK"
        except Exception as e:
            out[d] = f"ERROR: {e}"
    return out

def check_python() -> Dict[str,str]:
    return {"python_version": sys.version.split()[0]}
