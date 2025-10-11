from typing import Iterable
def normalize_origins(raw: str | Iterable[str] | None):
    if raw is None:
        return []
    if isinstance(raw, str):
        parts = [p.strip() for p in raw.split(",")]
    else:
        parts = [str(p).strip() for p in raw]
    return [p for p in parts if p]
