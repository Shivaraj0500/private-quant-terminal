from math import sqrt


def calculate_correlation(
    first_returns: tuple[float, ...],
    second_returns: tuple[float, ...],
) -> float:
    """Calculate Pearson correlation between two return series."""

    if len(first_returns) != len(second_returns):
        raise ValueError(
            "Return series must have the same length."
        )

    if len(first_returns) < 2:
        return 0.0

    first_average = sum(first_returns) / len(first_returns)
    second_average = sum(second_returns) / len(second_returns)

    covariance = sum(
        (first - first_average) * (second - second_average)
        for first, second in zip(
            first_returns,
            second_returns,
            strict=True,
        )
    )

    first_variance = sum(
        (value - first_average) ** 2
        for value in first_returns
    )

    second_variance = sum(
        (value - second_average) ** 2
        for value in second_returns
    )

    denominator = sqrt(
        first_variance * second_variance
    )

    if denominator == 0.0:
        return 0.0

    return covariance / denominator