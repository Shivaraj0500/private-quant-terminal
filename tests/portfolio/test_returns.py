import pytest

from private_quant_terminal.portfolio.returns import Returns


class TestReturns:
    def test_calculates_profit(self) -> None:
        returns = Returns(
            initial_value=100000.0,
            current_value=125000.0,
        )

        assert returns.profit_loss == 25000.0

    def test_calculates_loss(self) -> None:
        returns = Returns(
            initial_value=100000.0,
            current_value=75000.0,
        )

        assert returns.profit_loss == -25000.0

    def test_calculates_zero_profit_loss(self) -> None:
        returns = Returns(
            initial_value=100000.0,
            current_value=100000.0,
        )

        assert returns.profit_loss == 0.0

    def test_calculates_positive_return_percentage(self) -> None:
        returns = Returns(
            initial_value=100000.0,
            current_value=125000.0,
        )

        assert returns.return_percentage == 25.0

    def test_calculates_negative_return_percentage(self) -> None:
        returns = Returns(
            initial_value=100000.0,
            current_value=80000.0,
        )

        assert returns.return_percentage == -20.0

    def test_calculates_zero_return_percentage(self) -> None:
        returns = Returns(
            initial_value=100000.0,
            current_value=100000.0,
        )

        assert returns.return_percentage == 0.0

    def test_identifies_profit(self) -> None:
        returns = Returns(
            initial_value=100000.0,
            current_value=125000.0,
        )

        assert returns.is_profit is True
        assert returns.is_loss is False
        assert returns.is_break_even is False

    def test_identifies_loss(self) -> None:
        returns = Returns(
            initial_value=100000.0,
            current_value=75000.0,
        )

        assert returns.is_profit is False
        assert returns.is_loss is True
        assert returns.is_break_even is False

    def test_identifies_break_even(self) -> None:
        returns = Returns(
            initial_value=100000.0,
            current_value=100000.0,
        )

        assert returns.is_profit is False
        assert returns.is_loss is False
        assert returns.is_break_even is True

    def test_rejects_zero_initial_value_for_percentage_return(
        self,
    ) -> None:
        returns = Returns(
            initial_value=0.0,
            current_value=100000.0,
        )

        with pytest.raises(
            ValueError,
            match="initial_value must not be zero",
        ):
            _ = returns.return_percentage