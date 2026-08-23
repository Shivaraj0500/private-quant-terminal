from private_quant_terminal.portfolio.exposure import (
    PortfolioExposure,
    calculate_exposure,
)
from private_quant_terminal.portfolio.position import Position


class TestPortfolioExposure:
    def test_calculates_long_exposure(self) -> None:
        positions = (
            Position(
                symbol="NIFTY",
                quantity=50,
                average_price=22000.0,
            ),
        )

        result = calculate_exposure(
            positions=positions,
            prices={"NIFTY": 22500.0},
        )

        assert isinstance(result, PortfolioExposure)
        assert result.long_exposure == 1125000.0
        assert result.short_exposure == 0.0
        assert result.gross_exposure == 1125000.0
        assert result.net_exposure == 1125000.0

    def test_calculates_short_exposure(self) -> None:
        positions = (
            Position(
                symbol="BANKNIFTY",
                quantity=-25,
                average_price=48000.0,
            ),
        )

        result = calculate_exposure(
            positions=positions,
            prices={"BANKNIFTY": 50000.0},
        )

        assert result.long_exposure == 0.0
        assert result.short_exposure == 1250000.0
        assert result.gross_exposure == 1250000.0
        assert result.net_exposure == -1250000.0

    def test_calculates_combined_long_and_short_exposure(
        self,
    ) -> None:
        positions = (
            Position(
                symbol="NIFTY",
                quantity=50,
                average_price=22000.0,
            ),
            Position(
                symbol="BANKNIFTY",
                quantity=-25,
                average_price=48000.0,
            ),
        )

        result = calculate_exposure(
            positions=positions,
            prices={
                "NIFTY": 22500.0,
                "BANKNIFTY": 50000.0,
            },
        )

        assert result.long_exposure == 1125000.0
        assert result.short_exposure == 1250000.0
        assert result.gross_exposure == 2375000.0
        assert result.net_exposure == -125000.0

    def test_ignores_position_without_market_price(
        self,
    ) -> None:
        positions = (
            Position(
                symbol="NIFTY",
                quantity=50,
                average_price=22000.0,
            ),
            Position(
                symbol="BANKNIFTY",
                quantity=-25,
                average_price=48000.0,
            ),
        )

        result = calculate_exposure(
            positions=positions,
            prices={"NIFTY": 22500.0},
        )

        assert result.long_exposure == 1125000.0
        assert result.short_exposure == 0.0
        assert result.gross_exposure == 1125000.0
        assert result.net_exposure == 1125000.0

    def test_returns_zero_exposure_for_empty_portfolio(
        self,
    ) -> None:
        result = calculate_exposure(
            positions=(),
            prices={},
        )

        assert result.long_exposure == 0.0
        assert result.short_exposure == 0.0
        assert result.gross_exposure == 0.0
        assert result.net_exposure == 0.0
