import pytest

from private_quant_terminal.portfolio.position import Position
from private_quant_terminal.portfolio.risk_calculator import (
    PortfolioRiskCalculator,
)


class TestPortfolioRiskCalculator:
    def test_calculates_long_only_portfolio_risk(self) -> None:
        calculator = PortfolioRiskCalculator()

        positions = (
            Position(
                symbol="NIFTY",
                quantity=10,
                average_price=22000.0,
            ),
            Position(
                symbol="BANKNIFTY",
                quantity=5,
                average_price=48000.0,
            ),
        )

        risk = calculator.calculate(
            positions=positions,
            prices={
                "NIFTY": 23000.0,
                "BANKNIFTY": 50000.0,
            },
        )

        assert risk.long_exposure == 480000.0
        assert risk.short_exposure == 0.0
        assert risk.gross_exposure == 480000.0
        assert risk.net_exposure == 480000.0
        assert risk.largest_position_weight == 250000.0 / 480000.0
        assert risk.position_count == 2

    def test_calculates_short_only_portfolio_risk(self) -> None:
        calculator = PortfolioRiskCalculator()

        positions = (
            Position(
                symbol="NIFTY",
                quantity=-10,
                average_price=22000.0,
            ),
            Position(
                symbol="BANKNIFTY",
                quantity=-5,
                average_price=48000.0,
            ),
        )

        risk = calculator.calculate(
            positions=positions,
            prices={
                "NIFTY": 23000.0,
                "BANKNIFTY": 50000.0,
            },
        )

        assert risk.long_exposure == 0.0
        assert risk.short_exposure == 480000.0
        assert risk.gross_exposure == 480000.0
        assert risk.net_exposure == -480000.0
        assert risk.largest_position_weight == 250000.0 / 480000.0
        assert risk.position_count == 2

    def test_calculates_mixed_long_short_portfolio_risk(self) -> None:
        calculator = PortfolioRiskCalculator()

        positions = (
            Position(
                symbol="NIFTY",
                quantity=10,
                average_price=22000.0,
            ),
            Position(
                symbol="BANKNIFTY",
                quantity=-5,
                average_price=48000.0,
            ),
        )

        risk = calculator.calculate(
            positions=positions,
            prices={
                "NIFTY": 23000.0,
                "BANKNIFTY": 50000.0,
            },
        )

        assert risk.long_exposure == 230000.0
        assert risk.short_exposure == 250000.0
        assert risk.gross_exposure == 480000.0
        assert risk.net_exposure == -20000.0
        assert risk.largest_position_weight == 250000.0 / 480000.0
        assert risk.position_count == 2

    def test_calculates_empty_portfolio_risk(self) -> None:
        calculator = PortfolioRiskCalculator()

        risk = calculator.calculate(
            positions=(),
            prices={},
        )

        assert risk.long_exposure == 0.0
        assert risk.short_exposure == 0.0
        assert risk.gross_exposure == 0.0
        assert risk.net_exposure == 0.0
        assert risk.largest_position_weight == 0.0
        assert risk.position_count == 0

    def test_rejects_missing_market_price(self) -> None:
        calculator = PortfolioRiskCalculator()

        positions = (
            Position(
                symbol="NIFTY",
                quantity=10,
                average_price=22000.0,
            ),
        )

        with pytest.raises(
            ValueError,
            match="Missing market price for symbol: NIFTY",
        ):
            calculator.calculate(
                positions=positions,
                prices={},
            )

    @pytest.mark.parametrize(
        "price",
        [0.0, -1.0],
    )
    def test_rejects_non_positive_market_price(
        self,
        price: float,
    ) -> None:
        calculator = PortfolioRiskCalculator()

        positions = (
            Position(
                symbol="NIFTY",
                quantity=10,
                average_price=22000.0,
            ),
        )

        with pytest.raises(
            ValueError,
            match=(
                "Market price must be greater than zero "
                "for symbol: NIFTY"
            ),
        ):
            calculator.calculate(
                positions=positions,
                prices={"NIFTY": price},
            )

    def test_uses_absolute_exposure_for_largest_position_weight(
        self,
    ) -> None:
        calculator = PortfolioRiskCalculator()

        positions = (
            Position(
                symbol="LONG",
                quantity=100,
                average_price=100.0,
            ),
            Position(
                symbol="SHORT",
                quantity=-200,
                average_price=100.0,
            ),
        )

        risk = calculator.calculate(
            positions=positions,
            prices={
                "LONG": 100.0,
                "SHORT": 100.0,
            },
        )

        assert risk.gross_exposure == 30000.0
        assert risk.largest_position_weight == 20000.0 / 30000.0

    def test_private_largest_position_weight_returns_zero_for_zero_exposure(
        self,
    ) -> None:
        assert (
            PortfolioRiskCalculator._largest_position_weight(
                position_exposures=[],
                gross_exposure=0.0,
            )
            == 0.0
        )
