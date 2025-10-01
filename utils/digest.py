"""
Daily Digest generator: collates KPIs + alerts into a single PDF snapshot.
Requires reportlab (already added earlier).
"""
import io
from datetime import datetime
import pandas as pd
import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

from utils.finance import load_finance_df, compute_profitability, kpis as finance_kpis
from utils.data import load_sample_df
from utils.alerts_archive import alerts_buffer_to_df

def _make_table(df: pd.DataFrame, max_rows: int = 30):
    if df is None or df.empty:
        return [Paragraph("No data", getSampleStyleSheet()["Normal"])]
    df = df.tail(max_rows)
    data = [list(df.columns)] + df.astype(str).values.tolist()
    tbl = Table(data, repeatRows=1)
    tbl.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),colors.lightgrey),
        ("GRID",(0,0),(-1,-1),0.25,colors.grey),
        ("FONTSIZE",(0,0),(-1,-1),8),
        ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.whitesmoke,colors.white])
    ]))
    return [tbl]

def generate_digest_pdf() -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    elems = []

    # Title
    elems.append(Paragraph("Amazon Cockpit Daily Digest", styles["Title"]))
    elems.append(Paragraph(datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"), styles["Normal"]))
    elems.append(Spacer(1,12))

    # Finance KPIs
    f_raw = load_finance_df()
    f_df = compute_profitability(f_raw)
    rev, gp, np, acos = finance_kpis(f_df)
    elems.append(Paragraph(f"Finance KPIs — Revenue ${rev:,.0f}, GP ${gp:,.0f}, Net ${np:,.0f}, ACoS {acos:.1f}%", styles["Heading2"]))

    # Product Health
    p_df = load_sample_df("product")
    low_doc = int((p_df["Days of Cover"] < 10).sum())
    suppressed = int((p_df.get("Suppressed?", False) == True).sum()) if "Suppressed?" in p_df.columns else 0
    elems.append(Paragraph(f"Product KPIs — {len(p_df.index)} ASINs, {low_doc} low cover, {suppressed} suppressed, Avg Stars {p_df['Stars'].mean():.2f}", styles["Heading2"]))

    elems.append(Spacer(1,12))

    # Alerts
    elems.append(Paragraph("Alerts Summary", styles["Heading2"]))
    a_df = alerts_buffer_to_df(limit=100)
    elems += _make_table(a_df, max_rows=30)

    doc.build(elems)
    return buf.getvalue()
