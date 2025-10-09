# pages/00_Health_patch_snippet.py
# Add this near the top of pages/00_Health.py after imports to display effective data dir
import os, pathlib
try:
    from services.amazon_ads_service_patch_dbdir import ensure_writable_dir
    _dir, _warn = ensure_writable_dir()
    st.info(f"Data directory in use: **{_dir}**")
    if _warn:
        st.warning(_warn)
except Exception as _e:
    st.caption(f"(Dir check skipped: {_e})")
