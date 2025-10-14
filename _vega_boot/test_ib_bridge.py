#!/usr/bin/env python3
import os, httpx
base = os.getenv("IBKR_BRIDGE_URL","http://127.0.0.1:8088").rstrip("/")
headers = {}
api_key = os.getenv("IB_BRIDGE_API_KEY")
if api_key:
    headers["x-api-key"] = api_key
try:
    r = httpx.get(f"{base}/health", headers=headers, timeout=5.0)
    r.raise_for_status()
    print("Bridge OK:", r.json())
except Exception as e:
    print("Bridge NOT reachable:", e)