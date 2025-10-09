# infra/sheets_client.py
import os, json

class _SheetsDisabled(Exception):
    pass

def _disabled(reason):
    raise _SheetsDisabled(reason)

def _has_creds():
    return bool(os.getenv("SHEETS_CREDENTIALS_JSON") or os.getenv("SHEETS_CREDENTIALS_FILE"))

def _load_client():
    try:
        import gspread
        from google.oauth2.service_account import Credentials
    except Exception as e:
        _disabled(f"Sheets bridge not available: {e}")

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]

    if os.getenv("SHEETS_CREDENTIALS_JSON"):
        creds_dict = json.loads(os.getenv("SHEETS_CREDENTIALS_JSON"))
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    elif os.getenv("SHEETS_CREDENTIALS_FILE"):
        creds = Credentials.from_service_account_file(os.getenv("SHEETS_CREDENTIALS_FILE"), scopes=scopes)
    else:
        _disabled("SHEETS_CREDENTIALS_JSON (or SHEETS_CREDENTIALS_FILE) not set")

    return gspread.authorize(creds)

class SheetsClient:
    def __init__(self, doc_id=None):
        self.doc_id = doc_id or os.getenv("SHEETS_DOC_ID")
        if not self.doc_id:
            _disabled("SHEETS_DOC_ID not set")
        self.gc = _load_client()

    def worksheet(self, name):
        return self.gc.open_by_key(self.doc_id).worksheet(name)

def sheets_status():
    if not _has_creds():
        return False, "Credentials missing"
    try:
        _load_client()
        return True, "OK"
    except _SheetsDisabled as e:
        return False, str(e)
