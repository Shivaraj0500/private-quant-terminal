from collections.abc import Iterable

from private_quant_terminal.portfolio.position import Position


def calculate_concentration(
    positions: Iterable[Position],
) -> dict[str, float]:
    """Calculate each position's percentage concentration by market value."""
    positions = tuple(positions)

    if not positions:
        return {}

    total_value = sum(
        abs(position.quantity * position.average_price)
        for position in positions
    )

    if total_value == 0:
        return {
            position.symbol: 0.0
            for position in positions
        }

    return {
        position.symbol: (
            abs(position.quantity * position.average_price)
            / total_value
        )
        for position in positions
    }


def largest_concentration(
    positions: Iterable[Position],
) -> float:
    """Return the largest single-position concentration."""
    concentrations = calculate_concentration(positions)

    if not concentrations:
        return 0.0

    return max(concentrations.values())
