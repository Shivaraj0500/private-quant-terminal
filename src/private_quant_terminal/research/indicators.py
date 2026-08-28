import re
from collections.abc import Sequence

from private_quant_terminal.analytics.indicators import (
    ema,
    rsi,
    sma,
)
from private_quant_terminal.analytics.momentum import (
    momentum,
    rate_of_change,
    relative_strength_index,
)
from private_quant_terminal.models import Candle

_INDICATOR_PATTERN = re.compile(
    r"^(?P<name>[A-Z][A-Z0-9_]*)_(?P<period>[1-9][0-9]*)$"
)


def calculate_indicator(
    name: str,
    candles: Sequence[Candle],
) -> float:
    """Calculate the latest value of a supported indicator."""

    if not name:
        raise ValueError("indicator name cannot be empty")

    normalized_name = name.upper()

    if normalized_name in {"OPEN", "HIGH", "LOW", "CLOSE", "VOLUME"}:
        if not candles:
            raise ValueError("candles cannot be empty")

        candle = candles[-1]

        return float(getattr(candle, normalized_name.lower()))

    match = _INDICATOR_PATTERN.fullmatch(normalized_name)

    if match is None:
        raise ValueError(
            f"Invalid indicator specification: {name}"
        )

    indicator_name = match.group("name")
    period = int(match.group("period"))

    closes = [candle.close for candle in candles]

    if indicator_name == "SMA":
        return sma(closes, period)[-1]

    if indicator_name == "EMA":
        return ema(closes, period)[-1]

    if indicator_name == "RSI":
        return rsi(closes, period)[-1]

    if indicator_name == "MOMENTUM":
        return momentum(closes, period)

    if indicator_name == "ROC":
        return rate_of_change(closes, period)

    if indicator_name == "RELATIVE_STRENGTH_INDEX":
        return relative_strength_index(closes, period)

    raise KeyError(
        f"Unsupported research indicator: {indicator_name}"
    )


def calculate_indicators(
    names: Sequence[str],
    candles: Sequence[Candle],
) -> dict[str, float]:
    """Calculate the latest values for multiple indicators."""

    return {
        name: calculate_indicator(name, candles)
        for name in names
    }
