import streamlit as st
import pandas as pd
from utils.export import df_to_csv_bytes, df_to_xlsx_bytes, simple_pdf_bytes
from utils.ppc_changes import actions_split, to_bytes_csv, build_changes_log

# This file is meant to be merged into your current modules/ppc_manager.py
# Add the following block AFTER you compute `actions_df` (i.e., after suggestions table).

def _render_bulk_changes_and_log(actions_df: pd.DataFrame):
    st.subheader("Bulk Changes & Log")
    if actions_df is None or actions_df.empty:
        st.info("No actions to export.")
        return
    camp, kw, neg = actions_split(actions_df)

    with st.expander("⬇️ Export Bulk Files"):
        c1, c2, c3 = st.columns(3)
        c1.download_button("Campaign Budgets CSV", to_bytes_csv(camp), file_name="campaigns_changes.csv")
        c2.download_button("Keyword Bids CSV", to_bytes_csv(kw), file_name="keywords_changes.csv")
        c3.download_button("Negatives CSV", to_bytes_csv(neg), file_name="negatives_changes.csv")

    # Flat changes log (append-only concept; here we just let user download the log snapshot).
    log_df = build_changes_log(actions_df, actor="cockpit")
    with st.expander("⬇️ Export Changes Log"):
        st.dataframe(log_df, use_container_width=True)
        st.download_button("Download Log CSV", df_to_csv_bytes(log_df), file_name="ppc_changes_log.csv")

# Call `_render_bulk_changes_and_log(actions_df)` where appropriate in your ppc_manager_view
