# Auto-added by Vega bootstrap: ensure project root and /src are importable.
import sys, pathlib, os
HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE
SRC  = ROOT / "src"
for p in (ROOT, SRC):
    if p.exists() and str(p) not in sys.path:
        sys.path.insert(0, str(p))