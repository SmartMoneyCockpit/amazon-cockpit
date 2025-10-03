
from __future__ import annotations
import os, json, time, traceback, typing as t

LOG_PATH = os.getenv("COCKPIT_ERROR_LOG", "/tmp/cockpit_errors.jsonl")

def _now_ts() -> float:
    return time.time()

def _safe_serialize(obj):
    try:
        json.dumps(obj)
        return obj
    except Exception:
        return str(obj)

def log_error(context: str, err: Exception, extra: dict | None = None) -> None:
    rec = {
        "ts": _now_ts(),
        "context": context,
        "type": type(err).__name__,
        "message": str(err),
        "trace": traceback.format_exc(),
        "extra": _safe_serialize(extra or {}),
    }
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec) + "\n")
    except Exception:
        pass

def try_or_log(fn: t.Callable, context: str, *args, **kwargs):
    try:
        res = fn(*args, **kwargs)
        return True, res
    except Exception as e:
        log_error(context, e, {"args": args, "kwargs": kwargs})
        return False, f"{type(e).__name__}: {e}"

def wrap_streamlit_call(context: str):
    import functools
    def deco(func):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                try:
                    import streamlit as st
                    st.error(f"Something went wrong in {context}. Check logs.")
                except Exception:
                    pass
                log_error(context, e, {"args": args, "kwargs": kwargs})
                return None
        return inner
    return deco

def last_errors(n: int = 50) -> list[dict]:
    if not os.path.exists(LOG_PATH):
        return []
    try:
        with open(LOG_PATH, "r", encoding="utf-8") as f:
            lines = f.readlines()[-n:]
        return [json.loads(x) for x in lines if x.strip()]
    except Exception:
        return []
