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

        # Normalize aliases so uniqueness checks treat "Portfolio" and " portfolio " the same.
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


class URLStatsResponse(BaseModel):
    short_code: str
    short_url: str
    original_url: str
    expires_at: datetime | None
    total_clicks: int
    recent_clicks: list[ClickEventResponse]
