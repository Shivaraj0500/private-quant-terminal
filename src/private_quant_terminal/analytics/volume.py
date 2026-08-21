from collections.abc import Sequence


def volume_sma(
    volumes: Sequence[float],
    period: int = 20,
) -> float:
    """
    Calculate the Simple Moving Average of the most recent volume values.
    """

    if period <= 0:
        raise ValueError("period must be greater than zero")

    if len(volumes) < period:
        raise ValueError(
            "not enough volume data for the requested period"
        )

    recent_volumes = volumes[-period:]

    return sum(recent_volumes) / period


def relative_volume(
    volumes: Sequence[float],
    period: int = 20,
) -> float:
    """
    Calculate Relative Volume (RVOL).

    RVOL compares the latest volume against the average volume
    of the previous `period` observations.

        RVOL = Current Volume / Average Previous Volume

    An RVOL above 1.0 indicates above-average volume.
    """

    if period <= 0:
        raise ValueError("period must be greater than zero")

    if len(volumes) < period + 1:
        raise ValueError(
            "not enough volume data for the requested period"
        )

    current_volume = volumes[-1]
    previous_volumes = volumes[-(period + 1):-1]

    average_volume = sum(previous_volumes) / period

    if average_volume == 0:
        raise ValueError(
            "average previous volume must not be zero"
        )

    return current_volume / average_volume


def volume_rate_of_change(
    volumes: Sequence[float],
    period: int = 1,
) -> float:
    """
    Calculate the percentage change in volume.

        VROC = (
            Current Volume - Volume N periods ago
        ) / Volume N periods ago * 100
    """

    if period <= 0:
        raise ValueError("period must be greater than zero")

    if len(volumes) < period + 1:
        raise ValueError(
            "not enough volume data for the requested period"
        )

    current_volume = volumes[-1]
    previous_volume = volumes[-(period + 1)]

    if previous_volume == 0:
        raise ValueError(
            "previous volume must not be zero"
        )

    return (
        (current_volume - previous_volume)
        / previous_volume
    ) * 100


def on_balance_volume(
    closes: Sequence[float],
    volumes: Sequence[float],
) -> float:
    """
    Calculate cumulative On-Balance Volume (OBV).

    If today's close is higher than the previous close:
        OBV += volume

    If today's close is lower than the previous close:
        OBV -= volume

    If closes are equal:
        OBV remains unchanged.

    The first period establishes the starting OBV at 0.
    """

    if len(closes) != len(volumes):
        raise ValueError(
            "closes and volumes must have matching lengths"
        )

    if len(closes) < 2:
        raise ValueError(
            "at least two periods are required"
        )

    obv = 0.0

    for index in range(1, len(closes)):
        if closes[index] > closes[index - 1]:
            obv += volumes[index]
        elif closes[index] < closes[index - 1]:
            obv -= volumes[index]

    return obv