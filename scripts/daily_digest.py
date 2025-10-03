
from __future__ import annotations
import os, io, zipfile, datetime as dt
import pandas as pd

TMP_DIR = os.environ.get("DIGEST_OUT_DIR", "/tmp")

def _read_tab(name: str) -> pd.DataFrame:
    try:
        from utils import sheets_bridge as SB
        df = SB.read_tab(name)
        if isinstance(df, pd.DataFrame):
            df.columns = [c.strip().lower() for c in df.columns]
            return df
    except Exception:
        pass
    return pd.DataFrame()

def _derive_finance(fin: pd.DataFrame) -> pd.DataFrame:
    if fin.empty: return fin
    f = fin.copy()
    f.columns = [c.strip().lower() for c in f.columns]
    if "date" in f.columns and "month" not in f.columns:
        f["month"] = pd.to_datetime(f["date"], errors="coerce").dt.to_period("M").astype(str)
    for c in ["revenue","fees","other"]:
        if c not in f.columns: f[c] = 0.0
    f["net"] = f["revenue"] - f["fees"] - f["other"]
    return f

def _compute_kpis(fin: pd.DataFrame, actions: pd.DataFrame, lowdoc: pd.DataFrame, comp: pd.DataFrame):
    tz = os.getenv("TIMEZONE","America/Mazatlan")
    now = pd.Timestamp.utcnow().tz_localize("UTC").tz_convert(tz)
    this_month = now.strftime("%Y-%m")
    this_year = now.year

    rev_mtd = net_mtd = rev_ytd = net_ytd = 0.0
    if not fin.empty and "month" in fin.columns:
        mtd = fin[fin["month"] == this_month]
        ytd = fin[pd.to_datetime(fin["month"], errors="coerce").dt.year == this_year]
        rev_mtd = float(mtd["revenue"].sum())
        net_mtd = float(mtd["net"].sum())
        rev_ytd = float(ytd["revenue"].sum())
        net_ytd = float(ytd["net"].sum())

    crit = attn = 0
    if not actions.empty and "severity" in actions.columns:
        sev = actions["severity"].astype(str).str.lower()
        crit = int((sev=="red").sum())
        attn = int((sev=="yellow").sum())

    doc_at_risk = len(lowdoc) if not lowdoc.empty else 0
    comp_due = len(comp) if not comp.empty else 0

    return dict(now=now, rev_mtd=rev_mtd, net_mtd=net_mtd, rev_ytd=rev_ytd, net_ytd=net_ytd,
                crit=crit, attn=attn, doc_at_risk=doc_at_risk, comp_due=comp_due)

def _export_csv_pack(date_tag: str, fin: pd.DataFrame, lowdoc: pd.DataFrame, comp: pd.DataFrame, ppc: pd.DataFrame, actions: pd.DataFrame) -> str:
    zip_path = os.path.join(TMP_DIR, f"digest_{date_tag}.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        if not fin.empty:
            z.writestr("finance_summary.csv", fin.to_csv(index=False))
        if isinstance(lowdoc, pd.DataFrame):
            z.writestr("alerts_out_low_doc.csv", lowdoc.to_csv(index=False))
        if isinstance(comp, pd.DataFrame):
            z.writestr("alerts_out_compliance.csv", comp.to_csv(index=False))
        if isinstance(ppc, pd.DataFrame):
            z.writestr("alerts_out_ppc.csv", ppc.to_csv(index=False))
        if isinstance(actions, pd.DataFrame):
            z.writestr("actions_out.csv", actions.to_csv(index=False))
    return zip_path

def _make_charts_images(fin: pd.DataFrame, actions: pd.DataFrame):
    # Save small PNG charts to memory for embedding into PDF.
    imgs = {}
    try:
        import matplotlib.pyplot as plt
        # Revenue trend
        fig, ax = plt.subplots(figsize=(4.2, 1.8))
        if not fin.empty and "month" in fin.columns:
            trend = fin.groupby("month", as_index=False).agg(revenue=("revenue","sum"), net=("net","sum"))
            trend["month_dt"] = pd.to_datetime(trend["month"], errors="coerce")
            trend = trend.sort_values("month_dt").tail(6)
            ax.plot(trend["month_dt"].dt.strftime("%Y-%m"), trend["revenue"])
            ax.set_title("Revenue (6m)"); ax.set_xlabel(""); ax.set_ylabel("")
            plt.xticks(rotation=30, ha="right")
        buf = io.BytesIO(); fig.savefig(buf, format="png", bbox_inches="tight"); plt.close(fig)
        imgs["trend"] = buf.getvalue()
        # Actions bar
        fig2, ax2 = plt.subplots(figsize=(4.2, 1.8))
        if not actions.empty and "type" in actions.columns:
            bar = actions.groupby("type").size().sort_values(ascending=False).head(5)
            ax2.bar(bar.index.astype(str), bar.values)
            ax2.set_title("Actions by Type"); ax2.set_xlabel(""); ax2.set_ylabel("")
            plt.xticks(rotation=25, ha="right")
        buf2 = io.BytesIO(); fig2.savefig(buf2, format="png", bbox_inches="tight"); plt.close(fig2)
        imgs["actions"] = buf2.getvalue()
    except Exception:
        pass
    return imgs

def _write_pdf_1pager(date_tag: str, k: dict, fin_table: pd.DataFrame, lowdoc: pd.DataFrame, comp: pd.DataFrame, actions_top: pd.DataFrame, imgs: dict) -> str:
    out_pdf = os.path.join(TMP_DIR, f"digest_{date_tag}.pdf")
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import mm
        from reportlab.lib import colors
        from reportlab.pdfgen import canvas
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import Paragraph, SimpleDocTemplate, Table, TableStyle, Spacer, Image

        doc = SimpleDocTemplate(out_pdf, pagesize=A4, leftMargin=12*mm, rightMargin=12*mm, topMargin=10*mm, bottomMargin=10*mm)
        styles = getSampleStyleSheet()
        elements = []

        title = Paragraph(f"<b>Owner’s Daily Digest</b> — {date_tag} — {k['now'].strftime('%H:%M %Z')}", styles["Title"])
        elements.append(title); elements.append(Spacer(0, 4))

        kpi_data = [
            ["Revenue (MTD)", f"${k['rev_mtd']:,.0f}", "Net (MTD)", f"${k['net_mtd']:,.0f}"],
            ["Revenue (YTD)", f"${k['rev_ytd']:,.0f}", "Net (YTD)", f"${k['net_ytd']:,.0f}"],
            ["Critical", f"{k['crit']}", "Attention", f"{k['attn']}"],
            ["Low DoC", f"{k['doc_at_risk']}", "Compliance Due", f"{k['comp_due']}"],
        ]
        t = Table(kpi_data, colWidths=[80, 90, 80, 90])
        t.setStyle(TableStyle([("GRID",(0,0),(-1,-1),0.25,colors.grey),("BACKGROUND",(0,0),(-1,0),colors.whitesmoke),
                               ("FONTNAME",(0,0),(-1,-1),"Helvetica"),("FONTSIZE",(0,0),(-1,-1),9)]))
        elements.append(t); elements.append(Spacer(0, 6))

        fin_mini = fin_table.copy()
        if not fin_mini.empty:
            fin_mini = fin_mini[["month","revenue","fees","other","net"]].tail(2)
            fin_mini.columns = ["Month","Revenue","Fees","Other","Net"]
            fin_rows = [fin_mini.columns.tolist()] + fin_mini.fillna(0).round(0).applymap(lambda x: f"${x:,.0f}" if isinstance(x,(int,float)) else x).values.tolist()
            from reportlab.platypus import Table
            ft = Table(fin_rows, colWidths=[70, 70, 60, 60, 70])
            ft.setStyle(TableStyle([("GRID",(0,0),(-1,-1),0.25,colors.grey),("BACKGROUND",(0,0),(-1,0),colors.whitesmoke),("FONTSIZE",(0,0),(-1,-1),8)]))
            elements.append(Paragraph("<b>Finance (last month + MTD)</b>", styles["Heading4"]))
            elements.append(ft); elements.append(Spacer(0, 4))

        def _mini_table(df: pd.DataFrame, cols, title):
            if df is None or df.empty: 
                return [Paragraph(f"<b>{title}</b> — none", styles["Heading5"]), Spacer(0,2)]
            d = df.copy().head(6)
            d = d[[c for c in cols if c in d.columns]]
            rows = [ [c.title() for c in d.columns] ] + d.values.tolist()
            tb = Table(rows, colWidths=[110, 70, 70, 70])
            tb.setStyle(TableStyle([("GRID",(0,0),(-1,-1),0.25,colors.grey),("BACKGROUND",(0,0),(-1,0),colors.whitesmoke),("FONTSIZE",(0,0),(-1,-1),7)]))
            return [Paragraph(f"<b>{title}</b>", styles["Heading5"]), tb, Spacer(0,2)]

        elements += _mini_table(lowdoc, ["sku","asin","days_of_cover"], "Low DoC")
        elements += _mini_table(comp, ["asin","doc_type","days_to_expiry"], "Compliance Due")

        if actions_top is not None and not actions_top.empty:
            top = actions_top.head(10)[["type","key","detail","severity"]]
            rows = [ ["Type","Key","Detail","Sev"] ] + top.values.tolist()
            at = Table(rows, colWidths=[90, 120, 220, 40])
            at.setStyle(TableStyle([("GRID",(0,0),(-1,-1),0.25,colors.grey),("BACKGROUND",(0,0),(-1,0),colors.whitesmoke),("FONTSIZE",(0,0),(-1,-1),7)]))
            elements.append(Paragraph("<b>Top Actions</b>", styles["Heading5"]))
            elements.append(at); elements.append(Spacer(0, 4))

        pics = []
        from reportlab.platypus import Image
        if "trend" in imgs:
            pics.append(Image(io.BytesIO(imgs["trend"]), width=180, height=80))
        if "actions" in imgs:
            pics.append(Image(io.BytesIO(imgs["actions"]), width=180, height=80))
        if pics:
            from reportlab.platypus import Table
            row = Table([[pics[0], pics[1] if len(pics)>1 else ""]], colWidths=[200,200])
            elements.append(row)

        doc.build(elements)
        return out_pdf
    except Exception as e:
        out_txt = os.path.join(TMP_DIR, f"digest_{date_tag}.txt")
        with open(out_txt, "w") as f:
            f.write("Owner's Daily Digest (install reportlab for PDF output)\n")
            f.write(str(k)+"\n")
        return out_txt

def generate() -> dict:
    os.makedirs(TMP_DIR, exist_ok=True)
    date_tag = dt.datetime.now().strftime("%Y%m%d")

    fin = _derive_finance(_read_tab("profitability_monthly"))
    actions = _read_tab("actions_out")
    lowdoc = _read_tab("alerts_out_low_doc")
    comp = _read_tab("alerts_out_compliance")
    ppc = _read_tab("alerts_out_ppc")

    fin_summary = pd.DataFrame()
    if not fin.empty and "month" in fin.columns:
        fin_summary = fin.groupby("month", as_index=False).agg(revenue=("revenue","sum"), fees=("fees","sum"), other=("other","sum"))
        fin_summary["net"] = fin_summary["revenue"] - fin_summary["fees"] - fin_summary["other"]

    k = _compute_kpis(fin, actions, lowdoc, comp)
    zip_path = _export_csv_pack(date_tag, fin_summary, lowdoc, comp, ppc, actions)
    imgs = _make_charts_images(fin, actions)
    pdf_path = _write_pdf_1pager(date_tag, k, fin_summary, lowdoc, comp, actions, imgs)

    return {"pdf": pdf_path, "zip": zip_path}
