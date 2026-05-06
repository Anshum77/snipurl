from app.database import SessionLocal


def get_db():
    # FastAPI uses this dependency to open and close one DB session per request.
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
