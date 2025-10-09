# v7.2 — DB Directory Fallback (one-and-done)

This patch fixes `PermissionError: [Errno 13] Permission denied: '/data'` by
selecting a writable directory automatically. If `/data` isn't mounted,
it falls back to `/tmp/vega_data` (ephemeral).

## Apply
1) Replace your `services/amazon_ads_service.py` with the file in this zip.
2) Add `services/amazon_ads_service_patch_dbdir.py` (keep same path).
3) Replace `pages/00_Health.py` (optional; shows which dir is active).
4) Redeploy.

## Persistence
- For permanent storage, mount a **Persistent Disk** at `/data` in Render, or set `VEGA_DATA_DIR` to another writable mount.
- Without a disk, data in `/tmp/vega_data` is cleared on restart.

## Optional env
```
VEGA_DATA_DIR=/data               # preferred (with a disk)
# or
VEGA_DATA_DIR=/tmp/vega_data      # quick workaround
```
