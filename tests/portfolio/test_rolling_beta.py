from __future__ import annotations

import pytest

from private_quant_terminal.portfolio.rolling_beta import rolling_beta


class TestRollingBeta:
    def test_calculates_rolling_beta(self) -> None:
        result = rolling_beta(
            portfolio_returns=(0.02, 0.04, 0.06),
            benchmark_returns=(0.01, 0.02, 0.03),
            window=2,
        )

        assert result == pytest.approx(
            (
                2.0,
                2.0,
            )
        )

    def test_calculates_single_full_window_beta(self) -> None:
        result = rolling_beta(
            portfolio_returns=(0.02, 0.04, 0.06),
            benchmark_returns=(0.01, 0.02, 0.03),
            window=3,
        )

        assert result == pytest.approx((2.0,))

    def test_calculates_negative_beta(self) -> None:
        result = rolling_beta(
            portfolio_returns=(-0.02, -0.04, -0.06),
            benchmark_returns=(0.01, 0.02, 0.03),
            window=3,
        )

        assert result == pytest.approx((-2.0,))

    def test_calculates_beta_for_single_return_windows(self) -> None:
        with pytest.raises(
            ValueError,
            match="benchmark returns must have non-zero variance",
        ):
            rolling_beta(
                portfolio_returns=(0.01, 0.02),
                benchmark_returns=(0.03, 0.04),
                window=1,
            )

    def test_rejects_mismatched_return_lengths(self) -> None:
        with pytest.raises(
            ValueError,
            match="portfolio and benchmark returns must have equal lengths",
        ):
            rolling_beta(
                portfolio_returns=(0.01, 0.02),
                benchmark_returns=(0.01,),
                window=1,
            )

    def test_rejects_empty_returns(self) -> None:
        with pytest.raises(
            ValueError,
            match="returns cannot be empty",
        ):
            rolling_beta(
                portfolio_returns=(),
                benchmark_returns=(),
                window=1,
            )

    def test_rejects_zero_window(self) -> None:
        with pytest.raises(
            ValueError,
            match="window must be greater than zero",
        ):
            rolling_beta(
                portfolio_returns=(0.01, 0.02),
                benchmark_returns=(0.01, 0.02),
                window=0,
            )

    def test_rejects_negative_window(self) -> None:
        with pytest.raises(
            ValueError,
            match="window must be greater than zero",
        ):
            rolling_beta(
                portfolio_returns=(0.01, 0.02),
                benchmark_returns=(0.01, 0.02),
                window=-1,
            )

    def test_rejects_window_larger_than_returns(self) -> None:
        with pytest.raises(
            ValueError,
            match="window cannot be greater than the number of returns",
        ):
            rolling_beta(
                portfolio_returns=(0.01, 0.02),
                benchmark_returns=(0.01, 0.02),
                window=3,
            )

    def test_rejects_zero_benchmark_variance(self) -> None:
        with pytest.raises(
            ValueError,
            match="benchmark returns must have non-zero variance",
        ):
            rolling_beta(
                portfolio_returns=(0.01, 0.02, 0.03),
                benchmark_returns=(0.02, 0.02, 0.02),
                window=2,
            )