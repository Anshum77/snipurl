from datetime import datetime, timedelta, timezone


def test_root_health(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "SnipURL is running"


def test_shorten_and_redirect_and_stats(client):
    shorten_response = client.post(
        "/shorten",
        json={"url": "https://example.com"},
    )
    assert shorten_response.status_code == 200
    payload = shorten_response.json()
    assert payload["short_code"]
    assert payload["short_url"].endswith(f'/{payload["short_code"]}')
    assert payload["original_url"] == "https://example.com/"

    redirect_response = client.get(
        f'/{payload["short_code"]}',
        headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0"},
        follow_redirects=False,
    )
    assert redirect_response.status_code == 307
    assert redirect_response.headers["location"] == "https://example.com/"

    stats_response = client.get(f'/{payload["short_code"]}/stats')
    assert stats_response.status_code == 200
    stats = stats_response.json()
    assert stats["short_code"] == payload["short_code"]
    assert stats["total_clicks"] >= 1
    assert len(stats["recent_clicks"]) >= 1

    # Enriched analytics should be present (geo may be null).
    assert stats["analytics"] is not None
    assert stats["recent_clicks_enriched"]
    enriched_click = stats["recent_clicks_enriched"][0]
    assert "ua" in enriched_click


def test_custom_alias_is_case_insensitive(client):
    r1 = client.post(
        "/shorten",
        json={"url": "https://example.com/a", "custom_alias": "Portfolio"},
    )
    assert r1.status_code == 200
    assert r1.json()["short_code"] == "portfolio"

    r2 = client.post(
        "/shorten",
        json={"url": "https://example.com/b", "custom_alias": "portfolio"},
    )
    assert r2.status_code == 409


def test_expired_link_returns_410(client):
    r = client.post(
        "/shorten",
        json={"url": "https://example.com/exp", "expires_in_days": 1},
    )
    assert r.status_code == 200
    short_code = r.json()["short_code"]

    from app.database import SessionLocal
    from app.models import URL

    db = SessionLocal()
    try:
        url_entry = db.query(URL).filter(URL.short_code == short_code).first()
        assert url_entry is not None
        url_entry.expires_at = datetime.now(timezone.utc) - timedelta(days=1)
        db.commit()
    finally:
        db.close()

    redirect_response = client.get(f"/{short_code}", follow_redirects=False)
    assert redirect_response.status_code == 410
