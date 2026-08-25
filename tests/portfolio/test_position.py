import pytest

from private_quant_terminal.portfolio.position import Position


class TestPosition:
    def test_creates_long_position(self) -> None:
        position = Position(
            symbol="RELIANCE",
            quantity=10,
            average_price=100.0,
        )

        assert position.symbol == "RELIANCE"
        assert position.quantity == 10
        assert position.average_price == 100.0

    def test_creates_short_position(self) -> None:
        position = Position(
            symbol="NIFTY",
            quantity=-5,
            average_price=200.0,
        )

        assert position.quantity == -5

    def test_allows_zero_quantity(self) -> None:
        position = Position(
            symbol="RELIANCE",
            quantity=0,
            average_price=100.0,
        )

        assert position.cost_basis == pytest.approx(0.0)
        assert position.market_value(120.0) == pytest.approx(0.0)
        assert position.unrealized_pnl(120.0) == pytest.approx(0.0)
        assert position.unrealized_pnl_percentage(120.0) == pytest.approx(0.0)

    def test_calculates_cost_basis(self) -> None:
        position = Position(
            symbol="RELIANCE",
            quantity=10,
            average_price=100.0,
        )

        assert position.cost_basis == pytest.approx(1000.0)

    def test_calculates_market_value(self) -> None:
        position = Position(
            symbol="RELIANCE",
            quantity=10,
            average_price=100.0,
        )

        assert position.market_value(120.0) == pytest.approx(1200.0)

    def test_calculates_unrealized_profit(self) -> None:
        position = Position(
            symbol="RELIANCE",
            quantity=10,
            average_price=100.0,
        )

        assert position.unrealized_pnl(120.0) == pytest.approx(200.0)

    def test_calculates_unrealized_loss(self) -> None:
        position = Position(
            symbol="RELIANCE",
            quantity=10,
            average_price=100.0,
        )

        assert position.unrealized_pnl(80.0) == pytest.approx(-200.0)

    def test_calculates_unrealized_pnl_percentage(self) -> None:
        position = Position(
            symbol="RELIANCE",
            quantity=10,
            average_price=100.0,
        )

        assert position.unrealized_pnl_percentage(110.0) == pytest.approx(0.10)

    def test_calculates_short_position_pnl(self) -> None:
        position = Position(
            symbol="NIFTY",
            quantity=-10,
            average_price=100.0,
        )

        assert position.unrealized_pnl(90.0) == pytest.approx(100.0)

    def test_rejects_empty_symbol(self) -> None:
        with pytest.raises(ValueError, match="symbol must not be empty"):
            Position(
                symbol="",
                quantity=10,
                average_price=100.0,
            )

    def test_rejects_whitespace_symbol(self) -> None:
        with pytest.raises(ValueError, match="symbol must not be empty"):
            Position(
                symbol="   ",
                quantity=10,
                average_price=100.0,
            )

    def test_rejects_zero_average_price(self) -> None:
        with pytest.raises(
            ValueError,
            match="average_price must be greater than zero",
        ):
            Position(
                symbol="RELIANCE",
                quantity=10,
                average_price=0.0,
            )

    def test_rejects_negative_average_price(self) -> None:
        with pytest.raises(
            ValueError,
            match="average_price must be greater than zero",
        ):
            Position(
                symbol="RELIANCE",
                quantity=10,
                average_price=-100.0,
            )

    def test_rejects_zero_current_price(self) -> None:
        position = Position(
            symbol="RELIANCE",
            quantity=10,
            average_price=100.0,
        )

        with pytest.raises(
            ValueError,
            match="current_price must be greater than zero",
        ):
            position.market_value(0.0)

    def test_rejects_negative_current_price(self) -> None:
        position = Position(
            symbol="RELIANCE",
            quantity=10,
            average_price=100.0,
        )

        with pytest.raises(
            ValueError,
            match="current_price must be greater than zero",
        ):
            position.market_value(-10.0)