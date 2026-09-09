from __future__ import annotations

from datetime import datetime
from typing import Protocol

from private_quant_terminal.data.derivatives.models import (
    HistoricalOptionChainSnapshot,
)


class HistoricalOptionChainProvider(Protocol):
    """Point-in-time historical option-chain access."""

    def get_latest_chain(
        self,
        underlying: str,
        as_of: datetime,
    ) -> HistoricalOptionChainSnapshot | None:
        """Return the latest chain snapshot available at or before as_of."""
        ...


class InMemoryHistoricalOptionChainProvider:
    """Deterministic historical option-chain provider for research and tests."""

    def __init__(
        self,
        snapshots: tuple[HistoricalOptionChainSnapshot, ...],
    ) -> None:
        self._snapshots = tuple(
            sorted(
                snapshots,
                key=lambda snapshot: snapshot.timestamp,
            )
        )

    def get_latest_chain(
        self,
        underlying: str,
        as_of: datetime,
    ) -> HistoricalOptionChainSnapshot | None:
        if as_of.tzinfo is None or as_of.utcoffset() is None:
            raise ValueError("as_of must be timezone-aware")

        normalized_underlying = underlying.strip().upper()
        if not normalized_underlying:
            raise ValueError("underlying must not be empty")

        candidates = (
            snapshot
            for snapshot in self._snapshots
            if snapshot.underlying == normalized_underlying
            and snapshot.timestamp <= as_of
        )

        return max(
            candidates,
            key=lambda snapshot: snapshot.timestamp,
            default=None,
        )
