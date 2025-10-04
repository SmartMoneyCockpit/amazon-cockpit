from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional
import os, json, pathlib, math
import pandas as pd

CACHE_DIR = pathlib.Path(".cache")
CACHE_DIR.mkdir(exist_ok=True, parents=True)
RULES_JSON = CACHE_DIR / "alerts_rules.json"

@dataclass
class Rule:
    metric: str              # one of: gmv, acos, tacos, refund_rate
    operator: str            # >, <, >=, <=, crosses_above, crosses_below
    threshold: float         # numeric threshold; for crosses_* we compare last vs prev
    lookback_days: int = 7
    action: str = "Digest"   # only "Digest" supported for now
    name: str = ""           # optional label

    def evaluate(self, df: pd.DataFrame) -> (bool, str):
        if df is None or df.empty or self.metric not in df.columns:
            return False, "No data available for metric"
        series = df[self.metric].dropna()
        if series.empty:
            return False, "Series empty"

        # restrict lookback
        series = series.tail(max(2, self.lookback_days))
        last = series.iloc[-1]
        prev = series.iloc[-2] if len(series) >= 2 else None

        op = self.operator
        thr = float(self.threshold)

        def crosses_above(prev_v, last_v, thr_v):
            return prev_v is not None and prev_v <= thr_v and last_v > thr_v

        def crosses_below(prev_v, last_v, thr_v):
            return prev_v is not None and prev_v >= thr_v and last_v < thr_v

        passed = False
        if op == ">":
            passed = last > thr
        elif op == "<":
            passed = last < thr
        elif op == ">=":
            passed = last >= thr
        elif op == "<=":
            passed = last <= thr
        elif op == "crosses_above":
            passed = crosses_above(prev, last, thr)
        elif op == "crosses_below":
            passed = crosses_below(prev, last, thr)
        else:
            return False, f"Unsupported operator: {op}"

        reason = f"{self.metric}({last:.4f}) {op} {thr:.4f} over {len(series)} samples"
        return passed, reason

def load_rules() -> List[Rule]:
    if RULES_JSON.exists():
        try:
            data = json.loads(RULES_JSON.read_text())
            return [Rule(**r) for r in data]
        except Exception:
            return []
    return []

def save_rules(rules: List[Rule]) -> None:
    RULES_JSON.write_text(json.dumps([asdict(r) for r in rules], indent=2))

def add_rule(rule: Rule) -> None:
    rules = load_rules()
    rules.append(rule)
    save_rules(rules)

def remove_rule(idx: int) -> None:
    rules = load_rules()
    if 0 <= idx < len(rules):
        rules.pop(idx)
        save_rules(rules)
