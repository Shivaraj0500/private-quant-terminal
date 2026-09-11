from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Protocol

from private_quant_terminal.models.instrument import Instrument


class MarginRequirementType(str, Enum):
    ABSOLUTE = "ABSOLUTE"


@dataclass(frozen=True)
class HistoricalInstrumentEconomics:
    """Point-in-time economic metadata for a concrete instrument."""

    instrument: Instrument
    timestamp: datetime
    contract_multiplier: float
    margin_requirement: float | None = None
    margin_requirement_type: MarginRequirementType | None = None

    def __post_init__(self) -> None:
        if self.timestamp.tzinfo is None or self.timestamp.utcoffset() is None:
            raise ValueError("timestamp must be timezone-aware.")

        if self.contract_multiplier <= 0:
            raise ValueError("contract_multiplier must be greater than zero.")

        if self.margin_requirement is not None:
            if self.margin_requirement < 0:
                raise ValueError("margin_requirement cannot be negative.")

            if self.margin_requirement_type is None:
                raise ValueError(
                    "margin_requirement_type is required when margin_requirement is provided."
                )
        elif self.margin_requirement_type is not None:
            raise ValueError(
                "margin_requirement must be provided when margin_requirement_type is set."
            )


class HistoricalInstrumentEconomicsProvider(Protocol):
    """Point-in-time historical instrument-economics access."""

    def get_latest_economics(
        self,
        instrument: Instrument,
        as_of: datetime,
    ) -> HistoricalInstrumentEconomics | None:
        """Return latest economics available at or before as_of."""
        ...


class InMemoryHistoricalInstrumentEconomicsProvider:
    """Deterministic historical economics provider for research and tests."""

    def __init__(
        self,
        records: tuple[HistoricalInstrumentEconomics, ...],
    ) -> None:
        self._records = tuple(
            sorted(
                records,
                key=lambda record: record.timestamp,
            )
        )

    def get_latest_economics(
        self,
        instrument: Instrument,
        as_of: datetime,
    ) -> HistoricalInstrumentEconomics | None:
        if as_of.tzinfo is None or as_of.utcoffset() is None:
            raise ValueError("as_of must be timezone-aware.")

        candidates = (
            record
            for record in self._records
            if record.instrument.identifier == instrument.identifier and record.timestamp <= as_of
        )

        return max(
            candidates,
            key=lambda record: record.timestamp,
            default=None,
        )
