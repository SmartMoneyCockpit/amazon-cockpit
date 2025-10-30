from typing import List, Optional
from sqlalchemy import select, desc, or_
from sqlalchemy.ext.asyncio import AsyncSession
from backend.models import Product, Compliance, ProductResearch

async def list_products(db: AsyncSession, limit:int=50, q:Optional[str]=None) -> List[Product]:
    limit = max(1, min(limit, 500))
    stmt = select(Product).order_by(desc(Product.updated_at)).limit(limit)
    if q:
        like = f"%{q}%"
        stmt = select(Product).where(or_(
            Product.asin.ilike(like),
            Product.sku.ilike(like),
            Product.title.ilike(like),
            Product.brand.ilike(like),
        )).order_by(desc(Product.updated_at)).limit(limit)
    return (await db.execute(stmt)).scalars().all()

async def create_product(db: AsyncSession, **kwargs) -> Product:
    p = Product(**kwargs)
    db.add(p)
    await db.commit()
    await db.refresh(p)
    return p

async def list_compliance(db: AsyncSession):
    stmt = select(Compliance).order_by(desc(Compliance.id)).limit(500)
    return (await db.execute(stmt)).scalars().all()

async def list_research(db: AsyncSession):
    stmt = select(ProductResearch).order_by(desc(ProductResearch.opportunity_score)).limit(500)
    return (await db.execute(stmt)).scalars().all()
