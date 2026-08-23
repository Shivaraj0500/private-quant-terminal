from private_quant_terminal.portfolio.position import Position
from private_quant_terminal.portfolio.risk import PortfolioRisk


class PortfolioRiskCalculator:
    """Calculate portfolio-level exposure and concentration metrics."""

    def calculate(
        self,
        positions: tuple[Position, ...],
        prices: dict[str, float],
    ) -> PortfolioRisk:
        """Calculate risk metrics using current market prices."""
        long_exposure = 0.0
        short_exposure = 0.0
        position_exposures: list[float] = []

        for position in positions:
            price = prices.get(position.symbol)

            if price is None:
                raise ValueError(
                    f"Missing market price for symbol: {position.symbol}"
                )

            if price <= 0:
                raise ValueError(
                    f"Market price must be greater than zero for symbol: "
                    f"{position.symbol}"
                )

            exposure = position.quantity * price
            absolute_exposure = abs(exposure)

            position_exposures.append(absolute_exposure)

            if exposure > 0:
                long_exposure += exposure
            elif exposure < 0:
                short_exposure += absolute_exposure

        gross_exposure = long_exposure + short_exposure
        net_exposure = long_exposure - short_exposure

        largest_position_weight = self._largest_position_weight(
            position_exposures=position_exposures,
            gross_exposure=gross_exposure,
        )

        return PortfolioRisk(
            gross_exposure=gross_exposure,
            net_exposure=net_exposure,
            long_exposure=long_exposure,
            short_exposure=short_exposure,
            largest_position_weight=largest_position_weight,
            position_count=len(positions),
        )

    @staticmethod
    def _largest_position_weight(
        position_exposures: list[float],
        gross_exposure: float,
    ) -> float:
        """Calculate the largest absolute position as a portfolio weight."""
        if gross_exposure == 0.0:
            return 0.0

        return max(position_exposures) / gross_exposure
