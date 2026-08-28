import secrets
from urllib.parse import urlencode

from private_quant_terminal.brokers.upstox.config import UpstoxConfig


UPSTOX_AUTHORIZATION_URL = "https://api.upstox.com/v2/login/authorization/dialog"

_pending_states: set[str] = set()


def create_oauth_state() -> str:
    """Create and store a one-time OAuth state value."""

    state = secrets.token_urlsafe(32)
    _pending_states.add(state)

    return state


def consume_oauth_state(state: str) -> bool:
    """Validate and consume a one-time OAuth state value."""

    if state not in _pending_states:
        return False

    _pending_states.remove(state)
    return True


def build_authorization_url(
    config: UpstoxConfig,
    state: str,
) -> str:
    """Build the Upstox OAuth authorization URL."""

    query = urlencode(
        {
            "response_type": "code",
            "client_id": config.client_id,
            "redirect_uri": config.redirect_uri,
            "state": state,
        }
    )

    return f"{UPSTOX_AUTHORIZATION_URL}?{query}"
