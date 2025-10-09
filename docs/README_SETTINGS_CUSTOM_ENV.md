# v7.4.2 — Settings & Controls custom_env patch

This patch eliminates the error: `run_all() got an unexpected keyword argument 'custom_env'`.

## What's included
- `utils/sentinel.py` — updated to accept `custom_env` (backward compatible).
- `utils/sentinel_compat.py` — `safe_run_all(custom_env=None)` wrapper (works even if a stale sentinel is imported).
- `pages/44_Settings_Controls_patch.py` — optional demo page using the wrapper.

## How to apply
1. Replace your **`utils/sentinel.py`** with the one in this zip.
2. Add **`utils/sentinel_compat.py`**.
3. (Optional) If you want to switch your page to the wrapper, change the import to:
   ```python
   from utils.sentinel_compat import safe_run_all as run_all
   ```
   or call `safe_run_all(custom_env=...)` directly.
4. Rebuild/Deploy (clear build cache if needed).

If the page still shows the error, the running app is importing an older sentinel from another path.
Point your page to the wrapper as in step 3 and it will work regardless.
