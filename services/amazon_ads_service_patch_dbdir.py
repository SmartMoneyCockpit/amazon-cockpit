# services/amazon_ads_service_patch_dbdir.py
# Provides a safe, writable DATA_DIR even when /data isn't mounted.
import os, pathlib, tempfile

def ensure_writable_dir():
    cand = os.getenv("VEGA_DATA_DIR", "/data")
    try:
        p = pathlib.Path(cand)
        p.mkdir(parents=True, exist_ok=True)
        test = p / ".write_test"
        with open(test, "wb") as f:
            f.write(b"ok")
        try:
            test.unlink()
        except Exception:
            pass
        return str(p), None
    except Exception as e:
        # Fallback to /tmp (ephemeral)
        fallback = pathlib.Path(tempfile.gettempdir()) / "vega_data"
        fallback.mkdir(parents=True, exist_ok=True)
        warn = f"Permission denied on {cand}; using {fallback} (ephemeral). Add a Persistent Disk at /data or set VEGA_DATA_DIR."
        return str(fallback), warn
