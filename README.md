# SnipURL

A URL shortener API built with FastAPI, PostgreSQL, and SQLAlchemy.

## Current Status

SnipURL currently supports:

- short URL creation with random generated codes
- custom aliases such as `/portfolio`
- optional link expiration
- HTTP `307` redirects
- Redis caching for short-code lookups
- Redis-backed per-IP rate limiting
- background-task click event tracking for every redirect
- stats endpoint with total clicks and recent visits
- PostgreSQL persistence with SQLAlchemy ORM
- modular FastAPI backend structure

## Features

- `POST /shorten` creates a short URL for a long URL
- optional `custom_alias` support for human-readable links
- optional `expires_in_days` support for temporary links
- Redis cache-aside lookup for redirect performance
- Redis-backed fixed-window rate limiting for key endpoints
- click logging moved off the redirect hot path with FastAPI background tasks
- `GET /{short_code}` redirects to the original URL
- `GET /{short_code}/stats` returns click analytics for a short URL
- request validation using Pydantic
- environment-based configuration with `.env`

## Project Structure

```text
app/
|-- config.py         # environment variables
|-- cache.py          # Redis cache helpers
|-- crud.py           # database queries
|-- database.py       # engine, session, base
|-- dependencies.py   # shared FastAPI dependencies
|-- main.py           # routes and app startup
|-- models.py         # SQLAlchemy models
|-- schemas.py        # request/response schemas
`-- services.py       # business logic
```

## Run Locally

```powershell
# Clone the repo
git clone https://github.com/Anshum77/snipurl.git
cd snipurl

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1   # Windows

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
# Copy .env.example to .env
Copy-Item .env.example .env

# Update .env with your local values:
# DATABASE_URL=postgresql://username:password@localhost:5432/snipurl
# APP_BASE_URL=http://127.0.0.1:8000
# REDIS_URL=redis://localhost:6379/0
# REDIS_CACHE_TTL_SECONDS=3600
# RATE_LIMIT_WINDOW_SECONDS=60
# RATE_LIMIT_SHORTEN=5
# RATE_LIMIT_STATS=30
# RATE_LIMIT_REDIRECT=120

# Start the server
uvicorn app.main:app --reload
```

Visit:

- `http://127.0.0.1:8000/docs` for Swagger UI
- `http://127.0.0.1:8000/redoc` for ReDoc

## Example Request

Create a short URL:

```json
{
  "url": "https://github.com",
  "custom_alias": "portfolio",
  "expires_in_days": 7
}
```

Example response:

```json
{
  "short_code": "portfolio",
  "short_url": "http://127.0.0.1:8000/portfolio",
  "original_url": "https://github.com/",
  "expires_at": "2026-05-14T12:00:00+00:00"
}
```

Fetch stats:

```text
GET /portfolio/stats
```

## Tech Stack

- Backend: Python, FastAPI
- Database: PostgreSQL, SQLAlchemy
- Cache: Redis
- Rate limiting: Redis fixed-window counters
- Validation: Pydantic
- Server: Uvicorn

## Rate Limiting

- `POST /shorten` uses the strictest limit because URL creation is the easiest endpoint to abuse.
- `GET /{short_code}/stats` uses a moderate limit because analytics endpoints can be scraped repeatedly.
- `GET /{short_code}` uses a looser limit because redirects are expected to receive the highest legitimate traffic.

Current default policy:

- `POST /shorten`: 5 requests per 60 seconds per IP
- `GET /{short_code}/stats`: 30 requests per 60 seconds per IP
- `GET /{short_code}`: 120 requests per 60 seconds per IP

Current implementation note:

- The project currently uses a Redis-backed fixed-window approach because it is simple, fast, and easy to reason about.
- A known limitation of fixed-window rate limiting is the boundary burst problem: a client can send requests at the very end of one window and again at the start of the next window, effectively creating a short burst that exceeds the intended smooth rate.
- To address that in a future version, the rate limiter can be upgraded to a sliding-window or token-bucket approach, both of which provide smoother and fairer request control under bursty traffic.

## Click Tracking Tradeoff

- Click events are currently recorded with FastAPI `BackgroundTasks` so the redirect response does not wait on the analytics write.
- This improves redirect latency because the hot path no longer blocks on a synchronous database insert for every visit.
- The tradeoff is that `BackgroundTasks` is not a durable queue. If the application process stops at the wrong moment, an in-flight click event can be lost.
- For this project stage, that is a reasonable balance between performance improvement and implementation simplicity.
- In a more production-grade version, click events could be pushed to a durable queue or worker system for stronger delivery guarantees.

## Current Scope

Implemented:

- URL shortening
- custom aliases
- link expiration
- Redis caching
- rate limiting
- click tracking
- basic analytics endpoint

Planned next:

- richer analytics
- Docker setup
- automated tests
