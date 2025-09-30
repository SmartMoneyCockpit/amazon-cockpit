from fastapi import FastAPI, Depends, HTTPException, Header
from typing import Optional, List
import os
from sqlalchemy import select
from sqlalchemy.orm import Session
from pydantic import BaseModel
from db import get_session
from models import Product

API_KEY = os.getenv("API_KEY")  # set this in Render

app = FastAPI(title="Amazon Cockpit API", version="0.1")

def require_api_key(x_api_key: Optional[str] = Header(None)) -> None:
    if not API_KEY:
        # If no API_KEY configured, allow only /health
        raise HTTPException(status_code=500, detail="API key not configured")
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

class ProductOut(BaseModel):
    id: int
    sku: str
    asin: Optional[str] = None
    title: Optional[str] = None
    marketplace: str

@app.get("/health")
def health() -> dict:
    return {"ok": True}

@app.get("/v1/products", dependencies=[Depends(require_api_key)], response_model=List[ProductOut])
def list_products(limit: int = 50, offset: int = 0):
    sess: Session = get_session()
    rows = sess.execute(select(Product).offset(offset).limit(limit)).scalars().all()
    return [ProductOut(id=r.id, sku=r.sku, asin=r.asin, title=r.title, marketplace=r.marketplace) for r in rows]
