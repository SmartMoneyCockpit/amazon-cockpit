
import json
import os
from typing import List, Dict, Any, Optional, Tuple
import gspread

SHEET_URL = os.getenv("GOOGLE_SHEET_URL")

def _auth():
    # Prefer JSON content in env; fall back to secret file path
    creds_json = os.getenv("GCP_SERVICE_ACCOUNT_JSON")
    creds_file = os.getenv("GCP_SERVICE_ACCOUNT_JSON_FILE") or os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if creds_json:
        try:
            creds = json.loads(creds_json)
        except Exception as e:
            raise RuntimeError(f"GCP_SERVICE_ACCOUNT_JSON is set but not valid JSON: {e}")
        gc = gspread.service_account_from_dict(creds)
        return gc
    if creds_file and os.path.exists(creds_file):
        return gspread.service_account(filename=creds_file)
    raise RuntimeError("GCP_SERVICE_ACCOUNT_JSON is not set. Set GCP_SERVICE_ACCOUNT_JSON (JSON content) "
                       "or GCP_SERVICE_ACCOUNT_JSON_FILE/GOOGLE_APPLICATION_CREDENTIALS (path to JSON file).")

def _col_letter(n: int) -> str:
    result = ""
    while n > 0:
        n, rem = divmod(n - 1, 26)
        result = chr(65 + rem) + result
    return result

class SheetsClient:
    def __init__(self, sheet_url: Optional[str] = None):
        self.gc = _auth()
        self.sheet_url = sheet_url or SHEET_URL
        if not self.sheet_url:
            raise RuntimeError("GOOGLE_SHEET_URL is not set.")
        self.sh = self.gc.open_by_url(self.sheet_url)

    def read_table(self, tab: str) -> List[Dict[str, Any]]:
        ws = self.sh.worksheet(tab)
        return ws.get_all_records()

    def upsert_rows(self, tab: str, keys: List[str], rows: List[Dict[str, Any]]):
        ws = self.sh.worksheet(tab)
        header = ws.row_values(1)
        if not header:
            raise RuntimeError(f"Worksheet '{tab}' is missing a header row.")
        existing = ws.get_all_records()
        def keyof(r: Dict[str, Any]):
            return tuple(str(r.get(k, "")) for k in keys)
        index = { keyof(r): i+2 for i, r in enumerate(existing) }
        last_col_letter = _col_letter(len(header))
        for r in rows:
            k = keyof(r)
            row_values = [r.get(col, "") for col in header]
            if k in index:
                row_num = index[k]
                rng = f"{tab}!A{row_num}:{last_col_letter}{row_num}"
                ws.update(rng, [row_values])
            else:
                ws.append_row(row_values)
