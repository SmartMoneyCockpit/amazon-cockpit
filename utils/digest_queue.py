from __future__ import annotations
import os, json, time
QUEUE_DIR = os.path.join("data", "digest_queue")
os.makedirs(QUEUE_DIR, exist_ok=True)

def add_summary(module: str, title: str, rows: list[dict]) -> str:
    ts = time.strftime("%Y%m%d_%H%M%S")
    path = os.path.join(QUEUE_DIR, f"{module}_{ts}.json")
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"module": module, "title": title, "rows": rows, "ts": ts}, f, ensure_ascii=False, indent=2)
        return path
    except Exception as e:
        return ""

def list_summaries(limit: int = 20) -> list[dict]:
    try:
        files = [os.path.join(QUEUE_DIR, f) for f in os.listdir(QUEUE_DIR) if f.endswith(".json")]
        files.sort(key=lambda p: os.path.getmtime(p), reverse=True)
        out = []
        for p in files[:limit]:
            try:
                out.append(json.load(open(p, "r", encoding="utf-8")))
            except Exception:
                continue
        return out
    except Exception:
        return []
