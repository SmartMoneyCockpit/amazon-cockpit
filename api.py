# api.py
from __future__ import annotations

from fastapi import FastAPI, Depends, HTTPException, Header, Query
from typing import Optional, List, Literal
import os
from datetime import datetime, timedelta

from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import select, func, asc, desc, text
from sqlalchemy.orm import Session

from db import get_session
from models import Product, FinanceDaily

# ────────────────────────────────────────────────────────────────────────────────
# Security / Config
# ────────────────────────────────────────────────────────────────────────────────
API_KEY = os.getenv("API_KEY")
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "")
ALLOWED_ORIGINS = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "").split(",") if o.strip()]

app = FastAPI(title="Amazon Cockpit API", version="0.4 (pagination)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

class CountOut(BaseModel):
    count: int

_SORTABLE_PRODUCT_COLUMNS = {
    "id": Product.id,
    "asin": Product.asin,
    "title": Product.title,
    "price": Product.price,
}

@app.get("/v1/products", dependencies=[Depends(require_api_key)], response_model=List[ProductOut])
def list_products(
    limit: int = Query(50, ge=1, le=2000),
    offset: int = Query(0, ge=0),
    sort_by: Literal["id", "asin", "title", "price"] = "id",
    sort_dir: Literal["asc", "desc"] = "asc",
):
    sort_col = _SORTABLE_PRODUCT_COLUMNS.get(sort_by, Product.id)
    order = asc(sort_col) if sort_dir == "asc" else desc(sort_col)
    with get_session() as sess:
        rows = (
            sess.execute(
                select(Product).order_by(order).offset(offset).limit(limit)
            )
            .scalars()
            .all()
        )
    return [ProductOut(id=r.id, asin=r.asin, title=r.title, price=r.price) for r in rows]

@app.get("/v1/products/count", dependencies=[Depends(require_api_key)], response_model=CountOut)
def products_count():
    with get_session() as sess:
        total = sess.query(func.count(Product.id)).scalar() or 0
    return CountOut(count=int(total))

# ────────────────────────────────────────────────────────────────────────────────
# Finance
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
    with get_session() as sess:
        rev  = sess.query(func.coalesce(func.sum(FinanceDaily.revenue), 0.0)).scalar() or 0.0
        cogs = sess.query(func.coalesce(func.sum(FinanceDaily.cogs), 0.0)).scalar() or 0.0
        fees = sess.query(func.coalesce(func.sum(FinanceDaily.fees), 0.0)).scalar() or 0.0
        ads  = sess.query(func.coalesce(func.sum(FinanceDaily.ad_spend), 0.0)).scalar() or 0.0
    gross = rev - cogs - fees
    net   = gross - ads
    acos  = (ads / rev * 100.0) if rev > 1e-9 else 0.0
    return FinanceSummaryOut(revenue=rev, gross_profit=gross, net_profit=net, acos_pct=acos)

@app.get("/v1/finance/daily", dependencies=[Depends(require_api_key)], response_model=List[FinanceDailyOut])
def finance_daily(
    limit: int = Query(60, ge=1, le=10000),
    offset: int = Query(0, ge=0),
    sort: Literal["asc", "desc"] = "desc",
):
    order = desc(FinanceDaily.date) if sort == "desc" else asc(FinanceDaily.date)
    with get_session() as sess:
        rows = (
            sess.execute(
                select(FinanceDaily).order_by(order).offset(offset).limit(limit)
            )
            .scalars()
            .all()
        )
    # If user asked for DESC, return oldest→newest for charts
    if sort == "desc":
        rows = list(reversed(rows))
    return [
        FinanceDailyOut(
            date=r.date,
            units=r.units,
            revenue=r.revenue,
            cogs=r.cogs,
            fees=r.fees,
            ad_spend=r.ad_spend,
        )
        for r in rows
    ]

@app.get("/v1/finance/daily/count", dependencies=[Depends(require_api_key)], response_model=CountOut)
def finance_daily_count():
    with get_session() as sess:
        total = sess.query(func.count(FinanceDaily.id)).scalar() or 0
    return CountOut(count=int(total))

# ────────────────────────────────────────────────────────────────────────────────
# Admin-only seed (keep in prod but behind ADMIN_TOKEN)
# ────────────────────────────────────────────────────────────────────────────────
@app.post(
    "/ops/seed_finance_demo",
    dependencies=[Depends(require_api_key), Depends(require_admin)],
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
            sess.add(
                FinanceDaily(
                    date=d,
                    units=units,
                    revenue=base,
                    cogs=cogs,
                    fees=fees,
                    ad_spend=ads,
                )
            )
        sess.commit()
    return {"ok": True, "seeded_days": days}

# ────────────────────────────────────────────────────────────────────────────────
# Amazon Ads live refresh + counts
# ────────────────────────────────────────────────────────────────────────────────
from services.amazon_ads_service import _db, _init_db, fetch_metrics, fetch_search_terms, fetch_placements

class AdsRefreshOut(BaseModel):
    ok: bool
    inserted_metrics: int
    inserted_search_terms: int
    inserted_placements: int
    window_start: str
    window_end: str

@app.post("/v1/ads/refresh", dependencies=[Depends(require_api_key)], response_model=AdsRefreshOut)
def ads_refresh(days: int = 30, types: Optional[str] = "SP,SB"):
    _init_db()
    from datetime import datetime, timedelta
    end = datetime.utcnow().date()
    start = end - timedelta(days=days)
    start_s, end_s = start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")
    inserted = {"metrics": 0, "search_terms": 0, "placements": 0}
    ad_types = [t.strip().upper() for t in (types or "SP,SB").split(",") if t.strip()]
    for t in ad_types:
        try:
            m = fetch_metrics(t, start_s, end_s) or []
            inserted["metrics"] += len(m)
        except Exception as e:
            print(f"[WARN] fetch_metrics {t}: {e}")
        try:
            s = fetch_search_terms(t, start_s, end_s) or []
            inserted["search_terms"] += len(s)
        except Exception as e:
            print(f"[WARN] fetch_search_terms {t}: {e}")
        try:
            p = fetch_placements(t, start_s, end_s) or []
            inserted["placements"] += len(p)
        except Exception as e:
            print(f"[WARN] fetch_placements {t}: {e}")
    return AdsRefreshOut(
        ok=True,
        inserted_metrics=inserted["metrics"],
        inserted_search_terms=inserted["search_terms"],
        inserted_placements=inserted["placements"],
        window_start=start_s,
        window_end=end_s,
    )

class AdsCountOut(BaseModel):
    metrics: int
    search_terms: int
    placements: int

@app.get("/v1/ads/metrics/count", dependencies=[Depends(require_api_key)], response_model=AdsCountOut)
def ads_metrics_count():
    _init_db()
    con = _db()
    cur = con.cursor()
    def _count(table):
        try:
            return cur.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0] or 0
        except Exception:
            return 0
    return AdsCountOut(
        metrics=_count("metrics"),
        search_terms=_count("search_terms"),
        placements=_count("placements"),
    )
