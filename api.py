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
