from collections.abc import Sequence


def sma(values: Sequence[float], period: int) -> list[float]:
    """Calculate Simple Moving Average values."""
    _validate_period(period)
    _validate_enough_values(values, period)

    return [
        sum(values[index : index + period]) / period
        for index in range(len(values) - period + 1)
    ]


def ema(values: Sequence[float], period: int) -> list[float]:
    """Calculate Exponential Moving Average values."""
    _validate_period(period)
    _validate_enough_values(values, period)

    multiplier = 2 / (period + 1)
    result = [float(values[0])]

    for value in values[1:]:
        next_value = (
            float(value) * multiplier
            + result[-1] * (1 - multiplier)
        )
        result.append(next_value)

    return result


def rsi(values: Sequence[float], period: int) -> list[float]:
    """Calculate RSI using Wilder's smoothing method."""
    _validate_period(period)

    if len(values) <= period:
        raise ValueError(
            "values must contain more items than the period"
        )

    changes = [
        float(values[index]) - float(values[index - 1])
        for index in range(1, len(values))
    ]

    gains = [max(change, 0.0) for change in changes]
    losses = [abs(min(change, 0.0)) for change in changes]

    average_gain = sum(gains[:period]) / period
    average_loss = sum(losses[:period]) / period

    result = [
        _calculate_rsi(
            average_gain=average_gain,
            average_loss=average_loss,
        )
    ]

    for index in range(period, len(gains)):
        average_gain = (
            (average_gain * (period - 1)) + gains[index]
        ) / period

        average_loss = (
            (average_loss * (period - 1)) + losses[index]
        ) / period

        result.append(
            _calculate_rsi(
                average_gain=average_gain,
                average_loss=average_loss,
            )
        )

    return result


def atr(
    highs: Sequence[float],
    lows: Sequence[float],
    closes: Sequence[float],
    period: int,
) -> list[float]:
    """Calculate ATR using Wilder's smoothing method."""
    _validate_period(period)

    if not (
        len(highs) == len(lows) == len(closes)
    ):
        raise ValueError(
            "highs, lows, and closes must have matching lengths"
        )

    _validate_enough_values(highs, period)

    true_ranges = [
        float(highs[0]) - float(lows[0])
    ]

    for index in range(1, len(highs)):
        high = float(highs[index])
        low = float(lows[index])
        previous_close = float(closes[index - 1])

        true_ranges.append(
            max(
                high - low,
                abs(high - previous_close),
                abs(low - previous_close),
            )
        )

    first_atr = sum(true_ranges[:period]) / period
    result = [first_atr]

    for true_range in true_ranges[period:]:
        next_atr = (
            (result[-1] * (period - 1)) + true_range
        ) / period
        result.append(next_atr)

    return result


def _calculate_rsi(
    average_gain: float,
    average_loss: float,
) -> float:
    """Calculate one RSI value from average gain and loss."""
    if average_loss == 0:
        return 100.0

    if average_gain == 0:
        return 0.0

    relative_strength = average_gain / average_loss

    return 100 - (100 / (1 + relative_strength))


def _validate_period(period: int) -> None:
    """Ensure the indicator period is positive."""
    if period <= 0:
        raise ValueError("period must be greater than zero")


def _validate_enough_values(
    values: Sequence[float],
    period: int,
) -> None:
    """Ensure enough values exist for the requested period."""
    if len(values) < period:
        raise ValueError(
            "values must contain at least period items"
        )