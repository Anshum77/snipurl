from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, HttpUrl
from sqlalchemy.orm import Session
import string
import random

from app.database import engine, Base, SessionLocal
from app.models import URL

Base.metadata.create_all(bind=engine)

app = FastAPI()

CHARACTERS = string.ascii_letters + string.digits


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def generate_short_code(length: int = 6) -> str:
    return "".join(random.choices(CHARACTERS, k=length))


class URLRequest(BaseModel):
    url: HttpUrl


@app.get("/")
def root():
    return {"message": "SnipURL is running"}


@app.post("/shorten")
def shorten_url(request: URLRequest, db: Session = Depends(get_db)):
    short_code = generate_short_code()

    while db.query(URL).filter(URL.short_code == short_code).first():
        short_code = generate_short_code()

    new_url = URL(short_code=short_code, original_url=str(request.url))
    db.add(new_url)
    db.commit()

    return {
        "short_code": short_code,
        "short_url": f"http://127.0.0.1:8000/{short_code}",
        "original_url": str(request.url),
    }


@app.get("/{short_code}")
def redirect_to_url(short_code: str, db: Session = Depends(get_db)):
    url_entry = db.query(URL).filter(URL.short_code == short_code).first()

    if not url_entry:
        raise HTTPException(status_code=404, detail="Short URL not found")

    return RedirectResponse(url=url_entry.original_url, status_code=307)
