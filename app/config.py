import os
from dotenv import load_dotenv

# Load local environment variables before any settings are read.
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is not set. Configure it in your environment or in a local .env file "
        "(see .env.example)."
    )
APP_BASE_URL = os.getenv("APP_BASE_URL", "http://127.0.0.1:8000")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
REDIS_CACHE_TTL_SECONDS = int(os.getenv("REDIS_CACHE_TTL_SECONDS", "3600"))
RATE_LIMIT_WINDOW_SECONDS = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60"))
RATE_LIMIT_SHORTEN = int(os.getenv("RATE_LIMIT_SHORTEN", "5"))
RATE_LIMIT_STATS = int(os.getenv("RATE_LIMIT_STATS", "30"))
RATE_LIMIT_REDIRECT = int(os.getenv("RATE_LIMIT_REDIRECT", "120"))
GEOIP_DB_PATH = os.getenv("GEOIP_DB_PATH") or None
