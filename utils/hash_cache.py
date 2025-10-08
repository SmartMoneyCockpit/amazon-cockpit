"""
SHA-1 cache for backups/snapshots to speed up verification.
"""
import os, json, hashlib, time
CACHE_PATH = os.path.join("logs","sha1_cache.json")

def _load():
    try:
        return json.loads(open(CACHE_PATH,"r",encoding="utf-8").read())
    except Exception:
        return {}

def _save(obj):
    os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
    with open(CACHE_PATH,"w",encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False, indent=2))

def sha1(path: str) -> str:
    h = hashlib.sha1()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

def get_cached(path: str):
    cache = _load()
    return (cache.get(path,{}).get("sha1"), cache.get(path,{}).get("ts"))

def recompute_and_store(path: str):
    if not os.path.exists(path): 
        return {"status":"error","message":"not found"}
    s = sha1(path)
    cache = _load()
    cache[path] = {"sha1": s, "ts": int(time.time())}
    _save(cache)
    return {"status":"ok","sha1": s, "ts": cache[path]["ts"]}

def verify(path: str):
    if not os.path.exists(path): 
        return {"status":"error","message":"not found"}
    cache = _load()
    old = cache.get(path,{}).get("sha1")
    s = sha1(path)
    match = (old == s) if old else None
    return {"status":"ok","cached": old, "recomputed": s, "match": match}
