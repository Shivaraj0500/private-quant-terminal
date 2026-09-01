from collections.abc import Sequence
from itertools import pairwise


def _validate_period(period: int) -> None:
    """Validate that the period is a positive integer."""
    if period <= 0:
        raise ValueError("period must be greater than 0")


def _validate_enough_values(
    values: Sequence[float],
    required: int,
) -> None:
    """Validate that enough values exist for a calculation."""
    if len(values) < required:
        raise ValueError(
            f"values must contain at least {required} items"
        )


def momentum(
    values: Sequence[float],
    period: int = 1,
) -> float:
    """
    Calculate momentum.

    Momentum = latest value - value 'period' periods ago.
    """
    _validate_period(period)
    _validate_enough_values(values, period + 1)

    return values[-1] - values[-(period + 1)]


def rate_of_change(
    values: Sequence[float],
    period: int = 1,
) -> float:
    """
    Calculate percentage Rate of Change (ROC).

    ROC = ((latest - previous) / previous) * 100
    """
    _validate_period(period)
    _validate_enough_values(values, period + 1)

    previous = values[-(period + 1)]

    if previous == 0:
        raise ValueError(
            "previous value must not be zero"
        )

    return ((values[-1] - previous) / previous) * 100


def relative_strength_index(
    values: Sequence[float],
    period: int = 14,
) -> float:
    """
    Calculate the Relative Strength Index (RSI).

    Returns a value between 0 and 100.
    """
    _validate_period(period)
    _validate_enough_values(values, period + 1)

    recent_values = values[-(period + 1):]

    gains: list[float] = []
    losses: list[float] = []

    for previous, current in zip(
        recent_values,
        recent_values[1:],
    ):
        change = current - previous

        gains.append(max(change, 0))
        losses.append(abs(min(change, 0)))

    average_gain = sum(gains) / period
    average_loss = sum(losses) / period

    if average_loss == 0:
        return 100.0

    if average_gain == 0:
        return 0.0

    relative_strength = average_gain / average_loss

    return 100 - (100 / (1 + relative_strength))