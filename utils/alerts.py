
from dataclasses import dataclass, asdict
from typing import List
import pandas as pd

@dataclass
class Alert:
    severity: str
    message: str
    source: str = "system"

def alerts_to_df(items: List['Alert']) -> pd.DataFrame:
    if not items:
        return pd.DataFrame(columns=["severity","message","source"])
    return pd.DataFrame([asdict(a) for a in items])
