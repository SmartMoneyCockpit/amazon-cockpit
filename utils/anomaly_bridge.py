
from __future__ import annotations
import os, json, datetime as dt
from typing import Dict, Any
from utils.logs import log_job

DIGEST_PATH = os.path.join("alerts", "digest_queue.jsonl")

def append_anomalies_to_digest(flags: Dict[str, bool], z_thresh: float = 2.0) -> str:
    """Append active anomaly flags to digest queue. Returns path written."""
    if not flags:
        return DIGEST_PATH

    os.makedirs(os.path.dirname(DIGEST_PATH), exist_ok=True)
    ts = dt.datetime.utcnow().isoformat() + "Z"

    count = 0
    with open(DIGEST_PATH, "a", encoding="utf-8") as f:
        for metric, active in flags.items():
            if active:
                rec = {
                    "type": "finance_anomaly",
                    "metric": metric,
                    "reason": f"{metric.upper()} anomaly (|z| ≥ {z_thresh}) @ {dt.date.today().isoformat()}",
                    "ts": ts,
                }
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                count += 1

    if count > 0:
        log_job("finance_anomaly_bridge", "ok", f"Queued {count} anomalies to digest")
    else:
        log_job("finance_anomaly_bridge", "ok", "No active anomalies to queue")

    return DIGEST_PATH
