from __future__ import annotations
from typing import Iterable, Mapping, List

REQUIRED = ["date", "gmv", "acos", "tacos", "refund_rate"]

def missing_finance_columns(rows: Iterable[Mapping]) -> List[str]:
    """Return a list of required columns missing from the first row (case-insensitive).
    If rows is empty, assume all required columns are missing (signals empty/uncertain schema)."""
    it = iter(rows)
    try:
        first = next(it)
    except StopIteration:
        return REQUIRED[:]  # nothing to inspect
    # case-insensitive compare
    have = {str(k).strip().lower() for k in getattr(first, 'keys', lambda: first)()}
    return [c for c in REQUIRED if c not in have]
