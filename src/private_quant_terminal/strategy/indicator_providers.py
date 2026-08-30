from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from private_quant_terminal.models import Candle
from private_quant_terminal.strategy.indicator_specs import IndicatorSpec
from private_quant_terminal.strategy.series import TimeSeries


@dataclass(frozen=True)
class IndicatorResult:
    """Validated result produced by an indicator provider."""

    outputs: Mapping[str, TimeSeries]

    def __post_init__(self) -> None:
        if not self.outputs:
            raise ValueError(
                "Indicator result must contain at least one output."
            )

        object.__setattr__(
            self,
            "outputs",
            dict(self.outputs),
        )

    def output(self, name: str) -> TimeSeries:
        try:
            return self.outputs[name]
        except KeyError as exc:
            raise KeyError(
                f"Unknown indicator output: {name}"
            ) from exc


class IndicatorProvider(ABC):
    """Calculation provider for canonical indicator specifications."""

    @property
    @abstractmethod
    def provider_id(self) -> str:
        """Return the stable provider identity."""

    @abstractmethod
    def calculate(
        self,
        spec: IndicatorSpec,
        candles: Sequence[Candle],
        parameters: dict[str, object],
    ) -> IndicatorResult:
        """Calculate the indicator deterministically."""