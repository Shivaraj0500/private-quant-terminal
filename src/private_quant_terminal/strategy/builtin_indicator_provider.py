from __future__ import annotations

from collections.abc import Sequence

from private_quant_terminal.models import Candle
from private_quant_terminal.strategy.expressions import indicator
from private_quant_terminal.strategy.indicator_providers import (
    IndicatorProvider,
    IndicatorResult,
)
from private_quant_terminal.strategy.indicator_specs import IndicatorSpec
from private_quant_terminal.strategy.indicators import IndicatorEngine


class BuiltinStrategyIndicatorProvider(IndicatorProvider):
    """Adapter over the existing strategy indicator implementation.

    The adapter deliberately preserves the established strategy
    calculations instead of introducing a second mathematical
    implementation.
    """

    def __init__(
        self,
        *,
        engine: IndicatorEngine | None = None,
    ) -> None:
        self._engine = engine or IndicatorEngine()

    @property
    def provider_id(self) -> str:
        return "builtin_strategy"

    def supports(
        self,
        spec: IndicatorSpec,
    ) -> bool:
        return spec.provider == self.provider_id

    def calculate(
        self,
        spec: IndicatorSpec,
        candles: Sequence[Candle],
        parameters: dict[str, object],
    ) -> IndicatorResult:
        if spec.provider != self.provider_id:
            raise ValueError(
                f"Unsupported provider for {spec.id}: "
                f"{spec.provider}"
            )

        numeric_parameters: dict[str, float] = {}

        for name, value in parameters.items():
            if isinstance(value, bool):
                raise TypeError(
                    f"Indicator parameter {name} cannot be boolean."
                )

            if not isinstance(value, (int, float)):
                raise TypeError(
                    f"Indicator parameter {name} must be numeric."
                )

            numeric_parameters[name] = float(value)

        expression = indicator(
            spec.id,
            parameters=numeric_parameters,
        )

        series = self._engine.calculate(
            expression,
            candles,
        )

        return IndicatorResult(
            outputs={
                "value": series,
            },
        )
