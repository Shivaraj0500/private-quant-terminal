from __future__ import annotations

from datetime import datetime
from typing import Protocol, runtime_checkable

from private_quant_terminal.data.derivatives.models import (
    HistoricalOptionCandle,
    HistoricalOptionContract,
)


@runtime_checkable
class HistoricalOptionCandleProvider(Protocol):
    """Point-in-time historical OHLCV access for concrete option contracts."""

    def get_latest_candle(
        self,
        contract: HistoricalOptionContract,
        as_of: datetime,
    ) -> HistoricalOptionCandle | None:
        """Return the latest candle available at or before as_of."""
        ...


class InMemoryHistoricalOptionCandleProvider:
    """Deterministic historical option-candle provider for research and tests."""

    def __init__(
        self,
        candles: tuple[HistoricalOptionCandle, ...],
    ) -> None:
        self._candles = tuple(
            sorted(
                candles,
                key=lambda candle: candle.timestamp,
            )
        )

    def get_latest_candle(
        self,
        contract: HistoricalOptionContract,
        as_of: datetime,
    ) -> HistoricalOptionCandle | None:
        if as_of.tzinfo is None or as_of.utcoffset() is None:
            raise ValueError("as_of must be timezone-aware")

        candidates = (
            candle
            for candle in self._candles
            if candle.contract.identifier == contract.identifier
            and candle.timestamp <= as_of
        )

        return max(
            candidates,
            key=lambda candle: candle.timestamp,
            default=None,
        )
