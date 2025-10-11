# services/ads_scheduler.py
import os, threading, time, traceback
from datetime import datetime, timedelta
from services.amazon_ads_service import (
    _init_db, fetch_metrics, fetch_search_terms, fetch_placements, quick_diag
)

FREQ_MIN = int(os.getenv("SCHEDULE_FREQUENCY_MIN", "60"))
LOOKBACK_DAYS = int(os.getenv("ADS_LOOKBACK_DAYS", "30"))
# Accept SP,SB,SD (any order, case-insensitive)
AD_TYPES = [t.strip().upper() for t in os.getenv("ADS_TYPES", "SP,SB,SD").split(",") if t.strip()]

_started = False

def _run_once():
    # Light diag to confirm profile & campaign visibility when AMZ_ADS_DEBUG=1
    try:
        quick_diag()
    except Exception:
        pass

    _init_db()
    end = datetime.utcnow().date()
    start = end - timedelta(days=LOOKBACK_DAYS)
    s, e = start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")

    inserted = {"metrics": 0, "search_terms": 0, "placements": 0}

    # Correct usage: pass the date window once, with which=AD_TYPES
    try:
        m = fetch_metrics(s, e, which=AD_TYPES) or []
        inserted["metrics"] += len(m)
    except Exception as ex:
        print(f"[scheduler] fetch_metrics error:", ex)

    try:
        srows = fetch_search_terms(s, e, which=AD_TYPES) or []
        inserted["search_terms"] += len(srows)
    except Exception as ex:
        print(f"[scheduler] fetch_search_terms error:", ex)

    try:
        prows = fetch_placements(s, e, which=AD_TYPES) or []
        inserted["placements"] += len(prows)
    except Exception as ex:
        print(f"[scheduler] fetch_placements error:", ex)

    print({'scheduler': True, 'ok': True, 'window': [s, e], **inserted})

def _loop():
    global _started
    if _started:
        return
    _started = True
    print(f"[scheduler] starting; freq={FREQ_MIN} min, lookback_days={LOOKBACK_DAYS}, types={AD_TYPES}")
    try:
        _run_once()
    except Exception:
        print("[scheduler] initial run failed:")
        traceback.print_exc()

    while True:
        try:
            print(f"[scheduler] heartbeat — next run in {FREQ_MIN} min")
            time.sleep(max(1, 60 * FREQ_MIN))
            _run_once()
        except Exception:
            print("[scheduler] loop error:")
            traceback.print_exc()

def start_scheduler():
    if os.getenv("ENABLE_SCHEDULER", "1").lower() in ("1","true","yes","on"):
        print("[scheduler] start_scheduler() called — launching thread")
        th = threading.Thread(target=_loop, name="ads_scheduler", daemon=True)
        th.start()
        return True
    print("[scheduler] disabled via ENABLE_SCHEDULER")
    return False
