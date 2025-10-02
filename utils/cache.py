
import time
from functools import wraps

def ttl_cache(ttl_seconds: int = 900):
    """Simple in-memory TTL cache decorator."""
    def decorator(fn):
        cache = {}
        @wraps(fn)
        def wrapper(*args, **kwargs):
            key = (args, tuple(sorted(kwargs.items())))
            now = time.time()
            if key in cache:
                val, exp = cache[key]
                if now < exp:
                    return val
            val = fn(*args, **kwargs)
            cache[key] = (val, now + ttl_seconds)
            return val
        return wrapper
    return decorator
