import streamlit as st
import pandas as pd
from utils.layout import section_header
from utils.data import load_sheet, load_sample_df
from utils.compliance import ensure_columns, parse_dates, add_expiry_metrics, kpi_counts
from utils.export import df_to_csv_bytes, df_to_xlsx_bytes, simple_pdf_bytes
from utils.alerts import Alert

def _sample_index() -> pd.DataFrame:
    return pd.DataFrame({
        "Document": ["COA-2025Q1-NOPAL","GMP-2025-Audit","COA-2025Q1-MANGO"],
        "SKU": ["NOPAL-120","*","MANGO-120"],
        "Type": ["COA","GMP","COA"],
        "Lot": ["NPL-250101","—","MNG-250102"],
        "ManufactureDate": ["2025-01-05","","2025-01-06"],
        "ExpiryDate": ["2026-01-05","","2026-01-06"],
        "FileLink": ["https://drive.google.com/...","","https://drive.google.com/..."],
        "VerifiedBy": ["Joanne","Joanne","Joanne"],
        "VerifiedOn": ["2025-01-10","2025-02-01","2025-01-12"],
        "Notes": ["Batch COA uploaded","","Batch COA uploaded"]
    })

def compliance_vault_view():
    section_header("🧾 Compliance Vault")
    st.caption("GMP/COA, expiry tracking, 3rd‑party lab PDFs. Uses a Google Sheet index if configured; otherwise sample data.")

    # Try to read a Google Sheet index if provided via secrets
    sheet_id = st.secrets.get("gsheets_compliance_sheet_id", "")
    df = load_sheet(sheet_id, "index") if sheet_id else _sample_index()

    df = ensure_columns(df)
    df = parse_dates(df)
    df = add_expiry_metrics(df)

    # KPIs
    exp, d30, d60, d90 = kpi_counts(df)
    c = st.columns(4)
    c[0].metric("Expired", exp)
    c[1].metric("Due ≤30d", d30)
    c[2].metric("Due 31–60d", d60)
    c[3].metric("Due 61–90d", d90)

    st.dataframe(df, use_container_width=True)

    # Upload (in-memory; export your updated index)
    st.subheader("Add / Update Documents")
    with st.form("compliance_add"):
        col1, col2, col3 = st.columns(3)
        doc = col1.text_input("Document ID/Name")
        sku = col2.text_input("SKU (or *)", value="*")
        typ = col3.selectbox("Type", ["COA","GMP","Label","Other"])
        lot = st.text_input("Lot")
        col4, col5 = st.columns(2)
        manuf = col4.date_input("Manufacture Date", value=None)
        expi = col5.date_input("Expiry Date", value=None)
        link = st.text_input("File Link (Drive/Share)")
        vby, von = st.columns(2)
        verified_by = vby.text_input("Verified By", value="Joanne")
        verified_on = von.date_input("Verified On", value=None)
        notes = st.text_area("Notes")
        submitted = st.form_submit_button("Add to Index (session)")
    if submitted:
        new_row = {
            "Document": doc, "SKU": sku, "Type": typ, "Lot": lot,
            "ManufactureDate": pd.to_datetime(manuf) if manuf else pd.NaT,
            "ExpiryDate": pd.to_datetime(expi) if expi else pd.NaT,
            "FileLink": link, "VerifiedBy": verified_by,
            "VerifiedOn": pd.to_datetime(verified_on) if verified_on else pd.NaT,
            "Notes": notes
        }
        st.session_state.setdefault("compliance_edits", [])
        st.session_state["compliance_edits"].append(new_row)
        st.success("Added to in-session index. Export below and upload to your master Sheet.")

    # Show pending edits
    edits = st.session_state.get("compliance_edits", [])
    if edits:
        st.info(f"{len(edits)} new/updated row(s) staged")
        staged_df = pd.DataFrame(edits)
        staged_df = ensure_columns(parse_dates(staged_df))
        st.dataframe(staged_df, use_container_width=True)

        # Export merged index
        merged = pd.concat([df, staged_df], ignore_index=True)
        merged = ensure_columns(merged)
        with st.expander("⬇️ Export Updated Index"):
            c1, c2, c3 = st.columns(3)
            c1.download_button("CSV", df_to_csv_bytes(merged), file_name="compliance_index_updated.csv")
            c2.download_button("XLSX", df_to_xlsx_bytes(merged), file_name="compliance_index_updated.xlsx")
            c3.download_button("PDF", simple_pdf_bytes("Compliance Index", merged), file_name="compliance_index_updated.pdf")

    # Push expiry alerts to Alerts Hub buffer
    expiring = df[df["ExpiryStatus"].isin(["expired","due in 30","due in 60"])]
    if not expiring.empty:
        alerts = []
        for _, r in expiring.iterrows():
            sev = "crit" if r["ExpiryStatus"] in ["expired","due in 30"] else "warn"
            msg = f"{r.get('Type','Doc')} for {r.get('SKU','*')} {r['ExpiryStatus']} (Lot {r.get('Lot','—')})"
            alerts.append(Alert(severity=sev, message=msg, source="Compliance"))
        st.session_state.setdefault("alerts_buffer", [])
        st.session_state["alerts_buffer"].extend([a.__dict__ for a in alerts])

    st.info("Tip: store your master index in a Google Sheet named worksheet **index** and set secret `gsheets_compliance_sheet_id`.")
