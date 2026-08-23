from enum import Enum
from typing import Sequence


class TrendDirection(str, Enum):
    BULLISH = "bullish"
    BEARISH = "bearish"
    SIDEWAYS = "sideways"


def _validate_period(values: Sequence[float], period: int) -> None:
    if period <= 0:
        raise ValueError("period must be greater than zero")

    if len(values) < period:
        raise ValueError("values must contain at least period items")


def sma(values: Sequence[float], period: int) -> float:
    """Calculate the Simple Moving Average."""
    _validate_period(values, period)

    return sum(values[-period:]) / period


def ema(values: Sequence[float], period: int) -> float:
    """Calculate the Exponential Moving Average."""
    _validate_period(values, period)

    relevant_values = values[-period:]

    result = float(relevant_values[0])
    multiplier = 2 / (period + 1)

    for value in relevant_values[1:]:
        result = (float(value) - result) * multiplier + result

    return result


def detect_trend(values: Sequence[float]) -> TrendDirection:
    """Detect a simple directional trend from a price series."""
    if len(values) < 2:
        raise ValueError("values must contain at least two items")

    if values[-1] > values[0]:
        return TrendDirection.BULLISH

    if values[-1] < values[0]:
        return TrendDirection.BEARISH

    return TrendDirection.SIDEWAYS


def detect_crossover(
    *,
    fast_previous: float,
    fast_current: float,
    slow_previous: float,
    slow_current: float,
) -> str | None:
    """Detect bullish or bearish moving-average crossovers."""
    if (
        fast_previous <= slow_previous
        and fast_current > slow_current
    ):
        return "bullish"

    if (
        fast_previous >= slow_previous
        and fast_current < slow_current
    ):
        return "bearish"

    return None


def price_vs_ma(*, price: float, moving_average: float) -> str:
    """Return the position of price relative to a moving average."""
    if price > moving_average:
        return "above"

    if price < moving_average:
        return "below"

    return "at"
