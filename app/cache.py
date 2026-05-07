import json
from datetime import datetime

try:
    import redis
    from redis.exceptions import RedisError
except ImportError:  # pragma: no cover - fallback keeps the app usable without Redis installed.
    redis = None
    RedisError = Exception

from app.config import REDIS_CACHE_TTL_SECONDS, REDIS_URL


def create_redis_client():
    if redis is None:
        return None

    try:
        return redis.Redis.from_url(REDIS_URL, decode_responses=True)
    except (RedisError, ValueError):
        # Invalid local Redis config should not stop the API from starting up.
        return None


redis_client = create_redis_client()


def build_url_cache_key(short_code: str) -> str:
    return f"url:{short_code}"


def get_cached_url(short_code: str) -> dict[str, str | int | None] | None:
    if redis_client is None:
        return None

    try:
        cached_value = redis_client.get(build_url_cache_key(short_code))
        if not cached_value:
            return None
        return json.loads(cached_value)
    except (RedisError, json.JSONDecodeError, TypeError, ValueError):
        # Cache failures should never break redirects; Postgres remains the source of truth.
        return None


def set_cached_url(url_data: dict[str, str | int | None]) -> None:
    if redis_client is None:
        return

    payload = dict(url_data)
    expires_at = payload.get("expires_at")
    if isinstance(expires_at, datetime):
        payload["expires_at"] = expires_at.isoformat()

    try:
        redis_client.setex(
            build_url_cache_key(str(payload["short_code"])),
            REDIS_CACHE_TTL_SECONDS,
            json.dumps(payload),
        )
    except (RedisError, TypeError, ValueError):
        # Cache writes are best-effort; a miss only costs a DB read on the next request.
        return
