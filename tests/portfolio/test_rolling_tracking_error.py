from math import sqrt

import pytest

from private_quant_terminal.portfolio.rolling_tracking_error import (
    rolling_tracking_error,
)


class TestRollingTrackingError:
    def test_calculates_rolling_tracking_error(self) -> None:
        result = rolling_tracking_error(
            portfolio_returns=(0.03, 0.01, 0.05),
            benchmark_returns=(0.01, 0.02, 0.03),
            window=2,
        )

        assert result == pytest.approx(
            (
                0.015,
                0.015,
            )
        )

    def test_calculates_multiple_rolling_windows(self) -> None:
        result = rolling_tracking_error(
            portfolio_returns=(0.03, 0.01, 0.05, 0.02),
            benchmark_returns=(0.01, 0.02, 0.03, 0.01),
            window=2,
        )

        assert result == pytest.approx(
            (
                0.015,
                0.015,
                0.005,
            )
        )

    def test_calculates_for_full_sequence(self) -> None:
        result = rolling_tracking_error(
            portfolio_returns=(0.03, 0.01, 0.05),
            benchmark_returns=(0.01, 0.02, 0.03),
            window=3,
        )

        active_returns = (0.02, -0.01, 0.02)
        mean_active_return = sum(active_returns) / 3

        expected = sqrt(
            sum(
                (value - mean_active_return) ** 2
                for value in active_returns
            )
            / 3
        )

        assert result == pytest.approx((expected,))

    def test_returns_zero_for_constant_active_returns(self) -> None:
        result = rolling_tracking_error(
            portfolio_returns=(0.03, 0.04, 0.05),
            benchmark_returns=(0.01, 0.02, 0.03),
            window=2,
        )

        assert result == pytest.approx((0.0, 0.0))

    def test_rejects_different_length_sequences(self) -> None:
        with pytest.raises(
            ValueError,
            match="must have the same length",
        ):
            rolling_tracking_error(
                portfolio_returns=(0.01, 0.02),
                benchmark_returns=(0.01,),
                window=2,
            )

    def test_rejects_window_of_one(self) -> None:
        with pytest.raises(
            ValueError,
            match="window must be greater than 1",
        ):
            rolling_tracking_error(
                portfolio_returns=(0.01, 0.02),
                benchmark_returns=(0.01, 0.02),
                window=1,
            )

    def test_rejects_zero_window(self) -> None:
        with pytest.raises(
            ValueError,
            match="window must be greater than 1",
        ):
            rolling_tracking_error(
                portfolio_returns=(0.01, 0.02),
                benchmark_returns=(0.01, 0.02),
                window=0,
            )

    def test_rejects_window_larger_than_returns(self) -> None:
        with pytest.raises(
            ValueError,
            match="window cannot be greater",
        ):
            rolling_tracking_error(
                portfolio_returns=(0.01, 0.02),
                benchmark_returns=(0.01, 0.02),
                window=3,
            )

    def test_returns_tuple(self) -> None:
        result = rolling_tracking_error(
            portfolio_returns=(0.03, 0.01),
            benchmark_returns=(0.01, 0.02),
            window=2,
        )

        assert isinstance(result, tuple)