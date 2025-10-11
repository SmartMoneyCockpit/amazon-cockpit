"""
workers/ads_refresh_job.py
Run live Amazon Ads pulls (metrics, search_terms, placements) and write to SQLite.
Designed for Render "Scheduled Job" or "Background Worker".
"""
import os
from datetime import datetime, timedelta
from services.amazon_ads_service import (
    fetch_metrics, fetch_search_terms, fetch_placements, _init_db, _db
)

LOOKBACK_DAYS = int(os.getenv("ADS_LOOKBACK_DAYS", "30"))
AD_TYPES = os.getenv("ADS_TYPES", "SP,SB").split(",")  # SP=Sponsored Products, SB=Sponsored Brands

def main():
    _init_db()
    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=LOOKBACK_DAYS)
    start = start_date.strftime("%Y-%m-%d")
    end = end_date.strftime("%Y-%m-%d")

    results = {"metrics": 0, "search_terms": 0, "placements": 0}
    for ad in [a.strip().upper() for a in AD_TYPES if a.strip()]:
        try:
            m = fetch_metrics(ad, start, end) or []
            results["metrics"] += len(m)
        except Exception as e:
            print(f"[WARN] fetch_metrics {ad}: {e}")
        try:
            s = fetch_search_terms(ad, start, end) or []
            results["search_terms"] += len(s)
        except Exception as e:
            print(f"[WARN] fetch_search_terms {ad}: {e}")
        try:
            p = fetch_placements(ad, start, end) or []
            results["placements"] += len(p)
        except Exception as e:
            print(f"[WARN] fetch_placements {ad}: {e}")
    print({"ok": True, "window": [start, end], **results})

if __name__ == "__main__":
    main()
