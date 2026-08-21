from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Tick:
    symbol: str
    exchange: str
    timestamp: datetime
    last_price: float
    volume: float | None = None
    bid: float | None = None
    ask: float | None = None
