import pytest

from private_quant_terminal.portfolio.rolling_correlation import (
    rolling_correlation,
)


class TestRollingCorrelation:
    def test_calculates_perfect_positive_correlation(self) -> None:
        result = rolling_correlation(
            first_returns=(0.01, 0.02, 0.03),
            second_returns=(0.02, 0.04, 0.06),
            window=2,
        )

        assert result == pytest.approx((1.0, 1.0))

    def test_calculates_perfect_negative_correlation(self) -> None:
        result = rolling_correlation(
            first_returns=(0.01, 0.02, 0.03),
            second_returns=(0.03, 0.02, 0.01),
            window=2,
        )

        assert result == pytest.approx((-1.0, -1.0))

    def test_calculates_multiple_rolling_windows(self) -> None:
        result = rolling_correlation(
            first_returns=(0.01, 0.02, 0.03, 0.04),
            second_returns=(0.04, 0.03, 0.02, 0.01),
            window=3,
        )

        assert result == pytest.approx((-1.0, -1.0))

    def test_calculates_correlation_for_full_sequence(self) -> None:
        result = rolling_correlation(
            first_returns=(0.01, 0.02, 0.03),
            second_returns=(0.02, 0.04, 0.06),
            window=3,
        )

        assert result == pytest.approx((1.0,))

    def test_rejects_sequences_with_different_lengths(self) -> None:
        with pytest.raises(
            ValueError,
            match="must have the same length",
        ):
            rolling_correlation(
                first_returns=(0.01, 0.02),
                second_returns=(0.01,),
                window=2,
            )

    def test_rejects_window_of_one(self) -> None:
        with pytest.raises(
            ValueError,
            match="window must be greater than 1",
        ):
            rolling_correlation(
                first_returns=(0.01, 0.02),
                second_returns=(0.02, 0.03),
                window=1,
            )

    def test_rejects_zero_window(self) -> None:
        with pytest.raises(
            ValueError,
            match="window must be greater than 1",
        ):
            rolling_correlation(
                first_returns=(0.01, 0.02),
                second_returns=(0.02, 0.03),
                window=0,
            )

    def test_rejects_window_larger_than_sequence(self) -> None:
        with pytest.raises(
            ValueError,
            match="window cannot be greater",
        ):
            rolling_correlation(
                first_returns=(0.01, 0.02),
                second_returns=(0.02, 0.03),
                window=3,
            )

    def test_rejects_zero_variance_in_first_sequence(self) -> None:
        with pytest.raises(
            ValueError,
            match="zero variance",
        ):
            rolling_correlation(
                first_returns=(0.01, 0.01, 0.01),
                second_returns=(0.01, 0.02, 0.03),
                window=2,
            )

    def test_rejects_zero_variance_in_second_sequence(self) -> None:
        with pytest.raises(
            ValueError,
            match="zero variance",
        ):
            rolling_correlation(
                first_returns=(0.01, 0.02, 0.03),
                second_returns=(0.01, 0.01, 0.01),
                window=2,
            )