"""
Vega Sentinel — backend health checks (env, folders, optional deps).
Safe to import anywhere; no hard external deps.
"""
import os
import sys
from typing import Dict, List, Tuple

REQUIRED_ENV = [
    # Optional by default; mark critical when truly required for your deployment
    # "SENDGRID_API_KEY", "EMAIL_FROM", "EMAIL_TO",
    # "SHEETS_KEY",
]

RECOMMENDED_DIRS = ["backups", "snapshots", "data", ".streamlit"]

def check_env(vars_list: List[str]=None) -> Dict[str, str]:
    vars_list = vars_list or REQUIRED_ENV
    status = {}
    for k in vars_list:
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

def check_python() -> Dict[str, str]:
    return {
        "python_version": sys.version.split()[0],
        "executable": sys.executable or "unknown",
    }

def run_all(custom_env: List[str]=None, custom_dirs: List[str]=None) -> Dict[str, Dict[str,str]]:
    return {
        "python": check_python(),
        "env": check_env(custom_env),
        "dirs": check_dirs(custom_dirs),
    }
