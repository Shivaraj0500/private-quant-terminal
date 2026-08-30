from __future__ import annotations

from collections.abc import Sequence

from private_quant_terminal.models import Candle
from private_quant_terminal.strategy.expressions import (
    IndicatorExpression,
)
from private_quant_terminal.strategy.indicator_registry import (
    IndicatorRegistry,
)
from private_quant_terminal.strategy.indicator_providers import (
    IndicatorResult,
)
from private_quant_terminal.strategy.series import TimeSeries


class CanonicalIndicatorEngine:
    """Execute indicator expressions through the canonical registry."""

    def __init__(
        self,
        registry: IndicatorRegistry,
    ) -> None:
        self._registry = registry

    def calculate(
        self,
        expression: IndicatorExpression,
        candles: Sequence[Candle],
    ) -> IndicatorResult:
        if not candles:
            raise ValueError("candles cannot be empty")

        spec = self._registry.resolve_spec(
            expression.name
        )

        provider = self._registry.resolve_provider_for(
            spec
        )

        parameters = dict(expression.parameters)

        result = provider.calculate(
            spec,
            candles,
            parameters,
        )

        self._validate_result(
            spec,
            result,
            candles,
        )

        return result

    @staticmethod
    def _validate_result(
        spec,
        result: IndicatorResult,
        candles: Sequence[Candle],
    ) -> None:
        if not result.outputs:
            raise ValueError(
                f"Indicator {spec.id} returned no outputs"
            )

        for output_name, series in result.outputs.items():
            if not isinstance(series, TimeSeries):
                raise TypeError(
                    f"Indicator {spec.id} output "
                    f"{output_name} must be a TimeSeries"
                )

            if len(series) != len(candles):
                raise ValueError(
                    f"Indicator {spec.id} output "
                    f"{output_name} is not aligned with candles"
                )
