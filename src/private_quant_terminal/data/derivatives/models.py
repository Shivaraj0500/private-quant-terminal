from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from private_quant_terminal.models.candle import Candle
from private_quant_terminal.models.instrument import Instrument
from private_quant_terminal.models.instrument import InstrumentType


@dataclass(frozen=True)
class HistoricalOptionContract:
    """A concrete option contract resolved at a historical timestamp."""

    instrument: Instrument
    resolved_at: datetime

    def __post_init__(self) -> None:
        if self.resolved_at.utcoffset() is None:
            raise ValueError("resolved_at must be timezone-aware.")

        if self.instrument.instrument_type is not InstrumentType.OPTION:
            raise ValueError(
                "HistoricalOptionContract requires an OPTION instrument."
            )

        if self.instrument.expiry is None:
            raise ValueError("Option contract requires an expiry.")

        if self.instrument.strike is None:
            raise ValueError("Option contract requires a strike.")

        if self.instrument.option_type is None:
            raise ValueError("Option contract requires an option type.")

    @property
    def identifier(self) -> str:
        return self.instrument.identifier


@dataclass(frozen=True)
class HistoricalOptionCandle:
    """Historical OHLCV observation for one concrete option contract."""

    contract: HistoricalOptionContract
    candle: Candle

    @property
    def timestamp(self) -> datetime:
        return self.candle.timestamp

    @property
    def open(self) -> float:
        return self.candle.open

    @property
    def high(self) -> float:
        return self.candle.high

    @property
    def low(self) -> float:
        return self.candle.low

    @property
    def close(self) -> float:
        return self.candle.close

    @property
    def volume(self) -> float:
        return self.candle.volume


@dataclass(frozen=True)
class HistoricalOptionQuote:
    """Point-in-time quote for one concrete historical option contract."""

    contract: HistoricalOptionContract
    timestamp: datetime
    bid: float
    ask: float
    close: float

    def __post_init__(self) -> None:
        if self.timestamp.utcoffset() is None:
            raise ValueError("timestamp must be timezone-aware.")

        if self.bid < 0:
            raise ValueError("bid must not be negative.")

        if self.ask < 0:
            raise ValueError("ask must not be negative.")

        if self.close < 0:
            raise ValueError("close must not be negative.")

        if self.ask < self.bid:
            raise ValueError("ask must be greater than or equal to bid.")


@dataclass(frozen=True)
class HistoricalOptionChainSnapshot:
    """Complete option-chain observation available at one point in time."""

    timestamp: datetime
    underlying: str
    underlying_price: float
    quotes: tuple[HistoricalOptionQuote, ...]

    def __post_init__(self) -> None:
        if self.timestamp.utcoffset() is None:
            raise ValueError("timestamp must be timezone-aware.")

        normalized_underlying = self.underlying.strip().upper()

        if not normalized_underlying:
            raise ValueError("underlying must not be empty.")

        object.__setattr__(self, "underlying", normalized_underlying)

        if self.underlying_price <= 0:
            raise ValueError("underlying_price must be greater than zero.")

        for quote in self.quotes:
            if quote.contract.instrument.symbol != normalized_underlying:
                raise ValueError(
                    "Option quote underlying does not match chain snapshot."
                )

            if quote.timestamp != self.timestamp:
                raise ValueError(
                    "Option quote timestamp must match chain snapshot timestamp."
                )
