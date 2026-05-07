import os
from dotenv import load_dotenv

# Load local environment variables before any settings are read.
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
APP_BASE_URL = os.getenv("APP_BASE_URL", "http://127.0.0.1:8000")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
REDIS_CACHE_TTL_SECONDS = int(os.getenv("REDIS_CACHE_TTL_SECONDS", "3600"))
