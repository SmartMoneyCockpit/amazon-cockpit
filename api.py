from fastapi import FastAPI, Depends, HTTPException, Header
from typing import Optional, List
import os
from sqlalchemy import select
from sqlalchemy.orm import Session
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta

from db import get_session
from models import Product, FinanceDaily

# ────────────────────────────────────────────────────────────────────────────────
# Security configuration
# ────────────────────────────────────────────────────────────────────────────────
API_KEY = os.getenv("API_KEY")
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "")  # set this in Render for the API service
ALLOWED_ORIGINS = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "").split(",") if o.strip()]

app = FastAPI(title="Amazon Cockpit API", version="0.3 (finance-live)")

# ────────────────────────────────────────────────────────────────────────────────
# Middleware (CORS)
# ────────────────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ────────────────────────────────────────────────────────────────────────────────
# Auth helpers
# ────────────────────────────────────────────────────────────────────────────────
def require_api_key(x_api_key: Optional[str] = Header(None)) -> None:
    if API_KEY and x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

def require_admin(x_admin_token: Optional[str] = Header(None)) -> None:
    if not ADMIN_TOKEN or x_admin_token != ADMIN_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")

# ────────────────────────────────────────────────────────────────────────────────
# Health
# ────────────────────────────────────────────────────────────────────────────────
@app.get("/health")
def health() -> dict:
    return {"ok": True}

# ────────────────────────────────────────────────────────────────────────────────
# Products
# ────────────────────────────────────────────────────────────────────────────────
class ProductOut(BaseModel):
    id: int
    asin: Optional[str] = None
    title: Optional[str] = None
    price: Optional[float] = None

@app.get("/v1/products", dependencies=[Depends(require_api_key)], response_model=List[ProductOut])
def list_products(limit: int = 50, offset: int = 0):
    with get_session() as sess:
        rows = sess.execute(select(Product).offset(offset).limit(limit)).scalars().all()
    return [ProductOut(id=r.id, asin=r.asin, title=r.title, price=r.price) for r in rows]

# ────────────────────────────────────────────────────────────────────────────────
# Finance endpoints
# ────────────────────────────────────────────────────────────────────────────────
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

@app.get("/v1/finance/daily", dependencies=[Depends(require_api_key)], response_model=List[FinanceDailyOut])
def finance_daily(limit: int = 60, offset: int = 0, sort: str = "desc"):
    from sqlalchemy import select, desc, asc
    order = desc(FinanceDaily.date) if sort.lower() == "desc" else asc(FinanceDaily.date)
    with get_session() as sess:
        rows = sess.execute(
            select(FinanceDaily).order_by(order).offset(offset).limit(limit)
        ).scalars().all()
    if sort.lower() == "desc":
        rows = list(reversed(rows))  # show oldest→newest
    return [
        FinanceDailyOut(
            date=r.date, units=r.units, revenue=r.revenue,
            cogs=r.cogs, fees=r.fees, ad_spend=r.ad_spend
        ) for r in rows
    ]

# ────────────────────────────────────────────────────────────────────────────────
# Demo seeding (admin protected)
# ────────────────────────────────────────────────────────────────────────────────
@app.post(
    "/ops/seed_finance_demo",
    dependencies=[Depends(require_api_key), Depends(require_admin)]
)
def seed_finance_demo(days: int = 30):
    """Populate demo finance data (requires both API_KEY and ADMIN_TOKEN)."""
    import random
    now = datetime.utcnow().date()
    with get_session() as sess:
        for i in range(days, 0, -1):
            d = datetime.combine(now - timedelta(days=i), datetime.min.time())
            base = 1000 + random.randint(-120, 120)
            ads  = max(0, base * random.uniform(0.07, 0.14))
            fees = max(0, base * random.uniform(0.10, 0.15))
            cogs = max(0, base * random.uniform(0.35, 0.45))
            units = int(base / 25)
            sess.add(FinanceDaily(
                date=d, units=units, revenue=base,
                cogs=cogs, fees=fees, ad_spend=ads
            ))
        sess.commit()
    return {"ok": True, "seeded_days": days}
