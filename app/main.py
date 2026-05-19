from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from starlette.requests import Request

from app.config import APP_BASE_URL, RATE_LIMIT_REDIRECT, RATE_LIMIT_SHORTEN, RATE_LIMIT_STATS
from app.database import engine as default_engine, Base
from app.dependencies import get_db
from app.rate_limiter import check_rate_limit
from app.schemas import URLRequest, URLResponse, URLStatsResponse
from app.services import (
    build_url_stats,
    create_short_url,
    get_original_url,
    get_url_for_redirect,
    is_url_expired,
    record_click_event_in_background,
)

def create_app(*, engine=default_engine) -> FastAPI:
    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        # Create tables automatically for the current SQLAlchemy models.
        Base.metadata.create_all(bind=engine)
        yield

    app = FastAPI(lifespan=lifespan)

    # Frontend runs on a different port in development, so enable CORS.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    def enforce_rate_limit(request: Request, scope: str, limit: int) -> None:
        client_ip = request.client.host if request.client else "unknown"
        rate_limit_result = check_rate_limit(scope=scope, client_id=client_ip, limit=limit)

        if not rate_limit_result.allowed:
            raise HTTPException(
                status_code=429,
                detail=(
                    f"Rate limit exceeded for {scope}. "
                    f"Try again in {rate_limit_result.retry_after} seconds."
                ),
            )

    @app.get("/")
    def root():
        return {"message": "SnipURL is running"}


    @app.post("/shorten", response_model=URLResponse)
    def shorten_url(request: URLRequest, http_request: Request, db: Session = Depends(get_db)):
        # URL creation is the easiest endpoint to spam, so it gets the strictest limit.
        enforce_rate_limit(http_request, scope="shorten", limit=RATE_LIMIT_SHORTEN)

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
    def get_url_stats(short_code: str, request: Request, db: Session = Depends(get_db)):
        # Analytics endpoints are useful but can be scraped repeatedly, so we limit them too.
        enforce_rate_limit(request, scope="stats", limit=RATE_LIMIT_STATS)

        url_entry = get_original_url(db, short_code)

        if not url_entry:
            raise HTTPException(status_code=404, detail="Short URL not found")

        return build_url_stats(db, url_entry, APP_BASE_URL)

    @app.get("/{short_code}")
    def redirect_to_url(
        short_code: str,
        request: Request,
        background_tasks: BackgroundTasks,
        db: Session = Depends(get_db),
    ):
        # Redirect traffic is expected to be high, so this limit is intentionally looser.
        enforce_rate_limit(request, scope="redirect", limit=RATE_LIMIT_REDIRECT)

        url_data = get_url_for_redirect(db, short_code)

        if not url_data:
            raise HTTPException(status_code=404, detail="Short URL not found")
        if is_url_expired(url_data.expires_at):
            # 410 signals that the short link existed before but is no longer valid.
            raise HTTPException(status_code=410, detail="Short URL has expired")

        # Keep the redirect path light by logging analytics after the response is prepared.
        background_tasks.add_task(
            record_click_event_in_background,
            url_id=url_data.id,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            referrer=request.headers.get("referer"),
        )

        # A 307 redirect preserves the original HTTP method.
        return RedirectResponse(url=url_data.original_url, status_code=307)

    return app


app = create_app()
