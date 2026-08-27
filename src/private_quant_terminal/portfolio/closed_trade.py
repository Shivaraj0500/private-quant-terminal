from dataclasses import dataclass


@dataclass(frozen=True)
class ClosedTrade:
    """Represents a completed portion of a portfolio position."""

    symbol: str
    quantity: int
    entry_price: float
    exit_price: float
    realized_pnl: float

    def __post_init__(self) -> None:
        if not self.symbol.strip():
            raise ValueError("symbol must not be empty")

        if self.quantity <= 0:
            raise ValueError("quantity must be greater than zero")

        if self.entry_price <= 0:
            raise ValueError(
                "entry_price must be greater than zero"
            )

        if self.exit_price <= 0:
            raise ValueError(
                "exit_price must be greater than zero"
            )
