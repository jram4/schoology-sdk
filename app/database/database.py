from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///schoology.db"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

def init_db():
    # pragma tuning for local SQLite
    with engine.connect() as conn:
        conn.exec_driver_sql("PRAGMA journal_mode=WAL;")
        conn.exec_driver_sql("PRAGMA synchronous=NORMAL;")
    from app.database import models  # ensure models registered
    Base.metadata.create_all(bind=engine)

# FastAPI deps pattern (used in /mcp route)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
