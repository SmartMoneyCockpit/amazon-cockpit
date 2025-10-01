import streamlit as st
import pandas as pd
from utils.layout import section_header
from utils.export import df_to_csv_bytes, df_to_xlsx_bytes, simple_pdf_bytes
from utils.seo import load_keyword_index_df, load_competitors_df, indexing_kpis, deindexed_critical
from utils.alerts import Alert

def a_plus_seo_view():
    section_header("🧩 A+ & SEO Panel")
    st.caption("Keyword indexing health, deindexed critical terms, and competitor A+ snapshot. Connect Google Sheets to power this panel.")

    # Keyword Indexing
    st.subheader("Keyword Indexing")
    kdf = load_keyword_index_df()
    st.dataframe(kdf, use_container_width=True)
    total, indexed, missing = indexing_kpis(kdf)
    m1, m2, m3 = st.columns(3)
    m1.metric("Tracked Keywords", total)
    m2.metric("Indexed", indexed)
    m3.metric("Not Indexed", missing)

    with st.expander("⬇️ Export (Keywords)"):
        c1, c2, c3 = st.columns(3)
        c1.download_button("CSV", df_to_csv_bytes(kdf), file_name="keywords_index.csv")
        c2.download_button("XLSX", df_to_xlsx_bytes(kdf), file_name="keywords_index.xlsx")
        c3.download_button("PDF", simple_pdf_bytes("Keyword Indexing", kdf), file_name="keywords_index.pdf")

    # Deindexed critical alerts
    critical = deindexed_critical(kdf)
    if not critical.empty:
        st.error(f"{len(critical)} high-priority keyword(s) are NOT indexed.")
        st.dataframe(critical, use_container_width=True)
        # Push alerts to Alerts Hub
        st.session_state.setdefault("alerts_buffer", [])
        for _, r in critical.iterrows():
            kw = r.get("Keyword","(unknown)")
            asin = r.get("ASIN","")
            st.session_state["alerts_buffer"].append(Alert(severity="crit", message=f"Deindexed: '{kw}' for {asin}", source="A+ & SEO").__dict__)

    st.divider()

    # Competitor Snapshot
    st.subheader("Competitor Snapshot")
    cdf = load_competitors_df()
    st.dataframe(cdf, use_container_width=True)
    c1, c2, c3 = st.columns(3)
    c1.metric("Avg Price", f"${float(cdf['Price'].mean()):.2f}" if not cdf.empty else "$0.00")
    c2.metric("Avg Stars", f"{float(cdf['Stars'].mean()):.2f}" if not cdf.empty else "0.00")
    c3.metric("With A+ Content", int(cdf.get("APlus?", pd.Series(dtype=bool)).sum()) if not cdf.empty else 0)

    with st.expander("⬇️ Export (Competitors)"):
        c1, c2, c3 = st.columns(3)
        c1.download_button("CSV", df_to_csv_bytes(cdf), file_name="competitors.csv")
        c2.download_button("XLSX", df_to_xlsx_bytes(cdf), file_name="competitors.xlsx")
        c3.download_button("PDF", simple_pdf_bytes("Competitor Snapshot", cdf), file_name="competitors.pdf")

    st.info("Secrets supported: `gsheets_keywords_sheet_id`, `gsheets_competitors_sheet_id` (worksheets: keywords, competitors). If not set, sample data is shown.")
