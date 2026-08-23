from collections.abc import Sequence
from math import sqrt


def active_return(
    portfolio_return: float,
    benchmark_return: float,
) -> float:
    """Calculate the return earned relative to a benchmark."""
    return portfolio_return - benchmark_return


def active_returns(
    portfolio_returns: Sequence[float],
    benchmark_returns: Sequence[float],
) -> tuple[float, ...]:
    """Calculate active returns for matching return series."""
    if len(portfolio_returns) != len(benchmark_returns):
        raise ValueError(
            "Portfolio and benchmark return series must have the same length"
        )

    return tuple(
        portfolio_return - benchmark_return
        for portfolio_return, benchmark_return in zip(
            portfolio_returns,
            benchmark_returns,
            strict=True,
        )
    )


def tracking_error(
    portfolio_returns: Sequence[float],
    benchmark_returns: Sequence[float],
) -> float:
    """Calculate the population standard deviation of active returns."""
    returns = active_returns(
        portfolio_returns,
        benchmark_returns,
    )

    if not returns:
        raise ValueError(
            "At least one portfolio and benchmark return is required"
        )

    mean_return = sum(returns) / len(returns)

    variance = sum(
        (value - mean_return) ** 2
        for value in returns
    ) / len(returns)

    return sqrt(variance)


def information_ratio(
    portfolio_returns: Sequence[float],
    benchmark_returns: Sequence[float],
) -> float:
    """Calculate average active return divided by tracking error."""
    returns = active_returns(
        portfolio_returns,
        benchmark_returns,
    )

    if not returns:
        raise ValueError(
            "At least one portfolio and benchmark return is required"
        )

    error = tracking_error(
        portfolio_returns,
        benchmark_returns,
    )

    if error == 0:
        raise ValueError(
            "Information ratio is undefined when tracking error is zero"
        )

    average_active_return = sum(returns) / len(returns)

    return average_active_return / error