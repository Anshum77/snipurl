from datetime import datetime, timezone


def _create_url(db, short_code: str, original_url: str):
    from app import crud

    return crud.create_url(
        db,
        short_code=short_code,
        original_url=original_url,
        expires_at=None,
    )


def test_redirect_uses_cache_hit(mocker, db_session):
    from app.services import get_url_for_redirect

    url_entry = _create_url(
        db_session, short_code="cached1", original_url="https://example.com/cache-hit"
    )

    mock_get_cached = mocker.patch(
        "app.services.get_cached_url",
        return_value={
            "id": url_entry.id,
            "short_code": "cached1",
            "original_url": "https://example.com/cache-hit",
            "expires_at": datetime.now(timezone.utc).isoformat(),
        },
    )
    mock_db_lookup = mocker.patch("app.services.crud.get_url_by_short_code")

    url_data = get_url_for_redirect(db_session, "cached1")
    assert url_data is not None
    assert url_data.original_url == "https://example.com/cache-hit"

    mock_get_cached.assert_called_once()
    mock_db_lookup.assert_not_called()


def test_corrupted_cache_falls_back_to_db(mocker, db_session):
    from app.services import get_url_for_redirect

    _create_url(db_session, short_code="cached2", original_url="https://example.com/db-fallback")

    mocker.patch("app.services.get_cached_url", return_value={"bad": "data"})
    mock_db_lookup = mocker.patch(
        "app.services.crud.get_url_by_short_code",
        wraps=__import__("app.crud", fromlist=["get_url_by_short_code"]).get_url_by_short_code,
    )

    url_data = get_url_for_redirect(db_session, "cached2")
    assert url_data is not None
    assert url_data.original_url == "https://example.com/db-fallback"
    assert mock_db_lookup.call_count == 1
    

def test_redis_exception_does_not_break_lookup(mocker):
    import app.cache as cache

    class _FakeRedis:
        def get(self, _key):
            raise cache.RedisError("boom")

    mocker.patch.object(cache, "redis_client", _FakeRedis())

    # Should return None (graceful) rather than raise.
    assert cache.get_cached_url("anything") is None
