from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Protocol

from private_quant_terminal.models.candle import Candle

from private_quant_terminal.strategy.data_requirements import DataRequirement
from private_quant_terminal.strategy.ir import StrategyIR


class CandleDataProvider(Protocol):
    """Provider capability required by the availability checker."""

    def get_candles(
        self,
        symbol: str,
        timeframe: str,
        limit: int,
    ) -> list[Candle]:
        """Return historical candles."""
        ...


class DataAvailabilityStatus(str, Enum):
    """Result of checking one strategy data requirement."""

    AVAILABLE = "AVAILABLE"
    INSUFFICIENT_HISTORY = "INSUFFICIENT_HISTORY"
    UNAVAILABLE = "UNAVAILABLE"


@dataclass(frozen=True)
class DataAvailabilityResult:
    """Deterministic evidence for one data requirement."""

    requirement: DataRequirement
    status: DataAvailabilityStatus
    required_candles: int
    available_candles: int
    message: str


class DataAvailabilityChecker:
    """Check whether a provider can satisfy strategy data requirements."""

    def __init__(self, provider: CandleDataProvider) -> None:
        self._provider = provider

    def check_requirement(
        self,
        requirement: DataRequirement,
    ) -> DataAvailabilityResult:
        try:
            candles = self._provider.get_candles(
                requirement.symbol,
                requirement.timeframe,
                requirement.lookback,
            )
        except (LookupError, ValueError, KeyError) as exc:
            return DataAvailabilityResult(
                requirement=requirement,
                status=DataAvailabilityStatus.UNAVAILABLE,
                required_candles=requirement.lookback,
                available_candles=0,
                message=str(exc),
            )

        available_candles = len(candles)

        if available_candles < requirement.lookback:
            return DataAvailabilityResult(
                requirement=requirement,
                status=DataAvailabilityStatus.INSUFFICIENT_HISTORY,
                required_candles=requirement.lookback,
                available_candles=available_candles,
                message=(
                    f"Required {requirement.lookback} candles but provider "
                    f"returned {available_candles}."
                ),
            )

        return DataAvailabilityResult(
            requirement=requirement,
            status=DataAvailabilityStatus.AVAILABLE,
            required_candles=requirement.lookback,
            available_candles=available_candles,
            message=(
                f"Provider returned at least {requirement.lookback} "
                "required candles."
            ),
        )

    def check_strategy(
        self,
        strategy: StrategyIR,
    ) -> tuple[DataAvailabilityResult, ...]:
        return tuple(
            self.check_requirement(requirement)
            for requirement in strategy.data_requirements
        )
