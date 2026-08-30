from dataclasses import dataclass
from datetime import UTC, datetime

from private_quant_terminal.brokers.upstox.token import (
    UpstoxTokenResponse,
)


@dataclass(frozen=True)
class UpstoxSession:
    """Represents the currently authenticated Upstox session."""

    access_token: str
    token_type: str | None
    user_id: str | None
    user_name: str | None
    authenticated_at: datetime


class UpstoxSessionStore:
    """In-memory store for the current Upstox session."""

    def __init__(self) -> None:
        self._session: UpstoxSession | None = None

    def save(
        self,
        token: UpstoxTokenResponse,
    ) -> UpstoxSession:
        """Save the authenticated Upstox session."""

        session = UpstoxSession(
            access_token=token.access_token,
            token_type=token.token_type,
            user_id=token.user_id,
            user_name=token.user_name,
            authenticated_at=datetime.now(UTC),
        )

        self._session = session

        return session

    def get(self) -> UpstoxSession | None:
        """Return the current authenticated session."""

        return self._session

    def is_authenticated(self) -> bool:
        """Return whether an Upstox session is available."""

        return self._session is not None

    def clear(self) -> None:
        """Clear the current Upstox session."""

        self._session = None
