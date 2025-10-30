from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, Text, Numeric, Date, TIMESTAMP, func
from backend.db import Base

class Setting(Base):
    __tablename__ = "settings"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    key: Mapped[str] = mapped_column(Text, unique=True)
    value: Mapped[str | None] = mapped_column(Text)
    updated_at: Mapped[str] = mapped_column(TIMESTAMP, server_default=func.now())

class Product(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    asin: Mapped[str | None] = mapped_column(Text, unique=True)
    sku: Mapped[str | None] = mapped_column(Text)
    title: Mapped[str | None] = mapped_column(Text)
    brand: Mapped[str | None] = mapped_column(Text)
    category: Mapped[str | None] = mapped_column(Text)
    price: Mapped[float | None] = mapped_column(Numeric)
    cost: Mapped[float | None] = mapped_column(Numeric)
    inventory: Mapped[int | None] = mapped_column(Integer)
    reviews: Mapped[int | None] = mapped_column(Integer)
    stars: Mapped[float | None] = mapped_column(Numeric)
    updated_at: Mapped[str] = mapped_column(TIMESTAMP, server_default=func.now())

class AdsCampaign(Base):
    __tablename__ = "ads_campaigns"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    campaign_id: Mapped[str | None] = mapped_column(Text)
    name: Mapped[str | None] = mapped_column(Text)
    impressions: Mapped[int | None] = mapped_column(Integer)
    clicks: Mapped[int | None] = mapped_column(Integer)
    spend: Mapped[float | None] = mapped_column(Numeric)
    orders: Mapped[int | None] = mapped_column(Integer)
    acos: Mapped[float | None] = mapped_column(Numeric)
    roas: Mapped[float | None] = mapped_column(Numeric)
    created_at: Mapped[str] = mapped_column(TIMESTAMP, server_default=func.now())

class Compliance(Base):
    __tablename__ = "compliance"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    asin: Mapped[str | None] = mapped_column(Text)
    doc_type: Mapped[str | None] = mapped_column(Text)
    issuer: Mapped[str | None] = mapped_column(Text)
    issued_on: Mapped[str | None] = mapped_column(Date)
    expires_on: Mapped[str | None] = mapped_column(Date)
    link: Mapped[str | None] = mapped_column(Text)
    notes: Mapped[str | None] = mapped_column(Text)

class ProductResearch(Base):
    __tablename__ = "product_research"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    asin: Mapped[str | None] = mapped_column(Text)
    competitor_title: Mapped[str | None] = mapped_column(Text)
    price: Mapped[float | None] = mapped_column(Numeric)
    reviews: Mapped[int | None] = mapped_column(Integer)
    stars: Mapped[float | None] = mapped_column(Numeric)
    size: Mapped[str | None] = mapped_column(Text)
    restricted_notes: Mapped[str | None] = mapped_column(Text)
    opportunity_score: Mapped[float | None] = mapped_column(Numeric)
    updated_at: Mapped[str] = mapped_column(TIMESTAMP, server_default=func.now())
