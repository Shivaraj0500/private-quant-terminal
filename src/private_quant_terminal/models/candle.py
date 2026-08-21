from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Candle:
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float = 0.0

    def __post_init__(self) -> None:
        if self.high < self.low:
            raise ValueError("high cannot be lower than low")

        if not self.low <= self.open <= self.high:
            raise ValueError("open must be between low and high")

        if not self.low <= self.close <= self.high:
            raise ValueError("close must be between low and high")

        if self.volume < 0:
            raise ValueError("volume cannot be negative")
