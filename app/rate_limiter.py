from dataclasses import dataclass

from app.cache import RedisError, redis_client
from app.config import RATE_LIMIT_WINDOW_SECONDS

RATE_LIMIT_LUA_SCRIPT = """
local current_count = redis.call("INCR", KEYS[1])
if current_count == 1 then
    redis.call("EXPIRE", KEYS[1], ARGV[1])
end

local ttl = redis.call("TTL", KEYS[1])
return {current_count, ttl}
"""


@dataclass
class RateLimitResult:
    allowed: bool
    limit: int
    remaining: int
    retry_after: int


def build_rate_limit_key(scope: str, client_id: str) -> str:
    return f"rate_limit:{scope}:{client_id}"


def check_rate_limit(scope: str, client_id: str, limit: int) -> RateLimitResult:
    if redis_client is None:
        # If Redis is unavailable, do not break the API. We simply skip enforcement.
        return RateLimitResult(
            allowed=True,
            limit=limit,
            remaining=limit,
            retry_after=0,
        )

    key = build_rate_limit_key(scope, client_id)

    try:
        # Run counter increment and initial expiry in one atomic Redis operation.
        current_count, ttl = redis_client.eval(
            RATE_LIMIT_LUA_SCRIPT,
            1,
            key,
            RATE_LIMIT_WINDOW_SECONDS,
        )
        retry_after = max(ttl, 0) if ttl is not None else 0
        remaining = max(limit - current_count, 0)

        return RateLimitResult(
            allowed=current_count <= limit,
            limit=limit,
            remaining=remaining,
            retry_after=retry_after,
        )
    except RedisError:
        # Rate limiting is protective, but app availability still comes first.
        return RateLimitResult(
            allowed=True,
            limit=limit,
            remaining=limit,
            retry_after=0,
        )
