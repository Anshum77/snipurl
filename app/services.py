from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import random
import string

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app import crud
from app.cache import get_cached_url, set_cached_url
from app.models import URL, ClickEvent

CHARACTERS = string.ascii_letters + string.digits
MAX_SHORT_CODE_RETRIES = 5


@dataclass
class RedirectURLData:
    id: int
    short_code: str
    original_url: str
    expires_at: datetime | None


def generate_short_code(length: int = 6) -> str:
    return "".join(random.choices(CHARACTERS, k=length))


def build_expiration_datetime(expires_in_days: int | None) -> datetime | None:
    if expires_in_days is None:
        return None

    # Store expirations in UTC so comparisons stay consistent across environments.
    return datetime.now(timezone.utc) + timedelta(days=expires_in_days)


def create_short_url(
    db: Session,
    original_url: str,
    base_url: str,
    custom_alias: str | None = None,
    expires_in_days: int | None = None,
) -> dict[str, str | datetime | None]:
    expires_at = build_expiration_datetime(expires_in_days)
    url_entry = None

    # Let the database unique constraint make the final decision to avoid race conditions.
    for _ in range(MAX_SHORT_CODE_RETRIES):
        short_code = custom_alias or generate_short_code()
        try:
            url_entry = crud.create_url(
                db,
                short_code=short_code,
                original_url=original_url,
                expires_at=expires_at,
            )
            break
        except IntegrityError:
            if custom_alias:
                raise ValueError("Custom alias is already taken") from None

    if url_entry is None:
        raise ValueError("Could not generate a unique short code. Please try again.")

    set_cached_url(serialize_url_for_cache(url_entry))

    return {
        "short_code": url_entry.short_code,
        "short_url": f"{base_url}/{url_entry.short_code}",
        "original_url": url_entry.original_url,
        "expires_at": url_entry.expires_at,
    }


def serialize_url_for_cache(url_entry: URL) -> dict[str, str | int | None]:
    return {
        "id": url_entry.id,
        "short_code": url_entry.short_code,
        "original_url": url_entry.original_url,
        "expires_at": url_entry.expires_at,
    }


def build_redirect_url_data_from_db(url_entry: URL) -> RedirectURLData:
    return RedirectURLData(
        id=url_entry.id,
        short_code=url_entry.short_code,
        original_url=url_entry.original_url,
        expires_at=url_entry.expires_at,
    )


def build_redirect_url_data_from_cache(
    cached_url: dict[str, str | int | None],
) -> RedirectURLData:
    cached_expires_at = cached_url.get("expires_at")
    expires_at = None
    if isinstance(cached_expires_at, str):
        expires_at = datetime.fromisoformat(cached_expires_at)

    return RedirectURLData(
        id=int(cached_url["id"]),
        short_code=str(cached_url["short_code"]),
        original_url=str(cached_url["original_url"]),
        expires_at=expires_at,
    )


def get_original_url(db: Session, short_code: str) -> URL | None:
    return crud.get_url_by_short_code(db, short_code)


def get_url_for_redirect(db: Session, short_code: str) -> RedirectURLData | None:
    cached_url = get_cached_url(short_code)
    if cached_url:
        try:
            return build_redirect_url_data_from_cache(cached_url)
        except (KeyError, TypeError, ValueError):
            # Bad cache data should degrade to a DB read instead of breaking redirects.
            pass

    url_entry = crud.get_url_by_short_code(db, short_code)
    if not url_entry:
        return None

    # Populate Redis after a DB miss so later redirects can skip the lookup query.
    set_cached_url(serialize_url_for_cache(url_entry))
    return build_redirect_url_data_from_db(url_entry)


def is_url_expired(expires_at: datetime | None) -> bool:
    # Links without an expiration date stay active indefinitely.
    return expires_at is not None and expires_at <= datetime.now(timezone.utc)


def record_click_event(
    db: Session,
    url_id: int,
    ip_address: str | None = None,
    user_agent: str | None = None,
    referrer: str | None = None,
) -> ClickEvent:
    return crud.create_click_event(
        db=db,
        url_id=url_id,
        ip_address=ip_address,
        user_agent=user_agent,
        referrer=referrer,
    )


def build_url_stats(db: Session, url_entry: URL, base_url: str) -> dict[str, str | datetime | int | list[ClickEvent]]:
    # Keep the stats endpoint lightweight by returning a click count plus the most recent visits.
    recent_clicks = crud.get_recent_clicks_for_url(db, url_entry.id)

    return {
        "short_code": url_entry.short_code,
        "short_url": f"{base_url}/{url_entry.short_code}",
        "original_url": url_entry.original_url,
        "expires_at": url_entry.expires_at,
        "total_clicks": crud.get_click_count_for_url(db, url_entry.id),
        "recent_clicks": recent_clicks,
    }
