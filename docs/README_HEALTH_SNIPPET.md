# v7.2 — Health Patch Snippet (fixed)

This bundle gives you:
- `pages/Health_Patch_Snippet.py` — the minimal snippet with the correct `import streamlit as st`.
- `pages/00_Health.py` — fully patched Health page (optional drop‑in).
- `services/amazon_ads_service_patch_dbdir.py` — helper used by the snippet to ensure a writable data directory.

## How to use
1. Copy **pages/Health_Patch_Snippet.py** into your repo (or replace your existing snippet page).
2. If you want the full Health page patched, replace **pages/00_Health.py** with the file here.
3. Ensure **services/amazon_ads_service_patch_dbdir.py** exists (provided here).
4. Deploy and open the snippet/Health page — no NameError, and you should see the active data directory.
