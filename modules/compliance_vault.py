
import streamlit as st
import pandas as pd
from utils.layout import section_header
from utils.compliance import ensure_columns, parse_dates, add_expiry_metrics, kpi_counts

def _sample_vault_df() -> pd.DataFrame:
    data = [
        {"Document":"COA Batch 2024-09","SKU":"NOPAL-120","Type":"COA","Lot":"L2409","ManufactureDate":"2024-09-15","ExpiryDate":"2026-09-14","FileLink":"","VerifiedBy":"","VerifiedOn":"","Notes":""},
        {"Document":"COA Batch 2025-01","SKU":"MANGO-120","Type":"COA","Lot":"L2501","ManufactureDate":"2025-01-10","ExpiryDate":"2026-12-31","FileLink":"","VerifiedBy":"","VerifiedOn":"","Notes":""},
        {"Document":"Label Proof","SKU":"NOPAL-240","Type":"GMP","Lot":"-","ManufactureDate":"","ExpiryDate":"","FileLink":"","VerifiedBy":"","VerifiedOn":"","Notes":""},
    ]
    return pd.DataFrame(data)

def compliance_vault_view():
    section_header("🧾 Compliance Vault")
    st.caption("GMP/COA, expiry tracking, 3rd‑party lab PDFs. Uses a Google Sheet index if configured, otherwise sample data.")
    # TODO: wire real Google Sheet; for now, sample
    df = _sample_vault_df()
    df = ensure_columns(df)
    df = parse_dates(df)
    df = add_expiry_metrics(df)  # adds DaysToExpiry + ExpiryStatus

    exp, d30, d60, d90 = kpi_counts(df)
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Expired", exp)
    c2.metric("Due in 30d", d30)
    c3.metric("Due in 60d", d60)
    c4.metric("Due in 90d", d90)

    st.dataframe(df, use_container_width=True)
    st.caption("Statuses are derived from ExpiryDate: expired (<0), 30/60/90 windows, otherwise ok.")
