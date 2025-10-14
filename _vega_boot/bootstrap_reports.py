#!/usr/bin/env python3
import os, pathlib, datetime as dt, csv, sys
from typing import List
def ensure_dir(p): pathlib.Path(p).mkdir(parents=True, exist_ok=True)

ROOT = pathlib.Path(__file__).resolve().parent
REPORTS = ROOT / "reports"
ASSETS  = ROOT / "assets"
ensure_dir(REPORTS / "na")
ensure_dir(REPORTS / "apac")
ensure_dir(REPORTS / "europe")
ensure_dir(ASSETS)

def write_markdown(region: str):
    now = dt.datetime.utcnow().strftime("%Y-%m-%d %H:%MZ")
    md = (REPORTS / region / "morning_report.md")
    md.write_text(f"# Morning Report — {region.upper()}\n\nGenerated: {now}\n\n- Placeholder seeded by bootstrap.\n- Connect CI later to auto-refresh.\n")

def write_calendar(name: str):
    path = ASSETS / f"econ_calendar_{name}.csv"
    rows = [
        ["date","time","event","impact"],
        ["2025-10-13","08:30","CPI (YoY)","High"],
        ["2025-10-14","14:00","FOMC Minutes","High"],
        ["2025-10-15","10:00","Consumer Sentiment","Medium"],
    ]
    with open(path,"w",newline="",encoding="utf-8") as f:
        csv.writer(f).writerows(rows)

for region in ("na","apac","europe"):
    write_markdown(region)
for cal in ("na","apac","europe"):
    write_calendar(cal)

print("Bootstrapped reports to ./reports/* and assets/econ_calendar_*.csv")