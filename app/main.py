from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from starlette.requests import Request

from app.config import APP_BASE_URL
from app.database import engine, Base
from app.dependencies import get_db
from app.schemas import URLRequest, URLResponse, URLStatsResponse
from app.services import (
    build_url_stats,
    create_short_url,
    get_original_url,
    is_url_expired,
    record_click_event,
)

# Create tables automatically for the current SQLAlchemy models.
Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.get("/")
def root():
    return {"message": "SnipURL is running"}


@app.post("/shorten", response_model=URLResponse)
def shorten_url(request: URLRequest, db: Session = Depends(get_db)):
    try:
        return create_short_url(
            db=db,
            original_url=str(request.url),
            base_url=APP_BASE_URL,
            custom_alias=request.custom_alias,
            expires_in_days=request.expires_in_days,
        )
    except ValueError as exc:
        # A taken custom alias is a client conflict, not a server failure.
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.get("/{short_code}/stats", response_model=URLStatsResponse)
def get_url_stats(short_code: str, db: Session = Depends(get_db)):
    url_entry = get_original_url(db, short_code)

    if not url_entry:
        raise HTTPException(status_code=404, detail="Short URL not found")

    return build_url_stats(db, url_entry, APP_BASE_URL)


@app.get("/{short_code}")
def redirect_to_url(short_code: str, request: Request, db: Session = Depends(get_db)):
    url_entry = get_original_url(db, short_code)

    if not url_entry:
        raise HTTPException(status_code=404, detail="Short URL not found")
    if is_url_expired(url_entry):
        # 410 signals that the short link existed before but is no longer valid.
        raise HTTPException(status_code=410, detail="Short URL has expired")

    # Capture basic request metadata now so analytics can show who clicked and from where.
    record_click_event(
        db=db,
        url_entry=url_entry,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        referrer=request.headers.get("referer"),
    )

    # A 307 redirect preserves the original HTTP method.
    return RedirectResponse(url=url_entry.original_url, status_code=307)
