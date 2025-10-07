"""
Simple exporters for CSV / MD / TXT strings from in-memory data.
"""
from typing import List, Dict
import csv
import io

def to_csv(rows: List[Dict[str,object]]) -> bytes:
    if not rows: return b""
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)
    return buf.getvalue().encode("utf-8")

def to_md_table(rows: List[Dict[str,object]]) -> str:
    if not rows: return ""
    headers = list(rows[0].keys())
    line1 = "| " + " | ".join(headers) + " |"
    line2 = "| " + " | ".join(["---"]*len(headers)) + " |"
    body = ["| " + " | ".join(str(r.get(h,'')) for h in headers) + " |" for r in rows]
    return "\n".join([line1, line2] + body)

def to_txt(rows: List[Dict[str,object]]) -> str:
    if not rows: return ""
    lines=[] 
    for r in rows:
        lines.append(" ; ".join(f"{k}={r.get(k,'')}" for k in r.keys()))
    return "\n".join(lines)
