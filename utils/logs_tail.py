"""
Tiny helper to tail logs/vega_jobs.jsonl safely.
"""
from __future__ import annotations
import os, itertools
from typing import List

LOG_FILE = os.path.join("logs","vega_jobs.jsonl")

def tail_jsonl(n: int = 50, path: str = LOG_FILE) -> List[str]:
    if not os.path.exists(path):
        return []
    # Simple safe read (for small files). For large files, this can be improved.
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    return [l.rstrip("\n") for l in lines[-n:]]
