import pytest

from private_quant_terminal.portfolio.rolling_performance import (
    PortfolioRollingMetrics,
    calculate_rolling_metrics,
)


class TestCalculateRollingMetrics:
    def test_calculates_all_rolling_metrics(self) -> None:
        result = calculate_rolling_metrics(
            returns=(
                0.10,
                -0.05,
                0.15,
            ),
            window=2,
        )

        assert isinstance(result, PortfolioRollingMetrics)

        assert result.rolling_returns == pytest.approx(
            (
                0.045,
                0.0925,
            )
        )

        assert result.rolling_average == pytest.approx(
            (
                0.025,
                0.05,
            )
        )

        assert result.rolling_volatility == pytest.approx(
            (
                0.075,
                0.10,
            )
        )

        assert result.rolling_drawdown == pytest.approx(
            (
                -0.05,
                0.0,
            )
        )

        assert result.rolling_max_drawdown == pytest.approx(
            (
                -0.05,
                0.0,
            )
        )

    def test_rejects_empty_returns(self) -> None:
        with pytest.raises(
            ValueError,
            match="returns must not be empty",
        ):
            calculate_rolling_metrics(
                returns=(),
                window=1,
            )

    def test_rejects_total_loss_return(self) -> None:
        with pytest.raises(
            ValueError,
            match="returns must be greater than -1.0",
        ):
            calculate_rolling_metrics(
                returns=(0.10, -1.0),
                window=2,
            )

    def test_rejects_zero_window(self) -> None:
        with pytest.raises(
            ValueError,
            match="window must be greater than zero",
        ):
            calculate_rolling_metrics(
                returns=(0.10, 0.05),
                window=0,
            )

    def test_rejects_window_larger_than_returns(self) -> None:
        with pytest.raises(
            ValueError,
            match="window cannot be greater than the number of values",
        ):
            calculate_rolling_metrics(
                returns=(0.10, 0.05),
                window=3,
            )

    def test_rejects_window_one_for_volatility(self) -> None:
        with pytest.raises(
            ValueError,
            match="window must be at least 2 for rolling volatility",
        ):
            calculate_rolling_metrics(
                returns=(0.10, 0.05),
                window=1,
            )
