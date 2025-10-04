from __future__ import annotations
import os, json, datetime as dt
from collections import defaultdict
from typing import List, Dict, Any

DIGEST_FILE = os.path.join("alerts", "digest_queue.jsonl")

def read_queue(path: str = DIGEST_FILE) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    if not os.path.exists(path):
        return rows
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except Exception:
                # ignore bad lines
                continue
    return rows

def _rule_name(r: Dict[str, Any]) -> str:
    if not isinstance(r, dict):
        return ""
    return r.get("name") or f"{r.get('metric')} {r.get('operator')} {r.get('threshold')}"

def group_by_date_and_rule(rows: List[Dict[str, Any]]) -> Dict[str, Dict[str, List[Dict[str, Any]]]]:
    grouped: Dict[str, Dict[str, List[Dict[str, Any]]]] = defaultdict(lambda: defaultdict(list))
    for r in rows:
        ts = r.get("ts") or ""
        try:
            d = dt.datetime.fromisoformat(ts.replace("Z","")).date().isoformat()
        except Exception:
            d = "unknown-date"
        name = _rule_name(r.get("rule", {}))
        grouped[d][name].append(r)
    return grouped

def build_markdown_summary(rows: List[Dict[str, Any]]) -> str:
    if not rows:
        return "No alerts queued yet. Use **Alerts Center → Evaluate Now** to add items."
    grouped = group_by_date_and_rule(rows)
    parts: List[str] = []
    for day in sorted(grouped.keys(), reverse=True):
        parts.append(f"### 📅 {day}")
        rules = grouped[day]
        for rule_name in sorted(rules.keys()):
            hits = rules[rule_name]
            parts.append(f"- **{rule_name}** — {len(hits)} hit(s)")
            for h in hits[:5]:  # cap details to keep summary compact
                reason = h.get("reason", "")
                parts.append(f"  - {reason}")
        parts.append("")  # blank line
    return "\n".join(parts).strip()

def build_plaintext_summary(rows: List[Dict[str, Any]]) -> str:
    md = build_markdown_summary(rows)
    # simple markdown-to-text (strip ** and ### bullets)
    txt = md.replace("**", "").replace("### ", "").replace("- ", "- ")
    return txt
