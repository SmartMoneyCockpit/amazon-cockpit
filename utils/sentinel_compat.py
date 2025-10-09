# utils/sentinel_compat.py
# Provides safe_run_all() that calls utils.sentinel.run_all with or without kwargs.

from utils import sentinel

def safe_run_all(custom_env=None):
    try:
        return sentinel.run_all(custom_env=custom_env)
    except TypeError:
        # Older sentinel signature without kwargs; call without them
        return sentinel.run_all()
