
from __future__ import annotations
import os, json, datetime as dt
from collections import defaultdict
from typing import List, Dict, Any
DIGEST_FILE = os.path.join("alerts", "digest_queue.jsonl")
def read_queue(path: str = DIGEST_FILE) -> List[Dict[str, Any]]:
    if not os.path.exists(path): return []
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line=line.strip()
            if not line: continue
            try: rows.append(json.loads(line))
            except Exception: continue
    return rows
def _rule_name(r: Dict[str, Any]) -> str:
    return (r or {}).get("name") or f"{(r or {}).get('metric')} {(r or {}).get('operator')} {(r or {}).get('threshold')}"
def build_markdown_summary(rows: List[Dict[str, Any]]) -> str:
    if not rows: return "No alerts queued yet. Use **Alerts Center → Evaluate Now** to add items."
    grouped=defaultdict(lambda: defaultdict(list))
    for r in rows:
        ts=r.get("ts") or ""
        try: d=dt.datetime.fromisoformat(ts.replace("Z","")).date().isoformat()
        except Exception: d="unknown-date"
        name=_rule_name(r.get("rule",{})) or r.get("metric","")
        grouped[d][name].append(r)
    parts=[]
    for day in sorted(grouped.keys(), reverse=True):
        parts.append(f"### 📅 {day}")
        for name,hits in grouped[day].items():
            parts.append(f"- **{name}** — {len(hits)} hit(s)")
            for h in hits[:5]:
                reason=h.get("reason",""); parts.append(f"  - {reason}")
        parts.append("")
    return "\n".join(parts).strip()
def build_plaintext_summary(rows: List[Dict[str, Any]]) -> str:
    return build_markdown_summary(rows).replace("**","").replace("### ","")
