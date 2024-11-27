# database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

DATABASE_URL = "sqlite:///./users.db"

# Create engine
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}, echo=False
)

# Create sessionmaker
SessionLocal = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
