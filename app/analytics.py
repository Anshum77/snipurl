from __future__ import annotations

from urllib.parse import urlparse

from user_agents import parse as parse_user_agent_string

from app.schemas import ClickEventUserAgentInfo


def parse_user_agent(ua_string: str | None) -> ClickEventUserAgentInfo | None:
    if not ua_string:
        return None

    parsed = parse_user_agent_string(ua_string)

    browser_family = parsed.browser.family or None
    browser_version = ".".join(str(part) for part in parsed.browser.version) if parsed.browser.version else None
    os_family = parsed.os.family or None
    os_version = ".".join(str(part) for part in parsed.os.version) if parsed.os.version else None

    if parsed.is_bot:
        device = "bot"
    elif parsed.is_tablet:
        device = "tablet"
    elif parsed.is_mobile:
        device = "mobile"
    elif parsed.is_pc:
        device = "pc"
    else:
        device = None

    return ClickEventUserAgentInfo(
        browser=browser_family,
        browser_version=browser_version,
        os=os_family,
        os_version=os_version,
        device=device,
    )


def parse_referrer_domain(referrer: str | None) -> str | None:
    if not referrer:
        return None

    try:
        parsed = urlparse(referrer)
    except ValueError:
        return None

    hostname = parsed.hostname
    if not hostname:
        return None

    return hostname.lower()
