"""
Lightweight logging setup to file logs/app.log (rotates on deploy).
"""
import os, logging
from logging.handlers import RotatingFileHandler

def init_logging():
    try:
        os.makedirs("logs", exist_ok=True)
        handler = RotatingFileHandler("logs/app.log", maxBytes=2_000_000, backupCount=2, encoding="utf-8")
        fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
        handler.setFormatter(fmt)
        root = logging.getLogger()
        root.setLevel(logging.INFO)
        if not any(isinstance(h, RotatingFileHandler) for h in root.handlers):
            root.addHandler(handler)
        logging.getLogger(__name__).info("Logging initialized")
    except Exception as e:
        # Fail-soft; never break the app
        print(f"[logging_setup] init failed: {e}")
