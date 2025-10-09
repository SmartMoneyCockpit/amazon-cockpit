# utils/exporters.py
import io
import pandas as pd
from datetime import datetime
from services.amazon_ads_service import _db

def export_finance_monthly(year: int, month: int) -> bytes:
    prefix = f"{year:04d}-{month:02d}"
    con = _db()
    df = pd.read_sql_query(
        "SELECT date, adType, campaignId, campaignName, impressions, clicks, cost, sales14d "
        "FROM metrics WHERE substr(date,1,7)=? ORDER BY date, adType, campaignName",
        con, params=[prefix]
    )
    con.close()
    if df.empty:
        return pd.DataFrame(columns=[
            "date","adType","campaignId","campaignName","impressions","clicks","cost","sales14d"
        ]).to_csv(index=False).encode("utf-8")
    for col in ["impressions","clicks","cost","sales14d"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    total = df[["impressions","clicks","cost","sales14d"]].sum(numeric_only=True)
    summary = pd.DataFrame({
        "date": [prefix],
        "adType": ["ALL"],
        "campaignId": ["-"],
        "campaignName": ["Monthly totals"],
        "impressions": [int(total["impressions"])],
        "clicks": [int(total["clicks"])],
        "cost": [float(total["cost"])],
        "sales14d": [float(total["sales14d"])],
    })
    out = pd.concat([df, summary], ignore_index=True)
    buf = io.BytesIO()
    out.to_csv(buf, index=False)
    return buf.getvalue()
