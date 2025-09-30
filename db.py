import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL")

def get_engine():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL is not set. Add it in Render → Web Service → Settings → Environment.")
    return create_engine(DATABASE_URL, pool_pre_ping=True)

def get_session():
    engine = get_engine()
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)()

def health_check():
    eng = get_engine()
    with eng.connect() as conn:
        result = conn.execute(text("select 1 as ok"))
        return result.scalar() == 1
