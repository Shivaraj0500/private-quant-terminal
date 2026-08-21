from dataclasses import dataclass
from enum import Enum
from typing import Optional


class SignalType(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


@dataclass(frozen=True)
class Signal:
    symbol: str
    signal_type: SignalType
    price: Optional[float] = None
    reason: Optional[str] = None