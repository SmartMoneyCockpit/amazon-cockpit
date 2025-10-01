import streamlit as st
import pandas as pd
from utils.layout import section_header
from utils.export import df_to_csv_bytes, df_to_xlsx_bytes, simple_pdf_bytes
from utils.finance import load_finance_df, compute_profitability, kpis
from utils.alerts import Alert

def finance_dashboard_view():
    section_header("💵 Finance Dashboard")
    st.caption("Revenue, COGS, Fees, Ad Spend → profitability. Google Sheets supported via `gsheets_finance_sheet_id` (worksheet: finance).")

    raw = load_finance_df()
    df = compute_profitability(raw)

    # KPIs (YTD / total range in data)
    rev, gp, np, acos = kpis(df)
    c = st.columns(4)
    c[0].metric("Revenue (Total)", f"${rev:,.0f}")
    c[1].metric("Gross Profit (Total)", f"${gp:,.0f}")
    c[2].metric("Net Profit (Total)", f"${np:,.0f}")
    c[3].metric("ACoS (Total)", f"{acos:.1f}%")

    # Filters
    with st.expander("Filters"):
        skus = sorted(df["SKU"].unique().tolist())
        sel_skus = st.multiselect("SKU", skus, default=skus)
        df = df[df["SKU"].isin(sel_skus)] if sel_skus else df

    # Trend charts
    st.subheader("Trends by Month")
    monthly = df.groupby("Month", as_index=False)[["Revenue","GrossProfit","NetProfit","AdSpend"]].sum()
    st.line_chart(monthly.set_index("Month")[["Revenue","GrossProfit","NetProfit"]])
    st.area_chart(monthly.set_index("Month")[["AdSpend"]])

    # SKU table
    st.subheader("SKU Profitability")
    sku_view = df.groupby(["Month","SKU","ASIN"], as_index=False)[["Units","Revenue","COGS","Fees","AdSpend","GrossProfit","NetProfit","GrossMargin%","NetMargin%","Acos%","NetPerUnit"]].sum()
    st.dataframe(sku_view, use_container_width=True)

    with st.expander("⬇️ Export"):
        c1, c2, c3 = st.columns(3)
        c1.download_button("CSV", df_to_csv_bytes(sku_view), file_name="finance_sku_view.csv")
        c2.download_button("XLSX", df_to_xlsx_bytes(sku_view), file_name="finance_sku_view.xlsx")
        c3.download_button("PDF", simple_pdf_bytes("Finance – SKU Profitability", sku_view), file_name="finance_sku_view.pdf")

    # Alerts: negative net margin or very low gross margin
    neg_net = sku_view[sku_view["NetMargin%"] < 0]
    low_gross = sku_view[sku_view["GrossMargin%"] < 30]
    alerts = []
    for _, r in neg_net.iterrows():
        alerts.append(Alert("crit", f"NEGATIVE net margin for {r['SKU']} ({r['Month']})", "Finance"))
    for _, r in low_gross.iterrows():
        alerts.append(Alert("warn", f"Low gross margin <30% for {r['SKU']} ({r['Month']})", "Finance"))
    if alerts:
        st.warning(f"{len(alerts)} finance alert(s) detected — see Alerts Hub tab.")
        st.session_state.setdefault("alerts_buffer", [])
        st.session_state["alerts_buffer"].extend([a.__dict__ for a in alerts])
