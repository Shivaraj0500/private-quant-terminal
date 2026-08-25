import pytest

from private_quant_terminal.portfolio.rolling_sharpe import (
    rolling_sharpe_ratio,
)


class TestRollingSharpeRatio:
    def test_calculates_rolling_sharpe_ratio(self) -> None:
        result = rolling_sharpe_ratio(
            returns=(0.01, 0.03, 0.05),
            window=2,
        )

        assert result == pytest.approx((2.0, 4.0))

    def test_calculates_multiple_rolling_windows(self) -> None:
        result = rolling_sharpe_ratio(
            returns=(0.01, 0.03, 0.05, 0.07),
            window=2,
        )

        assert result == pytest.approx((2.0, 4.0, 6.0))

    def test_calculates_with_risk_free_rate(self) -> None:
        result = rolling_sharpe_ratio(
            returns=(0.03, 0.05),
            window=2,
            risk_free_rate=0.01,
        )

        assert result == pytest.approx((3.0,))

    def test_calculates_for_full_sequence(self) -> None:
        result = rolling_sharpe_ratio(
            returns=(0.01, 0.03, 0.05),
            window=3,
        )

        expected_mean = 0.03
        expected_volatility = (
            ((0.01 - expected_mean) ** 2
             + (0.03 - expected_mean) ** 2
             + (0.05 - expected_mean) ** 2)
            / 3
        ) ** 0.5

        assert result == pytest.approx(
            (expected_mean / expected_volatility,)
        )

    def test_rejects_window_of_one(self) -> None:
        with pytest.raises(
            ValueError,
            match="window must be greater than 1",
        ):
            rolling_sharpe_ratio(
                returns=(0.01, 0.02),
                window=1,
            )

    def test_rejects_zero_window(self) -> None:
        with pytest.raises(
            ValueError,
            match="window must be greater than 1",
        ):
            rolling_sharpe_ratio(
                returns=(0.01, 0.02),
                window=0,
            )

    def test_rejects_window_larger_than_returns(self) -> None:
        with pytest.raises(
            ValueError,
            match="window cannot be greater",
        ):
            rolling_sharpe_ratio(
                returns=(0.01, 0.02),
                window=3,
            )

    def test_rejects_zero_volatility(self) -> None:
        with pytest.raises(
            ValueError,
            match="volatility is zero",
        ):
            rolling_sharpe_ratio(
                returns=(0.02, 0.02),
                window=2,
            )

    def test_risk_free_rate_can_produce_zero_excess_volatility(self) -> None:
        with pytest.raises(
            ValueError,
            match="volatility is zero",
        ):
            rolling_sharpe_ratio(
                returns=(0.02, 0.02),
                window=2,
                risk_free_rate=0.01,
            )

    def test_returns_tuple(self) -> None:
        result = rolling_sharpe_ratio(
            returns=(0.01, 0.03),
            window=2,
        )

        assert isinstance(result, tuple)