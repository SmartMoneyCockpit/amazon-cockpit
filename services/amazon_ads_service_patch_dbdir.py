# services/amazon_ads_service_patch_dbdir.py
# Drop-in replacement or mix-in for v7: makes /data optional and falls back to /tmp/vega_data

import os, pathlib

def ensure_writable_dir():
    cand = os.getenv("VEGA_DATA_DIR", "/data")
    # Try candidate
    try:
        pathlib.Path(cand).mkdir(parents=True, exist_ok=True)
        test = pathlib.Path(cand) / ".write_test"
        with open(test, "wb") as f:
            f.write(b"ok")
        test.unlink(missing_ok=True)
        return cand, None
    except Exception as e:
        # Fallback to /tmp
        fallback = "/tmp/vega_data"
        pathlib.Path(fallback).mkdir(parents=True, exist_ok=True)
        return fallback, f"Permission denied on {cand}; using {fallback} (ephemeral). Set VEGA_DATA_DIR to a writable mounted disk."

# Usage in services/amazon_ads_service.py:
# replace:
#   DATA_DIR = os.getenv("VEGA_DATA_DIR", "/data")
#   pathlib.Path(DATA_DIR).mkdir(parents=True, exist_ok=True)
# with:
#   from services.amazon_ads_service_patch_dbdir import ensure_writable_dir
#   DATA_DIR, _VEGA_DIR_WARN = ensure_writable_dir()
#   if _VEGA_DIR_WARN: print(_VEGA_DIR_WARN)
