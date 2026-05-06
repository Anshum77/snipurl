# SnipURL

A URL shortener API built with FastAPI, PostgreSQL, and SQLAlchemy.

## Current Status

SnipURL currently supports:

- short URL creation with random generated codes
- custom aliases such as `/portfolio`
- optional link expiration
- HTTP `307` redirects
- click event tracking for every redirect
- stats endpoint with total clicks and recent visits
- PostgreSQL persistence with SQLAlchemy ORM
- modular FastAPI backend structure

## Features

- `POST /shorten` creates a short URL for a long URL
- optional `custom_alias` support for human-readable links
- optional `expires_in_days` support for temporary links
- `GET /{short_code}` redirects to the original URL
- `GET /{short_code}/stats` returns click analytics for a short URL
- request validation using Pydantic
- environment-based configuration with `.env`

## Project Structure

```text
app/
|-- config.py         # environment variables
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
- Validation: Pydantic
- Server: Uvicorn

## Current Scope

Implemented:

- URL shortening
- custom aliases
- link expiration
- click tracking
- basic analytics endpoint

Planned next:

- Redis caching
- rate limiting
- richer analytics
- Docker setup
- automated tests
