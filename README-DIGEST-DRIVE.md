# Next Step: Digest PDF → Google Drive + Sheets Link

This pack adds one-click **upload of the Daily Digest PDF to Google Drive** and appends
the file link to your **daily_digest_log** Google Sheet.

## Files
- `utils/drive_upload.py` → generic Drive uploader (service account)
- `utils/digest_drive.py` → orchestrates generate → upload → log
- `snapshot_drive.py` → manual entry point
- `modules_home_digest_drive_snippet.py` → Home UI button (Generate, Upload & Log)

## Secrets
- `gdrive_digest_folder_id` = Google Drive **folder ID** where PDFs go
- `gdrive_service_account` (JSON) = optional; if not set, we reuse `gsheets_credentials`

## Requirements (append to requirements.txt)
```
google-api-python-client>=2.137.0
google-auth-httplib2>=0.2.0
google-auth-oauthlib>=1.2.0
```

## How to apply
1) Copy `utils/drive_upload.py` and `utils/digest_drive.py`.
2) Add `snapshot_drive.py` (optional for direct runs).
3) In `modules/home.py`, paste the snippet to add the **Generate, Upload & Log** button.
4) Add secrets and share the Drive folder with the service account email.
5) Redeploy and click the button. The Sheet gains columns `drive_file_id` and `drive_webViewLink` for each day.

## Notes
- The uploader sets file permissions to `anyone with the link: reader` when possible; remove that step if you want stricter access.
- For strict auditing, we can log SHA256 of the PDF and enforce filename conventions.
```
