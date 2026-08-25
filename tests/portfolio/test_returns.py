import pytest

from private_quant_terminal.portfolio.returns import (
    average_return,
    cumulative_return,
    geometric_average_return,
    simple_returns,
)


class TestSimpleReturns:
    def test_calculates_simple_returns(self) -> None:
        result = simple_returns((100.0, 110.0, 99.0))

        assert result == pytest.approx((0.10, -0.10))

    def test_calculates_multiple_price_changes(self) -> None:
        result = simple_returns((100.0, 120.0, 132.0, 105.6))

        assert result == pytest.approx((0.20, 0.10, -0.20))

    def test_rejects_single_price(self) -> None:
        with pytest.raises(
            ValueError,
            match="at least two prices",
        ):
            simple_returns((100.0,))

    def test_rejects_zero_price(self) -> None:
        with pytest.raises(
            ValueError,
            match="prices must be greater than zero",
        ):
            simple_returns((100.0, 0.0))

    def test_rejects_negative_price(self) -> None:
        with pytest.raises(
            ValueError,
            match="prices must be greater than zero",
        ):
            simple_returns((100.0, -50.0))


class TestCumulativeReturn:
    def test_calculates_cumulative_return(self) -> None:
        result = cumulative_return((0.10, -0.10))

        assert result == pytest.approx(-0.01)

    def test_calculates_compounded_return(self) -> None:
        result = cumulative_return((0.10, 0.20))

        assert result == pytest.approx(0.32)

    def test_rejects_empty_returns(self) -> None:
        with pytest.raises(
            ValueError,
            match="at least one return",
        ):
            cumulative_return(())


class TestAverageReturn:
    def test_calculates_average_return(self) -> None:
        result = average_return((0.10, 0.20, -0.10))

        assert result == pytest.approx(0.06666666666666667)

    def test_rejects_empty_returns(self) -> None:
        with pytest.raises(
            ValueError,
            match="at least one return",
        ):
            average_return(())


class TestGeometricAverageReturn:
    def test_calculates_geometric_average_return(self) -> None:
        result = geometric_average_return((0.10, 0.20))

        assert result == pytest.approx((1.32**0.5) - 1.0)

    def test_calculates_negative_geometric_return(self) -> None:
        result = geometric_average_return((0.10, -0.10))

        assert result == pytest.approx((0.99**0.5) - 1.0)

    def test_rejects_empty_returns(self) -> None:
        with pytest.raises(
            ValueError,
            match="at least one return",
        ):
            geometric_average_return(())

    def test_rejects_return_of_negative_one(self) -> None:
        with pytest.raises(
            ValueError,
            match="returns must be greater than -1",
        ):
            geometric_average_return((0.10, -1.0))