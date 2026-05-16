from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator


class URLRequest(BaseModel):
    url: HttpUrl
    custom_alias: str | None = Field(default=None)
    expires_in_days: int | None = Field(default=None, ge=1, le=365)

    @field_validator("custom_alias")
    @classmethod
    def normalize_custom_alias(cls, value: str | None) -> str | None:
        if value is None:
            return value

        # Trim whitespace and canonicalize case so aliases are unique regardless of input casing.
        normalized_value = value.strip().lower()
        if not 3 <= len(normalized_value) <= 10:
            raise ValueError("custom_alias must be between 3 and 10 characters long")
        if not normalized_value.replace("-", "").replace("_", "").isalnum():
            raise ValueError(
                "custom_alias can only contain letters, numbers, hyphens, and underscores"
            )
        return normalized_value


class URLResponse(BaseModel):
    # Allow FastAPI to serialize directly from the SQLAlchemy URL object when needed.
    model_config = ConfigDict(from_attributes=True)

    short_code: str
    short_url: str
    original_url: str
    expires_at: datetime | None


class ClickEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    clicked_at: datetime | None
    ip_address: str | None
    user_agent: str | None
    referrer: str | None


class ClickEventUserAgentInfo(BaseModel):
    # Parsed user-agent details (best-effort; any field can be unknown/None).
    browser: str | None = None
    browser_version: str | None = None
    os: str | None = None
    os_version: str | None = None
    device: str | None = None


class ClickEventGeoInfo(BaseModel):
    # Derived from IP address (best-effort; depends on GeoIP provider availability).
    country: str | None = None
    region: str | None = None
    city: str | None = None
    latitude: float | None = None
    longitude: float | None = None


class ClickEventEnrichedResponse(ClickEventResponse):
    ua: ClickEventUserAgentInfo | None = None
    geo: ClickEventGeoInfo | None = None
    referrer_domain: str | None = None


class URLAnalyticsSummary(BaseModel):
    # Aggregations computed from click events.
    total_clicks: int
    unique_ips: int | None = None
    clicks_last_24h: int | None = None

    top_referrers: list["ClickBucket"] = Field(default_factory=list)
    clicks_by_country: list["ClickBucket"] = Field(default_factory=list)
    clicks_by_browser: list["ClickBucket"] = Field(default_factory=list)
    clicks_by_os: list["ClickBucket"] = Field(default_factory=list)
    clicks_by_device: list["ClickBucket"] = Field(default_factory=list)


class ClickBucket(BaseModel):
    # Standard shape for aggregated analytics buckets.
    label: str
    count: int


class URLStatsResponse(BaseModel):
    short_code: str
    short_url: str
    original_url: str
    expires_at: datetime | None
    total_clicks: int
    # Backwards-compatible: existing clients can keep reading the basic click shape.
    recent_clicks: list[ClickEventResponse]

    # New (optional) richer analytics payload. Step 2/3/4 will populate this.
    analytics: URLAnalyticsSummary | None = None
    recent_clicks_enriched: list[ClickEventEnrichedResponse] = Field(default_factory=list)
