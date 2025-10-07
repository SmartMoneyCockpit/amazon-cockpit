"""
Validate jobs YAML in tools/*.yaml for minimal schema sanity.
Avoids runtime surprises when loading job definitions.
"""
import os, glob, yaml
from typing import Dict, Any, List

MIN_FIELDS = {"name", "schedule", "task"}

def list_job_files(tools_dir: str="tools") -> List[str]:
    return sorted(glob.glob(os.path.join(tools_dir, "*.yaml")))

def validate_job_file(path: str) -> Dict[str, Any]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
    except Exception as e:
        return {"file": path, "ok": False, "error": f"read_error: {e}"}

    if isinstance(data, list):
        items = data
    else:
        items = [data]

    problems = []
    for i, item in enumerate(items):
        if not isinstance(item, dict):
            problems.append(f"item[{i}] is not a dict")
            continue
        missing = MIN_FIELDS - set(item.keys())
        if missing:
            problems.append(f"item[{i}] missing fields: {sorted(list(missing))}")
    return {
        "file": path,
        "ok": not problems,
        "problems": problems,
        "items_count": len(items),
    }

def validate_all(tools_dir: str="tools") -> List[Dict[str, Any]]:
    results = []
    for f in list_job_files(tools_dir):
        results.append(validate_job_file(f))
    return results
