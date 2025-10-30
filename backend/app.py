import os
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, Header, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from backend.db import engine, Base, SessionLocal
from backend.schemas import ProductOut, ProductIn
from backend.crud import list_products, create_product, list_compliance, list_research
from backend.debug_ads import check_ads_env, get_access_token, ping_ads_profiles, ping_ads_campaigns

APP_ENV = os.getenv("APP_ENV", "prod")
API_KEY = os.getenv("API_KEY", "")
ALLOWED_ORIGINS = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "http://localhost:8501").split(",") if o.strip()]

app = FastAPI(title="Vega Cockpit API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def get_db() -> AsyncSession:
    async with SessionLocal() as session:
        yield session

@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/health")
async def health(db: AsyncSession = Depends(get_db)):
    try:
        await db.execute(text("SELECT 1"))
        return {"ok": True, "env": APP_ENV, "db_ok": True}
    except Exception as e:
        return {"ok": False, "env": APP_ENV, "db_ok": False, "error": str(e)}

@app.get("/v1/products", response_model=List[ProductOut])
async def api_list_products(
    limit: int = Query(50, ge=1, le=500),
    q: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    return await list_products(db, limit=limit, q=q)

@app.post("/v1/products", response_model=ProductOut)
async def api_create_product(
    body: ProductIn,
    db: AsyncSession = Depends(get_db),
    x_api_key: str | None = Header(default=None)
):
    if API_KEY and x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return await create_product(db, **body.model_dump(exclude_none=True))

@app.get("/v1/compliance")
async def api_list_compliance(db: AsyncSession = Depends(get_db)):
    rows = await list_compliance(db)
    return [{k: getattr(r, k) for k in r.__dict__ if not k.startswith("_")} for r in rows]

@app.get("/v1/research/opportunities")
async def api_list_research(db: AsyncSession = Depends(get_db)):
    rows = await list_research(db)
    return [{k: getattr(r, k) for k in r.__dict__ if not k.startswith("_")} for r in rows]

@app.get("/debug/env")
async def debug_env():
    redacted, missing = check_ads_env()
    return {"env_present": redacted, "missing_keys": missing}

@app.get("/debug/ads")
async def debug_ads():
    redacted, missing = check_ads_env()
    if missing:
        return {"ok": False, "stage": "env", "missing": missing, "env": redacted}

    ok, token_or_err = get_access_token()
    if not ok:
        return {"ok": False, "stage": "token", "error": token_or_err, "env": redacted}

    status_profiles, body_profiles = ping_ads_profiles(token_or_err)
    if status_profiles != 200:
        return {"ok": False, "stage": "profiles", "status": status_profiles, "body": body_profiles}

    profile_id = os.getenv("ADS_PROFILE_ID") or os.getenv("AMZ_ADS_PROFILE_ID") or ""
    status_camps, body_camps = ping_ads_campaigns(token_or_err, profile_id)
    return {
        "ok": status_camps == 200,
        "stage": "campaigns" if status_camps == 200 else "campaigns_error",
        "status": status_camps,
        "body": body_camps,
    }

# --- one-time seed endpoint (safe to leave; no-op after first run) ---
@app.get("/seed")
async def seed(db: AsyncSession = Depends(get_db), x_api_key: str | None = Header(default=None)):
    if API_KEY and x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

    await db.execute(text("""
    CREATE TABLE IF NOT EXISTS products (
      id SERIAL PRIMARY KEY,
      asin TEXT UNIQUE,
      sku TEXT,
      title TEXT,
      brand TEXT,
      category TEXT,
      price NUMERIC,
      cost NUMERIC,
      inventory INT,
      reviews INT,
      stars NUMERIC,
      weight_kg NUMERIC,
      size TEXT,
      restricted_notes TEXT,
      updated_at TIMESTAMP DEFAULT NOW()
    );
    """))

    await db.execute(text("""
    INSERT INTO products (asin, sku, title, brand, price, cost, inventory, reviews, stars)
    VALUES
      ('TEST123','SKU-001','Sample Product A','Vega',19.99,7.50,25,120,4.3),
      ('TEST456','SKU-002','Sample Product B','Vega',12.49,5.10,60,45,4.0)
    ON CONFLICT (asin) DO NOTHING;
    """))

    await db.commit()
    return {"ok": True, "seeded": ["TEST123", "TEST456"]}
