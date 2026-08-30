from __future__ import annotations

from collections.abc import Sequence

from private_quant_terminal.models import Candle
from private_quant_terminal.strategy.expressions import (
    IndicatorExpression,
)
from private_quant_terminal.strategy.indicator_registry import (
    IndicatorRegistry,
)
from private_quant_terminal.strategy.indicator_warmup import (
    canonical_warmup,
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

        valid_outputs = {
            output.name.strip().lower()
            for output in spec.outputs
        }

        requested_output = expression.output.strip().lower()

        if requested_output not in valid_outputs:
            raise ValueError(
                f"Unknown indicator output "
                f"{expression.output!r} for indicator "
                f"{spec.id}. "
                f"Available outputs: "
                f"{sorted(valid_outputs)!r}"
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

        return self._apply_canonical_warmup(
            spec,
            result,
            parameters,
        )

    @staticmethod
    def _apply_canonical_warmup(
        spec,
        result: IndicatorResult,
        parameters: dict[str, object],
    ) -> IndicatorResult:
        warmup = canonical_warmup(
            spec.id,
            parameters,
        )

        if warmup <= 0:
            return result

        outputs = {}

        for output_name, series in result.outputs.items():
            values = list(series.values)

            for index in range(min(warmup, len(values))):
                values[index] = None

            outputs[output_name] = TimeSeries(
                timestamps=series.timestamps,
                values=tuple(values),
            )

        return IndicatorResult(outputs)


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
