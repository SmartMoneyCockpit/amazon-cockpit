from __future__ import annotations
import os, yaml
DEFAULTS = {
    'dev_tools_link_enabled': True,
    'alerts_auto_refresh_default_secs': 0,
    'digest_attachments_default': False,
}
CFG_DIR = 'config'
CFG_PATH = os.path.join(CFG_DIR, 'feature_flags.yaml')
def load_flags() -> dict:
    try:
        if os.path.exists(CFG_PATH):
            with open(CFG_PATH, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f) or {}
        else:
            data = {}
        out = DEFAULTS.copy()
        out.update({k:v for k,v in (data or {}).items() if k in DEFAULTS})
        return out
    except Exception:
        return DEFAULTS.copy()
