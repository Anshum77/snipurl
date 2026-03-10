# SnipURL

A URL shortener built with FastAPI and PostgreSQL.

## Current Status: Phase 2 Complete

- FastAPI backend with auto-generated docs
- URL shortening with random 6-char Base62 codes
- HTTP 307 redirects
- PostgreSQL + SQLAlchemy for persistent storage
- Environment-based configuration

## Run Locally

```bash
# Clone the repo
git clone https://github.com/Anshum77/snipurl.git
cd snipurl

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1   # Windows

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
# Copy .env.example to .env and fill in your database URL
cp .env.example .env

# Start the server
uvicorn app.main:app --reload
```

Visit http://127.0.0.1:8000/docs to try it out.

## Tech Stack

- **Backend:** Python + FastAPI
- **Database:** PostgreSQL + SQLAlchemy
- **Server:** Uvicorn