from math import sqrt

import pytest

from private_quant_terminal.portfolio.rolling_information_ratio import (
    rolling_information_ratio,
)


class TestRollingInformationRatio:
    def test_calculates_rolling_information_ratio(self) -> None:
        result = rolling_information_ratio(
            portfolio_returns=(0.03, 0.01, 0.05),
            benchmark_returns=(0.01, 0.02, 0.03),
            window=2,
        )

        expected = 1.0 / (3.0 * sqrt(2.0))

        assert result == pytest.approx(
            (
                expected,
                expected,
            )
        )

    def test_calculates_multiple_rolling_windows(self) -> None:
        result = rolling_information_ratio(
            portfolio_returns=(0.05, 0.01, 0.06, 0.02),
            benchmark_returns=(0.01, 0.02, 0.03, 0.01),
            window=2,
        )

        active_returns = (0.04, -0.01, 0.03, 0.01)
        expected = []

        for start in range(len(active_returns) - 1):
            values = active_returns[start : start + 2]
            mean_value = sum(values) / 2

            variance = sum(
                (value - mean_value) ** 2
                for value in values
            )

            expected.append(mean_value / sqrt(variance))

        assert result == pytest.approx(tuple(expected))

    def test_calculates_for_full_sequence(self) -> None:
        result = rolling_information_ratio(
            portfolio_returns=(0.03, 0.01, 0.05),
            benchmark_returns=(0.01, 0.02, 0.03),
            window=3,
        )

        active_returns = (0.02, -0.01, 0.02)
        mean_active_return = sum(active_returns) / 3

        variance = sum(
            (value - mean_active_return) ** 2
            for value in active_returns
        ) / 2

        expected = mean_active_return / sqrt(variance)

        assert result == pytest.approx((expected,))

    def test_rejects_constant_active_returns(self) -> None:
        with pytest.raises(
            ValueError,
            match="tracking error is zero",
        ):
            rolling_information_ratio(
                portfolio_returns=(0.03, 0.04, 0.05),
                benchmark_returns=(0.01, 0.02, 0.03),
                window=2,
            )

    def test_rejects_different_length_sequences(self) -> None:
        with pytest.raises(
            ValueError,
            match="must have the same length",
        ):
            rolling_information_ratio(
                portfolio_returns=(0.01, 0.02),
                benchmark_returns=(0.01,),
                window=2,
            )

    def test_rejects_window_of_one(self) -> None:
        with pytest.raises(
            ValueError,
            match="window must be greater than 1",
        ):
            rolling_information_ratio(
                portfolio_returns=(0.01, 0.02),
                benchmark_returns=(0.01, 0.02),
                window=1,
            )

    def test_rejects_zero_window(self) -> None:
        with pytest.raises(
            ValueError,
            match="window must be greater than 1",
        ):
            rolling_information_ratio(
                portfolio_returns=(0.01, 0.02),
                benchmark_returns=(0.01, 0.02),
                window=0,
            )

    def test_rejects_window_larger_than_returns(self) -> None:
        with pytest.raises(
            ValueError,
            match="window cannot be greater",
        ):
            rolling_information_ratio(
                portfolio_returns=(0.01, 0.02),
                benchmark_returns=(0.01, 0.02),
                window=3,
            )

    def test_returns_tuple(self) -> None:
        result = rolling_information_ratio(
            portfolio_returns=(0.03, 0.01),
            benchmark_returns=(0.01, 0.02),
            window=2,
        )

        assert isinstance(result, tuple)