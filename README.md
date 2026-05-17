# SnipURL — FastAPI URL Shortener

SnipURL is a URL shortener API built with FastAPI, PostgreSQL (SQLAlchemy ORM), and Redis (cache + rate limiting). It tracks click events and exposes rich analytics (user-agent parsing + optional offline GeoIP enrichment).

## Highlights

- Create short URLs with secure random codes or custom aliases
- Optional link expiration
- HTTP `307` redirects
- Redis cache-aside for short-code lookups
- Redis-backed fixed-window rate limiting (per IP)
- Click tracking via FastAPI background tasks
- Stats endpoint with enriched analytics (referrers/country/browser/os/device buckets)
- Pytest suite covering endpoints, cache behaviour, and rate limiting

## API Endpoints

- `POST /shorten`
- `GET /{short_code}`
- `GET /{short_code}/stats`

## Project Structure

```text
app/
|-- main.py           # FastAPI routes
|-- config.py         # environment configuration (dotenv)
|-- database.py       # SQLAlchemy engine + session
|-- models.py         # ORM models (URL, ClickEvent)
|-- schemas.py        # Pydantic request/response models
|-- crud.py           # DB queries
|-- services.py       # business logic + analytics aggregation
|-- cache.py          # Redis cache helpers (URL lookups)
|-- rate_limiter.py   # Redis fixed-window rate limiting
|-- analytics.py      # user-agent + referrer parsing helpers
`-- geoip.py          # offline GeoIP enrichment (optional)
tests/
|-- conftest.py       # SQLite test DB, fixtures, DB cleanup
|-- test_endpoints.py # end-to-end API tests
`-- test_cache_mocking.py  # cache hit/miss and Redis failure tests
```

## Run Locally

### Prerequisites

- Python 3.10+
- PostgreSQL running locally
- Redis running locally (optional; the API degrades gracefully without it)

### Setup

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

### Configure `.env`

Minimum required:

- `DATABASE_URL` (PostgreSQL connection string)

Common local defaults:

- `APP_BASE_URL=http://127.0.0.1:8000`
- `REDIS_URL=redis://localhost:6379/0`

### Start Server

```powershell
uvicorn app.main:app --reload
```

Open Swagger UI at `http://127.0.0.1:8000/docs`.

### Run Tests

```powershell
pip install -r requirements-dev.txt
pytest
```

Tests use SQLite in-memory and require no running PostgreSQL or Redis instance.

## GeoIP Setup (Optional)

GeoIP enrichment uses an offline IP2Location LITE DB11 `.BIN` file (no external API calls).

1. Download IP2Location LITE DB11 (`.BIN`) from ip2location.com.
2. Set `GEOIP_DB_PATH` in `.env` to the full path of the `.BIN` file.

If `GEOIP_DB_PATH` is not set (or the file is missing), geo fields return `null` and the API continues to work.

## Tech Stack

- API: FastAPI, Pydantic
- Database: PostgreSQL, SQLAlchemy
- Cache/Rate limiting: Redis
- Analytics enrichment: `user-agents` (UA parsing), IP2Location LITE (offline GeoIP)
- Testing: pytest, httpx, pytest-mock (SQLite in-memory)
- Server: Uvicorn

## Design Notes

- Tables are created with `Base.metadata.create_all()` for simplicity; Alembic migrations are the natural next step for production workflows.
- Redirect click logging uses FastAPI `BackgroundTasks` to keep the redirect hot-path fast (not a durable queue).
- Rate limiting uses a Lua script to make the Redis `INCR` + `EXPIRE` sequence atomic, avoiding the key-without-TTL bug common in naive fixed-window implementations.

## Planned Next

- Docker setup