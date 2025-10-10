# models.py
from __future__ import annotations
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Text, Float, DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


# ────────────────────────────────────────────────────────────────────────────────
# Base class
# ────────────────────────────────────────────────────────────────────────────────
class Base(DeclarativeBase):
    pass


# ────────────────────────────────────────────────────────────────────────────────
# Product table
# ────────────────────────────────────────────────────────────────────────────────
class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    asin: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    title: Mapped[str] = mapped_column(Text)
    price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )


# ────────────────────────────────────────────────────────────────────────────────
# FinanceDaily table (for /v1/finance endpoints)
# ────────────────────────────────────────────────────────────────────────────────
class FinanceDaily(Base):
    __tablename__ = "finance_daily"

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)

    units: Mapped[Optional[int]] = mapped_column(nullable=True)
    revenue: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    cogs: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    fees: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    ad_spend: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
