import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

load_dotenv()

# We default to SQLite for local development but allow PostgreSQL override
# Example Postgres URL for EC2: postgresql+psycopg://user:password@localhost/paperlens
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./paperlens.db")

# SQLite requires specific args, PostgreSQL does not
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency for FastAPI endpoints
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
