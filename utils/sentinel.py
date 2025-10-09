# utils/sentinel.py
# Enhanced to accept optional custom_env for extra environment summaries.

import os, pathlib, tempfile

def run_all(custom_env=None):
    custom_env = custom_env or {}

    def _write_test(dirpath: str):
        try:
            p = pathlib.Path(dirpath)
            p.mkdir(parents=True, exist_ok=True)
            test = p / ".write_test"
            with open(test, "wb") as f:
                f.write(b"ok")
            try:
                test.unlink()
            except Exception:
                pass
            return "write_ok"
        except Exception as e:
            return f"err: {e}"

    def _env_flag(*keys):
        for k in keys:
            if os.getenv(k):
                return "set"
        return "missing"

    def _sheets_status():
        doc = os.getenv("SHEETS_DOC_ID")
        creds = os.getenv("SHEETS_CREDENTIALS_JSON") or os.getenv("SHEETS_CREDENTIALS_FILE")
        if doc and creds:
            return {"status": "ok", "message": "configured"}
        elif doc or creds:
            return {"status": "warn", "message": "partial: missing one of SHEETS_DOC_ID or credentials"}
        else:
            return {"status": "warn", "message": "Sheets not configured: SHEETS_DOC_ID not set"}

    data_root = os.getenv("VEGA_DATA_DIR", "/data")
    if not os.path.exists(data_root):
        data_root = os.path.join(tempfile.gettempdir(), "vega_data")

    fs = {
        "snapshots": _write_test(os.path.join(data_root, "snapshots")),
        "alerts":    _write_test(os.path.join(data_root, "alerts")),
        "cache":     _write_test(os.path.join(data_root, "cache")),
        "logs":      _write_test(os.path.join(data_root, "logs")),
    }

    env_summary = {
        "SHEETS_KEY": _env_flag("SHEETS_DOC_ID"),
        "GCP_SERVICE_ACCOUNT_JSON": _env_flag("SHEETS_CREDENTIALS_JSON"),
        "GOOGLE_APPLICATION_CREDENTIALS": _env_flag("GOOGLE_APPLICATION_CREDENTIALS"),
        "SENDGRID_API_KEY": _env_flag("SENDGRID_API_KEY"),
        "EMAIL_FROM": _env_flag("VEGA_EMAIL_FROM", "EMAIL_FROM"),
        "EMAIL_TO": _env_flag("VEGA_EMAIL_TO", "EMAIL_TO"),
    }

    # extra env checks passed by the page
    for label, keys in custom_env.items():
        if isinstance(keys, (list, tuple)):
            env_summary[label] = _env_flag(*keys)
        else:
            env_summary[label] = _env_flag(keys)

    return {
        "google_sheets": _sheets_status(),
        "filesystem": fs,
        "env": env_summary,
    }
