from collections.abc import Sequence
from math import sqrt


def normalize_weights(
    weights: Sequence[float],
) -> tuple[float, ...]:
    """Normalize weights so their total equals one."""
    if not weights:
        raise ValueError(
            "At least one weight is required"
        )

    total_weight = sum(weights)

    if total_weight == 0:
        raise ValueError(
            "Weights must not sum to zero"
        )

    return tuple(
        weight / total_weight
        for weight in weights
    )


def equal_weights(
    asset_count: int,
) -> tuple[float, ...]:
    """Create an equal-weight portfolio."""
    if asset_count <= 0:
        raise ValueError(
            "Asset count must be greater than zero"
        )

    weight = 1 / asset_count

    return tuple(
        weight
        for _ in range(asset_count)
    )


def inverse_volatility_weights(
    volatilities: Sequence[float],
) -> tuple[float, ...]:
    """Create weights inversely proportional to asset volatility."""
    if not volatilities:
        raise ValueError(
            "At least one volatility is required"
        )

    if any(volatility <= 0 for volatility in volatilities):
        raise ValueError(
            "Volatilities must be greater than zero"
        )

    inverse_volatilities = tuple(
        1 / volatility
        for volatility in volatilities
    )

    return normalize_weights(
        inverse_volatilities
    )


def portfolio_expected_return(
    weights: Sequence[float],
    expected_returns: Sequence[float],
) -> float:
    """Calculate the weighted expected portfolio return."""
    _validate_matching_lengths(
        weights,
        expected_returns,
        "Weights and expected returns must have the same length",
    )

    return sum(
        weight * expected_return
        for weight, expected_return in zip(
            weights,
            expected_returns,
            strict=True,
        )
    )


def portfolio_variance(
    weights: Sequence[float],
    covariance_matrix: Sequence[Sequence[float]],
) -> float:
    """Calculate portfolio variance from weights and covariance."""
    if not weights:
        raise ValueError(
            "At least one weight is required"
        )

    asset_count = len(weights)

    if len(covariance_matrix) != asset_count:
        raise ValueError(
            "Covariance matrix size must match weight count"
        )

    if any(
        len(row) != asset_count
        for row in covariance_matrix
    ):
        raise ValueError(
            "Covariance matrix must be square"
        )

    return sum(
        weights[row_index]
        * covariance_matrix[row_index][column_index]
        * weights[column_index]
        for row_index in range(asset_count)
        for column_index in range(asset_count)
    )


def portfolio_volatility(
    weights: Sequence[float],
    covariance_matrix: Sequence[Sequence[float]],
) -> float:
    """Calculate portfolio volatility from portfolio variance."""
    variance = portfolio_variance(
        weights,
        covariance_matrix,
    )

    if variance < 0:
        raise ValueError(
            "Portfolio variance must not be negative"
        )

    return sqrt(variance)


def _validate_matching_lengths(
    first: Sequence[float],
    second: Sequence[float],
    error_message: str,
) -> None:
    """Validate that two sequences contain the same number of values."""
    if not first or not second:
        raise ValueError(
            "At least one value is required in each sequence"
        )

    if len(first) != len(second):
        raise ValueError(error_message)