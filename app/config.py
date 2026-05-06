import os
from dotenv import load_dotenv

# Load local environment variables before any settings are read.
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
APP_BASE_URL = os.getenv("APP_BASE_URL", "http://127.0.0.1:8000")
