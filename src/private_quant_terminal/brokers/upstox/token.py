from dataclasses import dataclass

import httpx

from private_quant_terminal.brokers.upstox.config import UpstoxConfig

UPSTOX_TOKEN_URL = (
    "https://api.upstox.com/v2/login/authorization/token"
)


@dataclass(frozen=True)
class UpstoxTokenResponse:
    """Token data returned by Upstox after OAuth authentication."""

    access_token: str
    token_type: str | None = None
    user_name: str | None = None
    user_id: str | None = None


def exchange_authorization_code(
    config: UpstoxConfig,
    code: str,
) -> UpstoxTokenResponse:
    """Exchange an OAuth authorization code for an access token."""

    response = httpx.post(
        UPSTOX_TOKEN_URL,
        headers={
            "Accept": "application/json",
        },
        data={
            "code": code,
            "client_id": config.client_id,
            "client_secret": config.client_secret,
            "redirect_uri": config.redirect_uri,
            "grant_type": "authorization_code",
        },
        timeout=20.0,
    )

    response.raise_for_status()

    payload = response.json()

    return UpstoxTokenResponse(
        access_token=payload["access_token"],
        token_type=payload.get("token_type"),
        user_name=payload.get("user_name"),
        user_id=payload.get("user_id"),
    )
