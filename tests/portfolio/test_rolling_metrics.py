import pytest

from private_quant_terminal.portfolio.rolling_metrics import (
    rolling_average,
    rolling_returns,
    rolling_volatility,
)


class TestRollingMetrics:
    def test_calculates_rolling_returns(self) -> None:
        returns = (0.10, 0.20, -0.10, 0.05)

        result = rolling_returns(
            returns=returns,
            window=2,
        )

        assert result == pytest.approx(
            (
                0.32,
                0.08,
                -0.055,
            )
        )

    def test_calculates_rolling_returns_for_full_window(
        self,
    ) -> None:
        result = rolling_returns(
            returns=(0.10, 0.20, -0.10),
            window=3,
        )

        assert result == pytest.approx((0.188,))

    def test_calculates_rolling_average(self) -> None:
        result = rolling_average(
            values=(1.0, 2.0, 3.0, 4.0),
            window=2,
        )

        assert result == pytest.approx(
            (
                1.5,
                2.5,
                3.5,
            )
        )

    def test_calculates_rolling_average_for_full_window(
        self,
    ) -> None:
        result = rolling_average(
            values=(1.0, 2.0, 3.0),
            window=3,
        )

        assert result == pytest.approx((2.0,))

    def test_calculates_rolling_volatility(self) -> None:
        result = rolling_volatility(
            returns=(1.0, 3.0, 5.0),
            window=2,
        )

        assert result == pytest.approx(
            (
                1.0,
                1.0,
            )
        )

    def test_calculates_rolling_volatility_for_full_window(
        self,
    ) -> None:
        result = rolling_volatility(
            returns=(1.0, 3.0, 5.0),
            window=3,
        )

        assert result == pytest.approx(
            ((8.0 / 3.0) ** 0.5,)
        )

    @pytest.mark.parametrize(
        "window",
        (0, -1),
    )
    def test_rejects_non_positive_window(
        self,
        window: int,
    ) -> None:
        with pytest.raises(
            ValueError,
            match="window must be greater than zero",
        ):
            rolling_average(
                values=(1.0, 2.0, 3.0),
                window=window,
            )

    def test_rejects_window_larger_than_values(self) -> None:
        with pytest.raises(
            ValueError,
            match=(
                "window cannot be greater than "
                "the number of values"
            ),
        ):
            rolling_returns(
                returns=(0.10, 0.20),
                window=3,
            )

    def test_rejects_single_value_window_for_volatility(
        self,
    ) -> None:
        with pytest.raises(
            ValueError,
            match=(
                "window must be at least 2 "
                "for rolling volatility"
            ),
        ):
            rolling_volatility(
                returns=(0.10, 0.20),
                window=1,
            )