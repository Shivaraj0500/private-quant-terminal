from collections.abc import Sequence


def rolling_returns(
    returns: Sequence[float],
    window: int,
) -> tuple[float, ...]:
    """Calculate compounded returns for each rolling window."""
    _validate_window(returns, window)

    return tuple(
        _compound_returns(
            returns[index : index + window]
        )
        for index in range(len(returns) - window + 1)
    )


def rolling_average(
    values: Sequence[float],
    window: int,
) -> tuple[float, ...]:
    """Calculate the arithmetic average for each rolling window."""
    _validate_window(values, window)

    return tuple(
        sum(values[index : index + window]) / window
        for index in range(len(values) - window + 1)
    )


def rolling_volatility(
    returns: Sequence[float],
    window: int,
) -> tuple[float, ...]:
    """Calculate population volatility for each rolling window."""
    _validate_window(returns, window)

    if window < 2:
        raise ValueError(
            "window must be at least 2 for rolling volatility"
        )

    results: list[float] = []

    for index in range(len(returns) - window + 1):
        window_returns = returns[index : index + window]
        mean_return = sum(window_returns) / window

        variance = sum(
            (value - mean_return) ** 2
            for value in window_returns
        ) / window

        results.append(variance**0.5)

    return tuple(results)


def _compound_returns(
    returns: Sequence[float],
) -> float:
    compounded = 1.0

    for value in returns:
        compounded *= 1.0 + value

    return compounded - 1.0


def _validate_window(
    values: Sequence[float],
    window: int,
) -> None:
    if window <= 0:
        raise ValueError("window must be greater than zero")

    if window > len(values):
        raise ValueError(
            "window cannot be greater than the number of values"
        )