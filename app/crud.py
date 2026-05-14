from datetime import datetime

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import URL, ClickEvent


def get_url_by_short_code(db: Session, short_code: str) -> URL | None:
    return db.query(URL).filter(URL.short_code == short_code).first()


def create_url(
    db: Session,
    short_code: str,
    original_url: str,
    expires_at: datetime | None = None,
) -> URL:
    new_url = URL(
        short_code=short_code,
        original_url=original_url,
        expires_at=expires_at,
    )
    db.add(new_url)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise
    db.refresh(new_url)
    return new_url


def create_click_event(
    db: Session,
    url_id: int,
    ip_address: str | None = None,
    user_agent: str | None = None,
    referrer: str | None = None,
) -> ClickEvent:
    new_click_event = ClickEvent(
        url_id=url_id,
        ip_address=ip_address,
        user_agent=user_agent,
        referrer=referrer,
    )
    db.add(new_click_event)
    db.commit()
    db.refresh(new_click_event)
    return new_click_event


def get_click_count_for_url(db: Session, url_id: int) -> int:
    return db.query(func.count(ClickEvent.id)).filter(ClickEvent.url_id == url_id).scalar() or 0


def get_recent_clicks_for_url(
    db: Session,
    url_id: int,
    limit: int = 10,
) -> list[ClickEvent]:
    return (
        db.query(ClickEvent)
        .filter(ClickEvent.url_id == url_id)
        .order_by(ClickEvent.clicked_at.desc())
        .limit(limit)
        .all()
    )
