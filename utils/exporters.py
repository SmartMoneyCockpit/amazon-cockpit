from __future__ import annotations
import os, pathlib, datetime as dt
from typing import Tuple, Optional
import pandas as pd

def _ensure_dir(p: pathlib.Path):
    p.mkdir(parents=True, exist_ok=True)

def _month_bounds(year: int, month: int) -> Tuple[dt.date, dt.date]:
    start = dt.date(year, month, 1)
    if month == 12:
        end = dt.date(year + 1, 1, 1)
    else:
        end = dt.date(year, month + 1, 1)
    return start, end

def _to_pdf_if_available(df: pd.DataFrame, out_pdf: pathlib.Path, title: str = "Finance Monthly Report") -> Optional[pathlib.Path]:
    # Optional PDF generation (requires reportlab)
    try:
        from reportlab.lib.pagesizes import LETTER
        from reportlab.pdfgen import canvas
        from reportlab.lib.units import inch
        c = canvas.Canvas(str(out_pdf), pagesize=LETTER)
        width, height = LETTER
        y = height - 1 * inch
        c.setFont("Helvetica-Bold", 14)
        c.drawString(1 * inch, y, title)
        y -= 0.3 * inch
        c.setFont("Helvetica", 9)
        lines = [", ".join(map(str, df.columns.values))]
        for _, row in df.iterrows():
            lines.append(", ".join("" if v is None else str(v) for v in row.values))
        for line in lines:
            if y < 0.75 * inch:
                c.showPage(); y = height - 0.75 * inch
                c.setFont("Helvetica", 9)
            c.drawString(1 * inch, y, line[:130])  # simple wrap
            y -= 0.2 * inch
        c.save()
        return out_pdf
    except Exception:
        return None

def export_finance_monthly(df: pd.DataFrame, year: int, month: int, out_dir: str = "snapshots") -> Tuple[pathlib.Path, Optional[pathlib.Path]]:
    out_base = pathlib.Path(out_dir) / f"{year:04d}-{month:02d}"
    _ensure_dir(out_base)
    # Normalize
    dfn = df.copy()
    dfn.columns = [str(c).strip().lower() for c in dfn.columns]
    if "date" in dfn.columns:
        dfn["date"] = pd.to_datetime(dfn["date"], errors="coerce").dt.date
    start, end = _month_bounds(year, month)
    if "date" in dfn.columns:
        dfn = dfn[(dfn["date"] >= start) & (dfn["date"] < end)]
    # Write CSV
    csv_path = out_base / "finance_monthly.csv"
    dfn.to_csv(csv_path, index=False)
    # Try PDF (optional)
    pdf_path = out_base / "finance_monthly.pdf"
    pdf_built = _to_pdf_if_available(dfn, pdf_path, title=f"Finance Monthly Report — {year:04d}-{month:02d}")
    return csv_path, (pdf_path if pdf_built else None)
