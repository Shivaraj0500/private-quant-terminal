from math import sqrt

import pytest

from private_quant_terminal.portfolio.rolling_sortino import (
    rolling_sortino_ratio,
)


class TestRollingSortinoRatio:
    def test_calculates_rolling_sortino_ratio(self) -> None:
        result = rolling_sortino_ratio(
            returns=(0.02, -0.01, 0.03),
            window=2,
        )

        assert result == pytest.approx(
            (
                1.0 / sqrt(2),
                sqrt(2),
            )
        )

    def test_calculates_multiple_rolling_windows(self) -> None:
        result = rolling_sortino_ratio(
            returns=(0.01, -0.01, 0.03, -0.02),
            window=2,
        )

        assert result == pytest.approx(
            (
                0.0,
                sqrt(2),
                0.25 * sqrt(2),
            )
        )

    def test_calculates_with_target_return(self) -> None:
        result = rolling_sortino_ratio(
            returns=(0.03, 0.01),
            window=2,
            target_return=0.02,
        )

        assert result == pytest.approx((0.0,))

    def test_calculates_for_full_sequence(self) -> None:
        result = rolling_sortino_ratio(
            returns=(0.02, -0.01, 0.03),
            window=3,
        )

        mean_return = 0.04 / 3
        downside_deviation = sqrt(0.0001 / 3)

        assert result == pytest.approx(
            (mean_return / downside_deviation,)
        )

    def test_rejects_window_of_one(self) -> None:
        with pytest.raises(
            ValueError,
            match="window must be greater than 1",
        ):
            rolling_sortino_ratio(
                returns=(0.01, -0.01),
                window=1,
            )

    def test_rejects_zero_window(self) -> None:
        with pytest.raises(
            ValueError,
            match="window must be greater than 1",
        ):
            rolling_sortino_ratio(
                returns=(0.01, -0.01),
                window=0,
            )

    def test_rejects_window_larger_than_returns(self) -> None:
        with pytest.raises(
            ValueError,
            match="window cannot be greater",
        ):
            rolling_sortino_ratio(
                returns=(0.01, -0.01),
                window=3,
            )

    def test_rejects_zero_downside_deviation(self) -> None:
        with pytest.raises(
            ValueError,
            match="downside deviation is zero",
        ):
            rolling_sortino_ratio(
                returns=(0.01, 0.02),
                window=2,
            )

    def test_returns_tuple(self) -> None:
        result = rolling_sortino_ratio(
            returns=(0.02, -0.01),
            window=2,
        )

        assert isinstance(result, tuple)