from dataclasses import dataclass


@dataclass(frozen=True)
class Position:
    """Represents a portfolio position managed by the application."""

    symbol: str
    quantity: int
    average_price: float
