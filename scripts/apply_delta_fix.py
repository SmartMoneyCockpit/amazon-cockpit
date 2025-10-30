#!/usr/bin/env python3
import re, sys, os, hashlib, datetime

APP_FILE = "app.py"

def hash_text(t):
    return hashlib.sha256(t.encode("utf-8")).hexdigest()

def main():
    path = APP_FILE
    if not os.path.exists(path):
        print(f"[ERROR] {path} not found. Run this from the repo root (same folder as app.py).")
        sys.exit(1)

    src = open(path, "r", encoding="utf-8").read()
    before_hash = hash_text(src)

    # Replace any st.dataframe(..., width="stretch") with use_container_width=True
    # Covers cases with spaces and different argument orders.
    pattern = r'(st\.dataframe\([^)]*?)\bwidth\s*=\s*["\']stretch["\']'
    repl    = r'\1use_container_width=True'
    dst, n = re.subn(pattern, src, flags=re.DOTALL)

    if n == 0:
        print("[INFO] No occurrences of width=\"stretch\" found in st.dataframe calls.")
        print("       Nothing changed. If the error persists, search your code base for: width=\"stretch\"")
        sys.exit(0)

    # Also ensure we don't end up with duplicated args if both width and use_container_width existed
    # (rare) — remove trailing ', ,'
    dst = re.sub(r',\s*,', ',', dst)

    open(path, "w", encoding="utf-8").write(dst)
    after_hash = hash_text(dst)

    print(f"[OK] Patched {path}.")
    print(f"     Replacements made: {n}")
    print(f"     Before: {before_hash}")
    print(f"     After : {after_hash}")
    print(f"     Time  : {datetime.datetime.now().isoformat()}")

if __name__ == "__main__":
    main()
