from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Integer, DateTime, func, ForeignKey, Float
from typing import Optional

class Base(DeclarativeBase):
    pass

class Product(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sku: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    asin: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, index=True)
    title: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    marketplace: Mapped[str] = mapped_column(String(8), default="US")
    created_at: Mapped = mapped_column(DateTime(timezone=True), server_default=func.now())

class Keyword(Base):
    __tablename__ = "keywords"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    term: Mapped[str] = mapped_column(String(128), index=True)
    volume: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    difficulty: Mapped[Optional[Float]] = mapped_column(nullable=True)
    created_at: Mapped = mapped_column(DateTime(timezone=True), server_default=func.now())
