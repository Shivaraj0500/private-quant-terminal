from __future__ import annotations

from collections.abc import Mapping

_PERIOD_MINUS_ONE = {
    "BBANDS",
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
    output_name: str = "value",
) -> int:
    """Return canonical warmup for the current strategy indicators."""

    normalized_id = str(indicator_id).strip().upper()
    normalized_output = str(output_name).strip().lower()

    if not normalized_output:
        raise ValueError("output name must not be empty")

    if normalized_id == "MACD":
        fastperiod = _parameter(
            parameters,
            "fastperiod",
            default=12,
        )
        slowperiod = _parameter(
            parameters,
            "slowperiod",
            default=26,
        )
        signalperiod = _parameter(
            parameters,
            "signalperiod",
            default=9,
        )

        if fastperiod >= slowperiod:
            raise ValueError("fastperiod must be less than slowperiod")

        if normalized_output == "macd":
            return slowperiod - 1

        if normalized_output in {"signal", "histogram"}:
            return slowperiod + signalperiod - 2

        raise ValueError(f"Unknown indicator output {output_name!r} for MACD")

    if normalized_id in _FIXED:
        return _FIXED[normalized_id]

    if normalized_id in _PERIOD_MINUS_ONE:
        return _period(parameters) - 1

    if normalized_id in _PERIOD:
        return _period(parameters)

    raise ValueError(f"Unknown indicator: {normalized_id}")


def _parameter(
    parameters: Mapping[str, object],
    name: str,
    *,
    default: int,
) -> int:
    value = parameters.get(name, default)

    if isinstance(value, bool):
        raise ValueError(  # noqa: TRY004
            f"{name} must be a positive integer"
        )

    try:
        numeric = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be a positive integer") from exc

    if not numeric.is_integer():
        raise ValueError(f"{name} must be a positive integer")

    result = int(numeric)

    if result <= 0:
        raise ValueError(f"{name} must be a positive integer")

    return result
