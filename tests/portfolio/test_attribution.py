from private_quant_terminal.portfolio.attribution import (
    Attribution,
    calculate_attribution,
)


class TestCalculateAttribution:
    def test_calculates_attribution_for_multiple_positions(
        self,
    ) -> None:
        result = calculate_attribution(
            {
                "NIFTY": 15000.0,
                "BANKNIFTY": -5000.0,
            }
        )

        assert result == (
            Attribution(
                symbol="NIFTY",
                pnl=15000.0,
                contribution=150.0,
            ),
            Attribution(
                symbol="BANKNIFTY",
                pnl=-5000.0,
                contribution=-50.0,
            ),
        )

    def test_calculates_attribution_for_single_position(
        self,
    ) -> None:
        result = calculate_attribution(
            {
                "NIFTY": 10000.0,
            }
        )

        assert result == (
            Attribution(
                symbol="NIFTY",
                pnl=10000.0,
                contribution=100.0,
            ),
        )

    def test_returns_zero_contribution_when_total_pnl_is_zero(
        self,
    ) -> None:
        result = calculate_attribution(
            {
                "NIFTY": 5000.0,
                "BANKNIFTY": -5000.0,
            }
        )

        assert result == (
            Attribution(
                symbol="NIFTY",
                pnl=5000.0,
                contribution=0.0,
            ),
            Attribution(
                symbol="BANKNIFTY",
                pnl=-5000.0,
                contribution=0.0,
            ),
        )

    def test_returns_empty_tuple_for_empty_input(
        self,
    ) -> None:
        assert calculate_attribution({}) == ()