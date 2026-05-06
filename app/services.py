from datetime import datetime, timedelta, timezone
import random
import string

from sqlalchemy.orm import Session

from app import crud
from app.models import URL, ClickEvent

CHARACTERS = string.ascii_letters + string.digits


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
    short_code = custom_alias or generate_short_code()

    # Custom aliases are user-chosen, so we fail fast instead of silently changing them.
    if custom_alias and crud.get_url_by_short_code(db, custom_alias):
        raise ValueError("Custom alias is already taken")

    # Randomly generated aliases can be retried until we find a free code.
    while not custom_alias and crud.get_url_by_short_code(db, short_code):
        short_code = generate_short_code()

    expires_at = build_expiration_datetime(expires_in_days)
    url_entry = crud.create_url(
        db,
        short_code=short_code,
        original_url=original_url,
        expires_at=expires_at,
    )

    return {
        "short_code": url_entry.short_code,
        "short_url": f"{base_url}/{url_entry.short_code}",
        "original_url": url_entry.original_url,
        "expires_at": url_entry.expires_at,
    }


def get_original_url(db: Session, short_code: str) -> URL | None:
    return crud.get_url_by_short_code(db, short_code)


def is_url_expired(url_entry: URL) -> bool:
    # Links without an expiration date stay active indefinitely.
    return url_entry.expires_at is not None and url_entry.expires_at <= datetime.now(timezone.utc)


def record_click_event(
    db: Session,
    url_entry: URL,
    ip_address: str | None = None,
    user_agent: str | None = None,
    referrer: str | None = None,
) -> ClickEvent:
    return crud.create_click_event(
        db=db,
        url_id=url_entry.id,
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
