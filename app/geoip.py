from __future__ import annotations

from functools import lru_cache
import ipaddress
import os
from typing import Any

from app.config import GEOIP_DB_PATH
from app.schemas import ClickEventGeoInfo

try:
    from ip2location.database import IP2Location as IP2LocationDB
except ImportError:  # pragma: no cover - keeps app usable without GeoIP deps installed.
    IP2LocationDB = None


def _is_public_ip(ip_string: str) -> bool:
    try:
        ip = ipaddress.ip_address(ip_string)
    except ValueError:
        return False

    return not (
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_multicast
        or ip.is_reserved
        or ip.is_unspecified
    )


@lru_cache(maxsize=1)
def _get_geoip_db() -> Any:
    if IP2LocationDB is None:
        return None

    if not GEOIP_DB_PATH:
        return None

    if not os.path.isfile(GEOIP_DB_PATH):
        return None

    db = IP2LocationDB()
    db.open(GEOIP_DB_PATH)
    return db


def lookup_geo(ip_address: str | None) -> ClickEventGeoInfo | None:
    if not ip_address:
        return None

    if not _is_public_ip(ip_address):
        return None

    db = _get_geoip_db()
    if db is None:
        return None

    try:
        record = db.get_all(ip_address)
    except Exception:
        return None

    if not record:
        return None

    try:
        latitude = float(record.latitude) if record.latitude not in (None, "", "-") else None
    except (TypeError, ValueError):
        latitude = None
    try:
        longitude = float(record.longitude) if record.longitude not in (None, "", "-") else None
    except (TypeError, ValueError):
        longitude = None

    country = getattr(record, "country_long", None) or getattr(record, "country_short", None) or None

    return ClickEventGeoInfo(
        country=country,
        region=getattr(record, "region", None) or None,
        city=getattr(record, "city", None) or None,
        latitude=latitude,
        longitude=longitude,
    )
