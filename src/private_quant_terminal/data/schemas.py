from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True)
class MarketTick:
    """Single market price update."""

    symbol: str
    timestamp: datetime
    price: Decimal
    volume: int = 0

    def __post_init__(self) -> None:
        if not self.symbol:
            raise ValueError("symbol cannot be empty")

        if self.price <= 0:
            raise ValueError("price must be greater than zero")

        if self.volume < 0:
            raise ValueError("volume cannot be negative")
