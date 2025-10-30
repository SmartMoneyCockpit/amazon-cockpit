from pydantic import BaseModel
from typing import Optional

class ProductOut(BaseModel):
    id: int
    asin: Optional[str] = None
    sku: Optional[str] = None
    title: Optional[str] = None
    brand: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = None
    cost: Optional[float] = None
    inventory: Optional[int] = None
    reviews: Optional[int] = None
    stars: Optional[float] = None
    updated_at: Optional[str] = None
    class Config:
        from_attributes = True

class ProductIn(BaseModel):
    asin: Optional[str] = None
    sku: Optional[str] = None
    title: Optional[str] = None
    brand: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = None
    cost: Optional[float] = None
    inventory: Optional[int] = None
    reviews: Optional[int] = None
    stars: Optional[float] = None
