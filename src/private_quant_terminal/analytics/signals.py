from dataclasses import dataclass
from enum import Enum


class SignalDirection(str, Enum):
    STRONG_BUY = "STRONG_BUY"
    BUY = "BUY"
    HOLD = "HOLD"
    SELL = "SELL"
    STRONG_SELL = "STRONG_SELL"


@dataclass(frozen=True)
class SignalResult:
    direction: SignalDirection
    score: int
    trend_score: int
    momentum_score: int
    volume_score: int
    volatility_score: int


def trend_score(
    short_moving_average: float,
    long_moving_average: float,
) -> int:
    """
    Score market trend.

    Returns:
        1  -> bullish
        0  -> neutral
        -1 -> bearish
    """
    if short_moving_average > long_moving_average:
        return 1

    if short_moving_average < long_moving_average:
        return -1

    return 0


def momentum_score(
    rsi: float,
    overbought: float = 70.0,
    oversold: float = 30.0,
) -> int:
    """
    Score momentum using RSI.

    Returns:
        1  -> bullish momentum
        0  -> neutral
        -1 -> bearish momentum
    """
    if not 0.0 <= rsi <= 100.0:
        raise ValueError("RSI must be between 0 and 100")

    if oversold >= overbought:
        raise ValueError("oversold must be less than overbought")

    if rsi < oversold:
        return 1

    if rsi > overbought:
        return -1

    return 0


def volume_score(relative_volume_value: float) -> int:
    """
    Score market participation using relative volume.

    Relative volume:
        > 1.0 -> above-average participation
        = 1.0 -> average participation
        < 1.0 -> below-average participation
    """
    if relative_volume_value < 0:
        raise ValueError("relative volume must not be negative")

    if relative_volume_value > 1.0:
        return 1

    if relative_volume_value < 1.0:
        return -1

    return 0


def volatility_score(
    current_volatility: float,
    average_volatility: float,
) -> int:
    """
    Score the volatility regime.

    Returns:
        1  -> normal or lower volatility
        0  -> unchanged volatility
        -1 -> elevated volatility
    """
    if current_volatility < 0:
        raise ValueError("current volatility must not be negative")

    if average_volatility < 0:
        raise ValueError("average volatility must not be negative")

    if current_volatility < average_volatility:
        return 1

    if current_volatility > average_volatility:
        return -1

    return 0


def generate_signal(
    short_moving_average: float,
    long_moving_average: float,
    rsi: float,
    relative_volume_value: float,
    current_volatility: float,
    average_volatility: float,
) -> SignalResult:
    """
    Generate a deterministic trading signal.

    Component scoring:

        Trend:
            bullish = +1
            neutral =  0
            bearish = -1

        Momentum:
            bullish = +1
            neutral =  0
            bearish = -1

        Volume:
            strong = +1
            average = 0
            weak = -1

        Volatility:
            normal/lower = +1
            unchanged = 0
            elevated = -1

    Total score range: -4 to +4.
    """

    calculated_trend_score = trend_score(
        short_moving_average,
        long_moving_average,
    )

    calculated_momentum_score = momentum_score(rsi)

    calculated_volume_score = volume_score(
        relative_volume_value,
    )

    calculated_volatility_score = volatility_score(
        current_volatility,
        average_volatility,
    )

    score = (
        calculated_trend_score
        + calculated_momentum_score
        + calculated_volume_score
        + calculated_volatility_score
    )

    if score >= 3:
        direction = SignalDirection.STRONG_BUY
    elif score >= 1:
        direction = SignalDirection.BUY
    elif score <= -3:
        direction = SignalDirection.STRONG_SELL
    elif score <= -1:
        direction = SignalDirection.SELL
    else:
        direction = SignalDirection.HOLD

    return SignalResult(
        direction=direction,
        score=score,
        trend_score=calculated_trend_score,
        momentum_score=calculated_momentum_score,
        volume_score=calculated_volume_score,
        volatility_score=calculated_volatility_score,
    )