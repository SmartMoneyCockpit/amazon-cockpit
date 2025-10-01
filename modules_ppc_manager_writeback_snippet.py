# --- Add this block after you build `actions_df` and (optionally) show the Bulk Exports ---
from utils.ppc_changes import build_changes_log
from utils.gsheets_write import append_df

st.subheader("Changes Log → Google Sheets")
sheet_id = st.secrets.get("gsheets_changes_log_sheet_id", "")
ws_title = st.text_input("Worksheet title", value="ppc_changes_log")
can_write = bool(sheet_id)

if not can_write:
    st.info("Set secret `gsheets_changes_log_sheet_id` to enable write-back.")
else:
    log_df = build_changes_log(actions_df, actor="cockpit")
    st.dataframe(log_df, use_container_width=True, height=200)
    if st.button("Append to Google Sheet"):
        n = append_df(sheet_id, ws_title, log_df)
        if n > 0:
            st.success(f"Appended {n} row(s) to worksheet '{ws_title}'.")
        else:
            st.warning("No rows appended.")
