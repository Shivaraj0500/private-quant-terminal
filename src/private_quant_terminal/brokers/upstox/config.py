import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class UpstoxConfig:
    """Configuration required for the Upstox broker integration."""

    client_id: str
    client_secret: str
    redirect_uri: str

    @classmethod
    def from_environment(cls) -> "UpstoxConfig":
        """Load Upstox configuration from environment variables."""

        client_id = os.getenv("UPSTOX_CLIENT_ID")
        client_secret = os.getenv("UPSTOX_CLIENT_SECRET")
        redirect_uri = os.getenv("UPSTOX_REDIRECT_URI")

        missing = [
            name
            for name, value in {
                "UPSTOX_CLIENT_ID": client_id,
                "UPSTOX_CLIENT_SECRET": client_secret,
                "UPSTOX_REDIRECT_URI": redirect_uri,
            }.items()
            if not value
        ]

        if missing:
            raise RuntimeError(
                "Missing required Upstox environment variables: "
                + ", ".join(missing)
            )

        return cls(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
        )
