from db import get_engine
from models import Base

def init():
    engine = get_engine()
    Base.metadata.create_all(engine)
    print("✅ DB tables created (or already exist).")

if __name__ == "__main__":
    init()
