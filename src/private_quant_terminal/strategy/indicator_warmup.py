from __future__ import annotations

from collections.abc import Mapping


_PERIOD_MINUS_ONE = {
    "SMA",
    "EMA",
    "ATR",
    "SUPERTREND",
    "VOLUME_SMA",
}

_PERIOD = {
    "RSI",
    "MOMENTUM",
    "ROC",
    "RELATIVE_VOLUME",
}

_FIXED = {
    "OBV": 0,
}


def _period(parameters: Mapping[str, object]) -> int:
    if "period" not in parameters:
        raise ValueError("period parameter is required")

    value = parameters["period"]

    try:
        period = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("period must be a positive integer") from exc

    if period <= 0:
        raise ValueError("period must be a positive integer")

    return period


def canonical_warmup(
    indicator_id: str,
    parameters: Mapping[str, object],
) -> int:
    """Return canonical warmup for the current strategy indicators."""

    normalized_id = str(indicator_id).strip().upper()

    if normalized_id in _FIXED:
        return _FIXED[normalized_id]

    if normalized_id in _PERIOD_MINUS_ONE:
        return _period(parameters) - 1

    if normalized_id in _PERIOD:
        return _period(parameters)

    raise ValueError(
        f"Unknown indicator: {normalized_id}"
    )
