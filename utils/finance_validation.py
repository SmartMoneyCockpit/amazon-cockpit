
from __future__ import annotations
from typing import Iterable, Mapping, List
REQUIRED=["date","gmv","acos","tacos","refund_rate"]
def missing_finance_columns(rows: Iterable[Mapping]) -> List[str]:
    it=iter(rows)
    try: first=next(it)
    except StopIteration: return REQUIRED[:]
    have={str(k).strip().lower() for k in getattr(first,'keys',lambda: first)()}
    return [c for c in REQUIRED if c not in have]
