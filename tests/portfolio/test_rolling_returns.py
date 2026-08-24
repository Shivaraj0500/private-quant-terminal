from __future__ import annotations

from math import sqrt

import pytest

from private_quant_terminal.portfolio.rolling_returns import (
    rolling_cumulative_return,
    rolling_mean_return,
    rolling_return_volatility,
)


class TestRollingCumulativeReturn:
    def test_calculates_rolling_cumulative_returns(self) -> None:
        result = rolling_cumulative_return(
            returns=(0.10, 0.20, -0.10),
            window=2,
        )

        assert result == pytest.approx(
            (
                0.32,
                0.08,
            )
        )

    def test_calculates_single_full_window(self) -> None:
        result = rolling_cumulative_return(
            returns=(0.10, 0.20, -0.10),
            window=3,
        )

        assert result == pytest.approx((0.188,))

    def test_rejects_zero_window(self) -> None:
        with pytest.raises(
            ValueError,
            match="window must be greater than zero",
        ):
            rolling_cumulative_return(
                returns=(0.01, 0.02),
                window=0,
            )

    def test_rejects_negative_window(self) -> None:
        with pytest.raises(
            ValueError,
            match="window must be greater than zero",
        ):
            rolling_cumulative_return(
                returns=(0.01, 0.02),
                window=-1,
            )

    def test_rejects_window_larger_than_values(self) -> None:
        with pytest.raises(
            ValueError,
            match="window cannot be greater than the number of values",
        ):
            rolling_cumulative_return(
                returns=(0.01, 0.02),
                window=3,
            )


class TestRollingMeanReturn:
    def test_calculates_rolling_mean_returns(self) -> None:
        result = rolling_mean_return(
            returns=(0.01, 0.03, 0.05),
            window=2,
        )

        assert result == pytest.approx(
            (
                0.02,
                0.04,
            )
        )

    def test_calculates_single_value_window(self) -> None:
        result = rolling_mean_return(
            returns=(0.01, -0.02, 0.03),
            window=1,
        )

        assert result == pytest.approx(
            (
                0.01,
                -0.02,
                0.03,
            )
        )


class TestRollingReturnVolatility:
    def test_calculates_rolling_return_volatility(self) -> None:
        result = rolling_return_volatility(
            returns=(0.01, 0.03, 0.05),
            window=2,
        )

        expected = sqrt(0.0001)

        assert result == pytest.approx(
            (
                expected,
                expected,
            )
        )

    def test_returns_zero_for_constant_returns(self) -> None:
        result = rolling_return_volatility(
            returns=(0.02, 0.02, 0.02),
            window=2,
        )

        assert result == pytest.approx(
            (
                0.0,
                0.0,
            )
        )

    def test_calculates_single_full_window_volatility(self) -> None:
        result = rolling_return_volatility(
            returns=(0.01, 0.03),
            window=2,
        )

        assert result == pytest.approx((0.01,))

    def test_rejects_invalid_window(self) -> None:
        with pytest.raises(
            ValueError,
            match="window must be greater than zero",
        ):
            rolling_return_volatility(
                returns=(0.01, 0.02),
                window=0,
            )