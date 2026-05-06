from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.config import DATABASE_URL

# Shared SQLAlchemy engine used by the whole application.
engine = create_engine(DATABASE_URL)

# Factory for creating one database session per request.
SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    # All ORM models inherit from this base class.
    pass
