from collections.abc import Sequence


def _normalized_weights(
    weights: Sequence[float],
) -> tuple[float, ...]:
    """Return portfolio weights normalized to sum to one."""
    if not weights:
        return ()

    if any(weight < 0.0 for weight in weights):
        raise ValueError(
            "Weights must not contain negative values.",
        )

    total_weight = sum(weights)

    if total_weight == 0.0:
        return ()

    return tuple(
        weight / total_weight
        for weight in weights
        if weight > 0.0
    )


def herfindahl_index(
    weights: Sequence[float],
) -> float:
    """Calculate the Herfindahl concentration index."""
    normalized_weights = _normalized_weights(weights)

    return sum(
        weight * weight
        for weight in normalized_weights
    )


def effective_number_of_positions(
    weights: Sequence[float],
) -> float:
    """Calculate the effective number of equally weighted positions."""
    index = herfindahl_index(weights)

    if index == 0.0:
        return 0.0

    return 1.0 / index


def largest_weight(
    weights: Sequence[float],
) -> float:
    """Return the largest normalized portfolio weight."""
    normalized_weights = _normalized_weights(weights)

    if not normalized_weights:
        return 0.0

    return max(normalized_weights)


def diversification_score(
    weights: Sequence[float],
) -> float:
    """Calculate a normalized diversification score between zero and one."""
    normalized_weights = _normalized_weights(weights)
    position_count = len(normalized_weights)

    if position_count <= 1:
        return 0.0

    index = herfindahl_index(normalized_weights)
    minimum_index = 1.0 / position_count

    return (
        1.0 - index
    ) / (
        1.0 - minimum_index
    )