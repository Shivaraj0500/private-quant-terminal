from collections.abc import Sequence
from math import log, sqrt


def average_true_range(
    highs: Sequence[float],
    lows: Sequence[float],
    closes: Sequence[float],
    period: int = 14,
) -> float:
    """
    Calculate the Average True Range (ATR).

    True Range (TR):

        First period:
            TR = High - Low

        Subsequent periods:
            TR = max(
                High - Low,
                abs(High - Previous Close),
                abs(Low - Previous Close),
            )

    This function returns the simple average of the most recent
    `period` True Range values.
    """

    if period <= 0:
        raise ValueError("period must be greater than zero")

    if len(highs) != len(lows) or len(highs) != len(closes):
        raise ValueError("highs, lows, and closes must have matching lengths")

    if len(highs) < period:
        raise ValueError("not enough price data for the requested period")

    true_ranges: list[float] = []

    for index in range(len(highs)):
        high = highs[index]
        low = lows[index]

        if index == 0:
            true_range = high - low
        else:
            previous_close = closes[index - 1]

            true_range = max(
                high - low,
                abs(high - previous_close),
                abs(low - previous_close),
            )

        true_ranges.append(true_range)

    recent_true_ranges = true_ranges[-period:]

    return sum(recent_true_ranges) / period


def historical_volatility(
    closes: Sequence[float],
    period: int = 20,
    annualization_factor: int = 252,
) -> float:
    """
    Calculate annualized historical volatility using log returns.
    """

    if period <= 0:
        raise ValueError("period must be greater than zero")

    if annualization_factor <= 0:
        raise ValueError("annualization_factor must be greater than zero")

    if len(closes) < period + 1:
        raise ValueError(
            "not enough closing prices for the requested period"
        )

    recent_closes = closes[-(period + 1):]

    if any(close <= 0 for close in recent_closes):
        raise ValueError("close prices must be greater than zero")

    log_returns = [
        log(recent_closes[index] / recent_closes[index - 1])
        for index in range(1, len(recent_closes))
    ]

    return standard_deviation(log_returns) * sqrt(annualization_factor)


def standard_deviation(values: Sequence[float]) -> float:
    """
    Calculate population standard deviation.
    """

    if len(values) < 2:
        raise ValueError("at least two values are required")

    mean = sum(values) / len(values)

    variance = sum(
        (value - mean) ** 2
        for value in values
    ) / len(values)

    return sqrt(variance)