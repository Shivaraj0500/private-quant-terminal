from dataclasses import dataclass

from private_quant_terminal.portfolio.position import Position


@dataclass(frozen=True)
class PortfolioExposure:
    """Portfolio exposure metrics."""

    gross_exposure: float
    net_exposure: float
    long_exposure: float
    short_exposure: float


def calculate_exposure(
    positions: tuple[Position, ...],
    prices: dict[str, float],
) -> PortfolioExposure:
    """Calculate gross, net, long and short portfolio exposure."""

    long_exposure = 0.0
    short_exposure = 0.0

    for position in positions:
        price = prices.get(position.symbol)

        if price is None:
            continue

        market_value = position.quantity * price

        if market_value >= 0:
            long_exposure += market_value
        else:
            short_exposure += abs(market_value)

    gross_exposure = long_exposure + short_exposure
    net_exposure = long_exposure - short_exposure

    return PortfolioExposure(
        gross_exposure=gross_exposure,
        net_exposure=net_exposure,
        long_exposure=long_exposure,
        short_exposure=short_exposure,
    )
