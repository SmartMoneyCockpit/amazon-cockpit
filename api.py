from fastapi import FastAPI, Depends, HTTPException, Header
from typing import Optional, List
import os
from sqlalchemy import select
from sqlalchemy.orm import Session
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from db import get_session
from models import Product

API_KEY = os.getenv("API_KEY")  # set this in Render
ALLOWED_ORIGINS = [o.strip() for o in os.getenv("ALLOWED_ORIGINS","").split(",") if o.strip()]

app = FastAPI(title="Amazon Cockpit API", version="0.2 (live-cors)")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS or ["*"],  # loosen during debug if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def require_api_key(x_api_key: Optional[str] = Header(None)) -> None:
    # If an API_KEY is configured, enforce it on all protected routes
    if API_KEY and x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

class ProductOut(BaseModel):
    id: int
    asin: Optional[str] = None
    title: Optional[str] = None
    price: Optional[float] = None

@app.get("/health")
def health() -> dict:
    return {"ok": True}

@app.get("/v1/products", dependencies=[Depends(require_api_key)], response_model=List[ProductOut])
def list_products(limit: int = 50, offset: int = 0):
    sess: Session = get_session()
    rows = sess.execute(select(Product).offset(offset).limit(limit)).scalars().all()
    return [ProductOut(id=r.id, asin=r.asin, title=r.title, price=r.price) for r in rows]

# --- Finance endpoints ---------------------------------------------------------
from datetime import datetime, timedelta
from pydantic import BaseModel
from models import FinanceDaily

class FinanceSummaryOut(BaseModel):
    revenue: float
    gross_profit: float
    net_profit: float
    acos_pct: float

class FinanceDailyOut(BaseModel):
    date: datetime
    units: int | None = 0
    revenue: float | None = 0.0
    cogs: float | None = 0.0
    fees: float | None = 0.0
    ad_spend: float | None = 0.0

@app.get("/v1/finance/summary", dependencies=[Depends(require_api_key)], response_model=FinanceSummaryOut)
def finance_summary():
    from sqlalchemy import func
    with get_session() as sess:
        rev = sess.query(func.coalesce(func.sum(FinanceDaily.revenue), 0.0)).scalar() or 0.0
        cogs = sess.query(func.coalesce(func.sum(FinanceDaily.cogs), 0.0)).scalar() or 0.0
        fees = sess.query(func.coalesce(func.sum(FinanceDaily.fees), 0.0)).scalar() or 0.0
        ads  = sess.query(func.coalesce(func.sum(FinanceDaily.ad_spend), 0.0)).scalar() or 0.0

    gross = rev - cogs - fees
    net   = gross - ads
    acos  = (ads / rev * 100.0) if rev > 1e-9 else 0.0
    return FinanceSummaryOut(revenue=rev, gross_profit=gross, net_profit=net, acos_pct=acos)

@app.get("/v1/finance/daily", dependencies=[Depends(require_api_key)], response_model=list[FinanceDailyOut])
def finance_daily(limit: int = 60):
    from sqlalchemy import select, desc
    with get_session() as sess:
        rows = sess.execute(
            select(FinanceDaily).order_by(desc(FinanceDaily.date)).limit(limit)
        ).scalars().all()
    # reverse so it charts left→right
    rows = list(reversed(rows))
    return [
        FinanceDailyOut(
            date=r.date, units=r.units, revenue=r.revenue, cogs=r.cogs,
            fees=r.fees, ad_spend=r.ad_spend
        ) for r in rows
    ]

# (Optional) demo seeder so you can see non-zero values immediately
@app.post("/ops/seed_finance_demo", dependencies=[Depends(require_api_key)])
def seed_finance_demo(days: int = 30):
    import random
    now = datetime.utcnow().date()
    with get_session() as sess:
        for i in range(days, 0, -1):
            d = datetime.combine(now - timedelta(days=i), datetime.min.time())
            base = 1000 + random.randint(-120, 120)  # base revenue
            ads  = max(0, base * random.uniform(0.07, 0.14))
            fees = max(0, base * random.uniform(0.10, 0.15))
            cogs = max(0, base * random.uniform(0.35, 0.45))
            units = int(base / 25)
            sess.add(FinanceDaily(
                date=d, units=units, revenue=base, cogs=cogs, fees=fees, ad_spend=ads
            ))
        sess.commit()
    return {"ok": True, "seeded_days": days}

