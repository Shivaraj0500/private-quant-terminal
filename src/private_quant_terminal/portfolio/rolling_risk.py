from collections.abc import Sequence


def rolling_sharpe_ratio(
    returns: Sequence[float],
    window: int,
    risk_free_rate: float = 0.0,
) -> tuple[float, ...]:
    """Calculate the population Sharpe ratio for each rolling window."""
    _validate_window(returns, window)

    results: list[float] = []

    for index in range(len(returns) - window + 1):
        window_returns = returns[index : index + window]
        excess_returns = tuple(
            value - risk_free_rate
            for value in window_returns
        )
        volatility = _population_standard_deviation(
            excess_returns
        )

        if volatility == 0.0:
            raise ValueError(
                "rolling Sharpe ratio is undefined "
                "when volatility is zero"
            )

        average_excess_return = (
            sum(excess_returns) / window
        )

        results.append(
            average_excess_return / volatility
        )

    return tuple(results)


def rolling_downside_volatility(
    returns: Sequence[float],
    window: int,
    target_return: float = 0.0,
) -> tuple[float, ...]:
    """Calculate downside volatility for each rolling window."""
    _validate_window(returns, window)

    return tuple(
        _downside_volatility(
            returns[index : index + window],
            target_return,
        )
        for index in range(len(returns) - window + 1)
    )


def rolling_sortino_ratio(
    returns: Sequence[float],
    window: int,
    target_return: float = 0.0,
) -> tuple[float, ...]:
    """Calculate the Sortino ratio for each rolling window."""
    _validate_window(returns, window)

    results: list[float] = []

    for index in range(len(returns) - window + 1):
        window_returns = returns[index : index + window]
        downside_volatility = _downside_volatility(
            window_returns,
            target_return,
        )

        if downside_volatility == 0.0:
            raise ValueError(
                "rolling Sortino ratio is undefined "
                "when downside volatility is zero"
            )

        average_excess_return = (
            sum(
                value - target_return
                for value in window_returns
            )
            / window
        )

        results.append(
            average_excess_return / downside_volatility
        )

    return tuple(results)


def _population_standard_deviation(
    values: Sequence[float],
) -> float:
    mean = sum(values) / len(values)

    variance = (
        sum(
            (value - mean) ** 2
            for value in values
        )
        / len(values)
    )

    return variance**0.5


def _downside_volatility(
    returns: Sequence[float],
    target_return: float,
) -> float:
    downside_squared_returns = tuple(
        min(value - target_return, 0.0) ** 2
        for value in returns
    )

    return (
        sum(downside_squared_returns) / len(returns)
    ) ** 0.5


def _validate_window(
    returns: Sequence[float],
    window: int,
) -> None:
    if window <= 0:
        raise ValueError("window must be greater than zero")

    if window > len(returns):
        raise ValueError(
            "window cannot be greater than the number of returns"
        )