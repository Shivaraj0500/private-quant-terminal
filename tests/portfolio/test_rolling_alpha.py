import pytest

from private_quant_terminal.portfolio.rolling_alpha import rolling_alpha


class TestRollingAlpha:
    def test_calculates_rolling_alpha(self) -> None:
        result = rolling_alpha(
            portfolio_returns=(0.03, 0.05, 0.07),
            benchmark_returns=(0.02, 0.04, 0.06),
            window=2,
        )

        assert result == pytest.approx(
            (
                0.01,
                0.01,
            )
        )

    def test_calculates_rolling_alpha_with_risk_free_rate(self) -> None:
        result = rolling_alpha(
            portfolio_returns=(0.03, 0.05),
            benchmark_returns=(0.02, 0.04),
            window=2,
            risk_free_rate=0.01,
        )

        assert result == pytest.approx((0.01,))

    def test_returns_multiple_rolling_windows(self) -> None:
        result = rolling_alpha(
            portfolio_returns=(0.02, 0.04, 0.06, 0.08),
            benchmark_returns=(0.01, 0.02, 0.03, 0.04),
            window=2,
        )

        assert len(result) == 3

    def test_calculates_zero_alpha_for_matching_returns(self) -> None:
        result = rolling_alpha(
            portfolio_returns=(0.01, 0.02, 0.03),
            benchmark_returns=(0.01, 0.02, 0.03),
            window=3,
        )

        assert result == pytest.approx((0.0,))

    def test_rejects_non_positive_window(self) -> None:
        with pytest.raises(
            ValueError,
            match="window must be greater than zero",
        ):
            rolling_alpha(
                portfolio_returns=(0.01, 0.02),
                benchmark_returns=(0.01, 0.02),
                window=0,
            )

    def test_rejects_negative_window(self) -> None:
        with pytest.raises(
            ValueError,
            match="window must be greater than zero",
        ):
            rolling_alpha(
                portfolio_returns=(0.01, 0.02),
                benchmark_returns=(0.01, 0.02),
                window=-1,
            )

    def test_rejects_unequal_return_lengths(self) -> None:
        with pytest.raises(
            ValueError,
            match=(
                "portfolio_returns and benchmark_returns "
                "must have equal length"
            ),
        ):
            rolling_alpha(
                portfolio_returns=(0.01, 0.02),
                benchmark_returns=(0.01,),
                window=1,
            )

    def test_rejects_window_larger_than_returns(self) -> None:
        with pytest.raises(
            ValueError,
            match="window cannot be greater than the number of returns",
        ):
            rolling_alpha(
                portfolio_returns=(0.01, 0.02),
                benchmark_returns=(0.01, 0.02),
                window=3,
            )

    def test_rejects_zero_benchmark_variance(self) -> None:
        with pytest.raises(
            ValueError,
            match="benchmark variance must not be zero",
        ):
            rolling_alpha(
                portfolio_returns=(0.01, 0.02),
                benchmark_returns=(0.03, 0.03),
                window=2,
            )

    def test_returns_tuple(self) -> None:
        result = rolling_alpha(
            portfolio_returns=(0.03, 0.05),
            benchmark_returns=(0.02, 0.04),
            window=2,
        )

        assert isinstance(result, tuple)