from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class DataField(str, Enum):
    """Canonical market-data fields that a strategy may require."""

    OPEN = "OPEN"
    HIGH = "HIGH"
    LOW = "LOW"
    CLOSE = "CLOSE"
    VOLUME = "VOLUME"


@dataclass(frozen=True)
class DataRequirement:
    """Canonical declaration of market data required by a strategy."""

    symbol: str
    timeframe: str
    fields: tuple[DataField, ...] = (
        DataField.OPEN,
        DataField.HIGH,
        DataField.LOW,
        DataField.CLOSE,
        DataField.VOLUME,
    )
    lookback: int = 1
    purpose: str = "MARKET_DATA"

    def __post_init__(self) -> None:
        symbol = self.symbol.strip().upper()
        timeframe = self.timeframe.strip().lower()
        purpose = self.purpose.strip().upper()

        if not symbol:
            raise ValueError("Data requirement symbol cannot be empty.")

        if not timeframe:
            raise ValueError("Data requirement timeframe cannot be empty.")

        if not purpose:
            raise ValueError("Data requirement purpose cannot be empty.")

        if self.lookback <= 0:
            raise ValueError("Data requirement lookback must be greater than zero.")

        normalized_fields = tuple(
            field if isinstance(field, DataField)
            else DataField(str(field).strip().upper())
            for field in self.fields
        )

        if not normalized_fields:
            raise ValueError("Data requirement must contain at least one field.")

        if len(normalized_fields) != len(set(normalized_fields)):
            raise ValueError("Data requirement fields must be unique.")

        object.__setattr__(self, "symbol", symbol)
        object.__setattr__(self, "timeframe", timeframe)
        object.__setattr__(self, "purpose", purpose)
        object.__setattr__(self, "fields", normalized_fields)
