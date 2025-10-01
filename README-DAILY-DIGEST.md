# Next Step: Daily Digest Vault

Adds a generator for a **Daily Digest PDF** containing:
- Finance KPIs (Revenue, GP, Net, ACoS)
- Product KPIs (ASINs, low cover, suppressed, avg stars)
- Alerts table (latest 30)

## Files
- `utils/digest.py` → PDF builder
- `snapshot.py` → simple Streamlit entry point for manual/cron run
- `modules_home_digest_snippet.py` → snippet to paste into Home tab

## Usage
1) Copy `utils/digest.py` and `snapshot.py` into your project.
2) In `modules/home.py`, paste the snippet (`modules_home_digest_snippet.py`) near the bottom of `dashboard_home_view()`.
3) Redeploy. On Home you’ll see **Daily Digest** with a generate button.
4) You can also run separately:
   ```
   streamlit run snapshot.py
   ```

## Automation
For daily automation:
- Add a Render Cron Job or GitHub Action to call `snapshot.py` once per day.
- We can extend to auto‑upload to Google Sheets, Drive, or S3 vaults later.
