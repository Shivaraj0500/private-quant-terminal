import itertools
from collections.abc import Sequence

from private_quant_terminal.models import Candle


def validate_candles(candles: Sequence[Candle]) -> None:
    """Validate a sequence of candles."""

    if not candles:
        raise ValueError("candle collection cannot be empty")

    timestamps = [candle.timestamp for candle in candles]

    if timestamps != sorted(timestamps):
        raise ValueError("candles must be ordered by timestamp")

    for previous, current in itertools.pairwise(candles):
        if previous.timestamp == current.timestamp:
            raise ValueError("duplicate candle timestamps are not allowed")
