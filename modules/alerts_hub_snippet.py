# --- Paste this inside your alerts_hub_view() after rendering the alerts dataframe ---
import streamlit as st
from utils.alerts_archive import export_alerts_pdf, export_alerts_csv, export_alerts_xlsx, append_alerts_to_sheet

st.subheader("Archive Alerts")
limit = st.number_input("Rows to include", min_value=50, max_value=10000, value=500, step=50)

# Exports
c1, c2, c3 = st.columns(3)
c1.download_button("Download CSV", data=export_alerts_csv(limit), file_name="alerts_history.csv")
c2.download_button("Download XLSX", data=export_alerts_xlsx(limit), file_name="alerts_history.xlsx")
c3.download_button("Download PDF", data=export_alerts_pdf("Alerts History Snapshot", limit), file_name="alerts_history.pdf")

# Google Sheets append
st.markdown("**Append to Google Sheet**")
sheet_id = st.secrets.get("gsheets_alerts_history_sheet_id", "")
ws_title = st.text_input("Worksheet title", value="alerts_history")
if not sheet_id:
    st.info("Set secret `gsheets_alerts_history_sheet_id` to enable archiving to Sheets.")
else:
    if st.button("Append Now"):
        n = append_alerts_to_sheet(sheet_id, ws_title, limit=limit)
        if n > 0:
            st.success(f"Appended {n} row(s) to '{ws_title}'.")
        else:
            st.warning("No rows appended.")
