from __future__ import annotations

from collections.abc import Sequence


def rolling_beta(
    portfolio_returns: Sequence[float],
    benchmark_returns: Sequence[float],
    window: int,
) -> tuple[float, ...]:
    """Calculate beta for each rolling return window."""
    _validate_inputs(
        portfolio_returns=portfolio_returns,
        benchmark_returns=benchmark_returns,
        window=window,
    )

    return tuple(
        _calculate_beta(
            portfolio_returns=portfolio_returns[index : index + window],
            benchmark_returns=benchmark_returns[index : index + window],
        )
        for index in range(len(portfolio_returns) - window + 1)
    )


def _calculate_beta(
    portfolio_returns: Sequence[float],
    benchmark_returns: Sequence[float],
) -> float:
    portfolio_mean = sum(portfolio_returns) / len(portfolio_returns)
    benchmark_mean = sum(benchmark_returns) / len(benchmark_returns)

    covariance = sum(
        (portfolio_return - portfolio_mean)
        * (benchmark_return - benchmark_mean)
        for portfolio_return, benchmark_return in zip(
            portfolio_returns,
            benchmark_returns,
            strict=True,
        )
    ) / len(portfolio_returns)

    benchmark_variance = sum(
        (benchmark_return - benchmark_mean) ** 2
        for benchmark_return in benchmark_returns
    ) / len(benchmark_returns)

    if benchmark_variance == 0:
        raise ValueError(
            "benchmark returns must have non-zero variance"
        )

    return covariance / benchmark_variance


def _validate_inputs(
    portfolio_returns: Sequence[float],
    benchmark_returns: Sequence[float],
    window: int,
) -> None:
    if len(portfolio_returns) != len(benchmark_returns):
        raise ValueError(
            "portfolio and benchmark returns must have equal lengths"
        )

    if not portfolio_returns:
        raise ValueError("returns cannot be empty")

    if window <= 0:
        raise ValueError("window must be greater than zero")

    if window > len(portfolio_returns):
        raise ValueError(
            "window cannot be greater than the number of returns"
        )