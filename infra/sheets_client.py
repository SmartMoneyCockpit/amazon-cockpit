from __future__ import annotations
import gspread, time
from google.oauth2.service_account import Credentials
from tenacity import retry, stop_after_attempt, wait_exponential
import pandas as pd

class SheetsClient:
    def __init__(self):
        # existing init assumed elsewhere; keeping as-is if present
        try:
            scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
            self.creds = Credentials.from_service_account_file("gcp_service_account.json", scopes=scope)
            self.gc = gspread.authorize(self.creds)
            self.sh = self.gc.open_by_key(self._get_key())
        except Exception as e:
            raise

    def _get_key(self):
        # naive; in your app this likely reads from env/secrets
        import os
        return os.environ.get("GOOGLE_SHEET_KEY", "")

    @retry(stop=stop_after_attempt(4), wait=wait_exponential(multiplier=0.5, min=0.5, max=6))
    def read_table(self, sheet_name: str):
        ws = self.sh.worksheet(sheet_name)
        rows = ws.get_all_records()
        return rows

    @retry(stop=stop_after_attempt(4), wait=wait_exponential(multiplier=0.5, min=0.5, max=6))
    def write_table(self, sheet_name: str, rows, clear=False):
        ws = None
        try:
            ws = self.sh.worksheet(sheet_name)
        except Exception:
            ws = self.sh.add_worksheet(sheet_name, rows=100, cols=10)

        if clear:
            ws.clear()

        if isinstance(rows, pd.DataFrame):
            df = rows
        else:
            df = pd.DataFrame(rows)

        if df.empty:
            return

        ws.update([df.columns.tolist()] + df.values.tolist())
