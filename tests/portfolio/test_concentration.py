from private_quant_terminal.portfolio.concentration import (
    calculate_concentration,
    largest_concentration,
)
from private_quant_terminal.portfolio.position import Position


class TestCalculateConcentration:
    def test_returns_empty_result_for_no_positions(self) -> None:
        assert calculate_concentration(()) == {}

    def test_calculates_position_concentrations(self) -> None:
        positions = (
            Position(
                symbol="NIFTY",
                quantity=10,
                average_price=100.0,
            ),
            Position(
                symbol="BANKNIFTY",
                quantity=5,
                average_price=100.0,
            ),
        )

        result = calculate_concentration(positions)

        assert result == {
            "NIFTY": 2 / 3,
            "BANKNIFTY": 1 / 3,
        }

    def test_returns_zero_concentration_when_total_value_is_zero(
        self,
    ) -> None:
        positions = (
            Position(
                symbol="NIFTY",
                quantity=0,
                average_price=100.0,
            ),
            Position(
                symbol="BANKNIFTY",
                quantity=0,
                average_price=200.0,
            ),
        )

        result = calculate_concentration(positions)

        assert result == {
            "NIFTY": 0.0,
            "BANKNIFTY": 0.0,
        }


class TestLargestConcentration:
    def test_returns_zero_for_no_positions(self) -> None:
        assert largest_concentration(()) == 0.0

    def test_returns_largest_position_concentration(self) -> None:
        positions = (
            Position(
                symbol="NIFTY",
                quantity=10,
                average_price=100.0,
            ),
            Position(
                symbol="BANKNIFTY",
                quantity=5,
                average_price=100.0,
            ),
        )

        assert largest_concentration(positions) == 2 / 3
