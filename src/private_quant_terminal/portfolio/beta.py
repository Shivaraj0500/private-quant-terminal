from collections.abc import Sequence


def covariance(
    values: Sequence[float],
    benchmark_values: Sequence[float],
) -> float:
    """Calculate population covariance between two return series."""
    if len(values) != len(benchmark_values):
        raise ValueError(
            "Return series must have the same length.",
        )

    if not values:
        return 0.0

    values_mean = sum(values) / len(values)
    benchmark_mean = (
        sum(benchmark_values) / len(benchmark_values)
    )

    return sum(
        (value - values_mean)
        * (benchmark_value - benchmark_mean)
        for value, benchmark_value in zip(
            values,
            benchmark_values,
            strict=True,
        )
    ) / len(values)


def variance(
    values: Sequence[float],
) -> float:
    """Calculate population variance for a return series."""
    if not values:
        return 0.0

    mean = sum(values) / len(values)

    return sum(
        (value - mean) ** 2
        for value in values
    ) / len(values)


def beta(
    portfolio_returns: Sequence[float],
    benchmark_returns: Sequence[float],
) -> float:
    """Calculate portfolio beta relative to a benchmark."""
    benchmark_variance = variance(
        benchmark_returns,
    )

    if benchmark_variance == 0.0:
        raise ValueError(
            "Benchmark returns must have non-zero variance.",
        )

    return (
        covariance(
            portfolio_returns,
            benchmark_returns,
        )
        / benchmark_variance
    )