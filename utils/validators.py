from __future__ import annotations
from typing import Iterable, Mapping, List, Dict, Any

class SchemaError(Exception):
    pass

def require_columns(rows: Iterable[Mapping[str, Any]], required: Iterable[str]) -> None:
    required = list(required)
    it = iter(rows)
    try:
        first = next(it)
    except StopIteration:
        # empty: still validate types by returning silently
        return
    missing = [c for c in required if c not in first.keys()]
    if missing:
        raise SchemaError(f"Missing column(s): {', '.join(missing)}")

def non_empty(rows: Iterable[Mapping[str, Any]], at_least: int = 1) -> None:
    count = 0
    for count, _ in enumerate(rows, 1):
        if count >= at_least:
            return
    if count < at_least:
        raise SchemaError(f"Expected at least {at_least} row(s), got {count}.")

def validate_settings_sheet(rows: List[Dict[str, Any]]) -> None:
    """Expect 'Settings' with 'key' and 'value' columns."""
    require_columns(rows, ["key", "value"])
