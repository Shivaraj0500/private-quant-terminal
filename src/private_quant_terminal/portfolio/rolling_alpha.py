from collections.abc import Sequence
from statistics import mean


def rolling_alpha(
    portfolio_returns: Sequence[float],
    benchmark_returns: Sequence[float],
    window: int,
    risk_free_rate: float = 0.0,
) -> tuple[float, ...]:
    """
    Calculate Jensen's alpha across rolling windows.

    Alpha is calculated as:

        alpha = mean(portfolio returns)
                - risk_free_rate
                - beta * (mean(benchmark returns) - risk_free_rate)

    Beta is calculated within each rolling window using population
    covariance and population variance.
    """
    if window <= 0:
        raise ValueError("window must be greater than zero")

    if len(portfolio_returns) != len(benchmark_returns):
        raise ValueError(
            "portfolio_returns and benchmark_returns must have equal length"
        )

    if len(portfolio_returns) < window:
        raise ValueError(
            "window cannot be greater than the number of returns"
        )

    results: list[float] = []

    for start in range(len(portfolio_returns) - window + 1):
        portfolio_window = portfolio_returns[start : start + window]
        benchmark_window = benchmark_returns[start : start + window]

        portfolio_mean = mean(portfolio_window)
        benchmark_mean = mean(benchmark_window)

        covariance = sum(
            (portfolio_return - portfolio_mean)
            * (benchmark_return - benchmark_mean)
            for portfolio_return, benchmark_return in zip(
                portfolio_window,
                benchmark_window,
            )
        ) / window

        benchmark_variance = sum(
            (benchmark_return - benchmark_mean) ** 2
            for benchmark_return in benchmark_window
        ) / window

        if benchmark_variance == 0:
            raise ValueError(
                "benchmark variance must not be zero"
            )

        beta = covariance / benchmark_variance

        alpha = (
            portfolio_mean
            - risk_free_rate
            - beta * (benchmark_mean - risk_free_rate)
        )

        results.append(alpha)

    return tuple(results)