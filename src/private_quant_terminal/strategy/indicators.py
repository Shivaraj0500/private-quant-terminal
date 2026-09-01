from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass

from private_quant_terminal.analytics.indicators import (
    ema as calculate_ema,
)
from private_quant_terminal.analytics.indicators import (
    rsi as calculate_rsi,
)
from private_quant_terminal.analytics.indicators import (
    sma as calculate_sma,
)
from private_quant_terminal.models import Candle
from private_quant_terminal.strategy.expressions import (
    IndicatorExpression,
    PriceField,
)
from private_quant_terminal.strategy.series import (
    TimeSeries,
    aligned_series,
)


@dataclass(frozen=True)
class IndicatorDefinition:
    """Metadata and calculation contract for an indicator."""

    name: str
    required_periods: int
    calculator: Callable[
        [Sequence[Candle], dict[str, float]],
        Sequence[float],
    ]

    def __post_init__(self) -> None:
        normalized = self.name.strip().upper()

        if not normalized:
            raise ValueError(
                "Indicator name cannot be empty."
            )

        if self.required_periods < 1:
            raise ValueError(
                "required_periods must be greater than zero."
            )

        object.__setattr__(
            self,
            "name",
            normalized,
        )


class StrategyIndicatorRegistry:
    """Registry of indicators available to the strategy engine."""

    def __init__(self) -> None:
        self._definitions: dict[str, IndicatorDefinition] = {}

    def register(
        self,
        definition: IndicatorDefinition,
    ) -> None:
        name = definition.name

        if name in self._definitions:
            raise ValueError(
                f"Indicator already registered: {name}"
            )

        self._definitions[name] = definition

    def get(self, name: str) -> IndicatorDefinition:
        normalized = name.strip().upper()

        try:
            return self._definitions[normalized]
        except KeyError as exc:
            raise KeyError(
                f"Unknown strategy indicator: {name}"
            ) from exc

    def names(self) -> list[str]:
        return sorted(self._definitions)


def _period(
    parameters: dict[str, float],
    default: int = 14,
) -> int:
    value = int(parameters.get("period", default))

    if value <= 0:
        raise ValueError(
            "indicator period must be greater than zero"
        )

    return value


def _closes(candles: Sequence[Candle]) -> list[float]:
    return [float(candle.close) for candle in candles]


def _highs(candles: Sequence[Candle]) -> list[float]:
    return [float(candle.high) for candle in candles]


def _lows(candles: Sequence[Candle]) -> list[float]:
    return [float(candle.low) for candle in candles]


def _volumes(candles: Sequence[Candle]) -> list[float]:
    return [float(candle.volume) for candle in candles]


def _sma(
    candles: Sequence[Candle],
    parameters: dict[str, float],
) -> Sequence[float]:
    period = _period(parameters)
    return calculate_sma(_closes(candles), period)


def _ema(
    candles: Sequence[Candle],
    parameters: dict[str, float],
) -> Sequence[float]:
    period = _period(parameters)
    return calculate_ema(_closes(candles), period)


def _rsi(
    candles: Sequence[Candle],
    parameters: dict[str, float],
) -> Sequence[float]:
    period = _period(parameters)
    return calculate_rsi(_closes(candles), period)


def _historical_atr(
    candles: Sequence[Candle],
    period: int,
) -> Sequence[float]:
    """Calculate the repository's SMA-based ATR for every ready candle."""

    if period <= 0:
        raise ValueError(
            "indicator period must be greater than zero"
        )

    if len(candles) < period:
        raise ValueError(
            "not enough candles for ATR"
        )

    highs = _highs(candles)
    lows = _lows(candles)
    closes = _closes(candles)

    true_ranges: list[float] = []

    for index in range(len(candles)):
        if index == 0:
            true_ranges.append(
                highs[index] - lows[index]
            )
            continue

        previous_close = closes[index - 1]

        true_ranges.append(
            max(
                highs[index] - lows[index],
                abs(highs[index] - previous_close),
                abs(lows[index] - previous_close),
            )
        )

    return [
        sum(
            true_ranges[index - period + 1:index + 1]
        ) / period
        for index in range(period - 1, len(true_ranges))
    ]


def _atr(
    candles: Sequence[Candle],
    parameters: dict[str, float],
) -> Sequence[float]:
    return _historical_atr(
        candles,
        _period(parameters),
    )


def _supertrend(
    candles: Sequence[Candle],
    parameters: dict[str, float],
) -> Sequence[float]:
    """Calculate Supertrend using the strategy ATR convention."""

    period = _period(parameters, 10)
    multiplier = float(parameters.get("multiplier", 2.0))

    if multiplier <= 0:
        raise ValueError(
            "Supertrend multiplier must be greater than zero"
        )

    atr_values = _historical_atr(
        candles,
        period,
    )

    highs = _highs(candles)
    lows = _lows(candles)
    closes = _closes(candles)

    # ATR is available beginning at index period - 1.
    first_index = period - 1

    basic_upper: list[float] = []
    basic_lower: list[float] = []

    for offset, atr_value in enumerate(atr_values):
        index = first_index + offset
        midpoint = (highs[index] + lows[index]) / 2.0

        basic_upper.append(
            midpoint + multiplier * atr_value
        )
        basic_lower.append(
            midpoint - multiplier * atr_value
        )

    final_upper: list[float] = []
    final_lower: list[float] = []
    supertrend: list[float] = []

    for offset in range(len(atr_values)):
        index = first_index + offset

        upper = basic_upper[offset]
        lower = basic_lower[offset]

        if offset == 0:
            final_upper.append(upper)
            final_lower.append(lower)

            # Initial direction follows the close relative to
            # the initial midpoint/bands. We use the lower band
            # when the close is above it, otherwise the upper band.
            if closes[index] >= lower:
                supertrend.append(lower)
            else:
                supertrend.append(upper)

            continue

        previous_upper = final_upper[-1]
        previous_lower = final_lower[-1]
        previous_close = closes[index - 1]
        previous_supertrend = supertrend[-1]

        if (
            upper < previous_upper
            or previous_close > previous_upper
        ):
            current_upper = upper
        else:
            current_upper = previous_upper

        if (
            lower > previous_lower
            or previous_close < previous_lower
        ):
            current_lower = lower
        else:
            current_lower = previous_lower

        final_upper.append(current_upper)
        final_lower.append(current_lower)

        if previous_supertrend == previous_upper:
            if closes[index] <= current_upper:
                current_supertrend = current_upper
            else:
                current_supertrend = current_lower
        else:
            if closes[index] >= current_lower:
                current_supertrend = current_lower
            else:
                current_supertrend = current_upper

        supertrend.append(current_supertrend)

    return supertrend


def _momentum(
    candles: Sequence[Candle],
    parameters: dict[str, float],
) -> Sequence[float]:
    period = _period(parameters, 1)
    closes = _closes(candles)

    if len(closes) <= period:
        raise ValueError(
            "not enough candles for momentum"
        )

    return [
        closes[index] - closes[index - period]
        for index in range(period, len(closes))
    ]


def _roc(
    candles: Sequence[Candle],
    parameters: dict[str, float],
) -> Sequence[float]:
    period = _period(parameters, 1)
    closes = _closes(candles)

    if len(closes) <= period:
        raise ValueError(
            "not enough candles for ROC"
        )

    result: list[float] = []

    for index in range(period, len(closes)):
        previous = closes[index - period]

        if previous == 0:
            raise ValueError(
                "previous value must not be zero"
            )

        result.append(
            ((closes[index] - previous) / previous)
            * 100.0
        )

    return result


def _volume_sma(
    candles: Sequence[Candle],
    parameters: dict[str, float],
) -> Sequence[float]:
    period = _period(parameters, 20)
    volumes = _volumes(candles)

    if len(volumes) < period:
        raise ValueError(
            "not enough candles for volume SMA"
        )

    return [
        sum(volumes[index:index + period]) / period
        for index in range(len(volumes) - period + 1)
    ]


def _relative_volume(
    candles: Sequence[Candle],
    parameters: dict[str, float],
) -> Sequence[float]:
    period = _period(parameters, 20)
    volumes = _volumes(candles)

    if len(volumes) < period + 1:
        raise ValueError(
            "not enough candles for relative volume"
        )

    result: list[float] = []

    for index in range(period, len(volumes)):
        previous = volumes[index - period:index]
        average = sum(previous) / period

        if average == 0:
            raise ValueError(
                "average previous volume must not be zero"
            )

        result.append(volumes[index] / average)

    return result


def _obv(
    candles: Sequence[Candle],
    parameters: dict[str, float],
) -> Sequence[float]:
    del parameters

    closes = _closes(candles)
    volumes = _volumes(candles)

    if len(closes) < 2:
        raise ValueError(
            "at least two candles are required for OBV"
        )

    result: list[float] = [0.0]
    current = 0.0

    for index in range(1, len(closes)):
        if closes[index] > closes[index - 1]:
            current += volumes[index]
        elif closes[index] < closes[index - 1]:
            current -= volumes[index]

        result.append(current)

    return result


def _identity(
    candles: Sequence[Candle],
    parameters: dict[str, float],
) -> Sequence[float]:
    del parameters
    return _closes(candles)


def default_indicator_registry() -> StrategyIndicatorRegistry:
    """Return the deterministic built-in indicator registry."""

    registry = StrategyIndicatorRegistry()

    registry.register(
        IndicatorDefinition(
            name="SMA",
            required_periods=1,
            calculator=_sma,
        )
    )

    registry.register(
        IndicatorDefinition(
            name="EMA",
            required_periods=1,
            calculator=_ema,
        )
    )

    registry.register(
        IndicatorDefinition(
            name="RSI",
            required_periods=1,
            calculator=_rsi,
        )
    )

    registry.register(
        IndicatorDefinition(
            name="ATR",
            required_periods=1,
            calculator=_atr,
        )
    )

    registry.register(
        IndicatorDefinition(
            name="SUPERTREND",
            required_periods=1,
            calculator=_supertrend,
        )
    )

    registry.register(
        IndicatorDefinition(
            name="MOMENTUM",
            required_periods=1,
            calculator=_momentum,
        )
    )

    registry.register(
        IndicatorDefinition(
            name="ROC",
            required_periods=1,
            calculator=_roc,
        )
    )

    registry.register(
        IndicatorDefinition(
            name="VOLUME_SMA",
            required_periods=1,
            calculator=_volume_sma,
        )
    )

    registry.register(
        IndicatorDefinition(
            name="RELATIVE_VOLUME",
            required_periods=1,
            calculator=_relative_volume,
        )
    )

    registry.register(
        IndicatorDefinition(
            name="OBV",
            required_periods=1,
            calculator=_obv,
        )
    )

    return registry


class IndicatorEngine:
    """Calculate aligned indicator series for strategy evaluation."""

    def __init__(
        self,
        registry: StrategyIndicatorRegistry | None = None,
    ) -> None:
        self._registry = (
            registry
            if registry is not None
            else default_indicator_registry()
        )

    def calculate(
        self,
        expression: IndicatorExpression,
        candles: Sequence[Candle],
    ) -> TimeSeries:
        if not candles:
            raise ValueError(
                "candles cannot be empty"
            )

        definition = self._registry.get(expression.name)

        parameters = dict(expression.parameters)

        raw_values = tuple(
            float(value)
            for value in definition.calculator(
                candles,
                parameters,
            )
        )

        warmup = len(candles) - len(raw_values)

        if warmup < 0:
            raise ValueError(
                "indicator returned more values than candles"
            )

        return aligned_series(
            [candle.timestamp for candle in candles],
            raw_values,
            warmup=warmup,
        )


def price_series(
    candles: Sequence[Candle],
    field: PriceField,
) -> TimeSeries:
    values = tuple(
        float(getattr(candle, field.value))
        for candle in candles
    )

    return TimeSeries(
        timestamps=tuple(
            candle.timestamp
            for candle in candles
        ),
        values=values,
    )
