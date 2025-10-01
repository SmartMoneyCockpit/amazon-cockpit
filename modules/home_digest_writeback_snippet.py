# --- Paste this near the "Daily Digest" section on Home ---
from utils.digest_log import append_digest_metadata

st.subheader("🗂️ Log Digest Metadata to Google Sheets")
sheet_id = st.secrets.get("gsheets_digest_log_sheet_id", "")
if not sheet_id:
    st.info("Set secret `gsheets_digest_log_sheet_id` to enable digest logging.")
else:
    if st.button("Append Today's KPIs + Alerts Counts"):
        n = append_digest_metadata(sheet_id, worksheet="daily_digest_log")
        if n > 0:
            st.success(f"Appended {n} row(s) to daily_digest_log.")
        else:
            st.warning("No rows appended.")
