import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

DATABASE_URL = os.environ["DATABASE_URL"]

# Normalize postgres:// to postgresql+psycopg2://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg2://", 1)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    future=True,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

# Create tables on import if not present (simple bootstrap; for production use migrations)
try:
    from models import Base
    Base.metadata.create_all(bind=engine)
except Exception as e:
    # Avoid hard crash on circular import during tooling
    pass

@contextmanager
def get_session():
    sess = SessionLocal()
    try:
        yield sess
    finally:
        sess.close()
