from dataclasses import dataclass


@dataclass(frozen=True)
class MarketDepthLevel:
    price: float
    quantity: float
    orders: int | None = None


@dataclass(frozen=True)
class MarketDepth:
    symbol: str
    exchange: str
    bids: tuple[MarketDepthLevel, ...]
    asks: tuple[MarketDepthLevel, ...]
