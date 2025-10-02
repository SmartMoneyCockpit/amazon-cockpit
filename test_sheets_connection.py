# test_sheets_connection.py
import os, json, gspread
from datetime import datetime

def main():
    creds_json = os.getenv("GCP_SERVICE_ACCOUNT_JSON")
    if not creds_json:
        raise RuntimeError("Missing GCP_SERVICE_ACCOUNT_JSON")
    creds = json.loads(creds_json)
    gc = gspread.service_account_from_dict(creds)

    sheet_url = os.getenv("GOOGLE_SHEET_URL")
    if not sheet_url:
        raise RuntimeError("Missing GOOGLE_SHEET_URL")

    sh = gc.open_by_url(sheet_url)
    ws = sh.worksheet("Settings")
    rows = ws.get_all_records()
    print("Settings (first 5 rows):", rows[:5])
    ws.append_row([f"ping_at_{datetime.utcnow().isoformat()}", "from test_sheets_connection.py"])
    print("Ping row appended ✅")

if __name__ == "__main__":
    main()