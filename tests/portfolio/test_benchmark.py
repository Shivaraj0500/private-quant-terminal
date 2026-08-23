import pytest

from private_quant_terminal.portfolio.benchmark import (
    active_return,
    active_returns,
    information_ratio,
    tracking_error,
)


class TestBenchmark:
    def test_calculates_active_return(self) -> None:
        assert active_return(
            portfolio_return=0.12,
            benchmark_return=0.08,
        ) == pytest.approx(0.04)

    def test_calculates_negative_active_return(self) -> None:
        assert active_return(
            portfolio_return=0.05,
            benchmark_return=0.08,
        ) == pytest.approx(-0.03)

    def test_calculates_active_return_series(self) -> None:
        result = active_returns(
            portfolio_returns=(0.10, 0.08, 0.12),
            benchmark_returns=(0.08, 0.06, 0.09),
        )

        assert result == pytest.approx(
            (0.02, 0.02, 0.03)
        )

    def test_rejects_mismatched_return_series(self) -> None:
        with pytest.raises(
            ValueError,
            match=(
                "Portfolio and benchmark return series "
                "must have the same length"
            ),
        ):
            active_returns(
                portfolio_returns=(0.10, 0.08),
                benchmark_returns=(0.08,),
            )

    def test_calculates_zero_tracking_error_for_identical_active_returns(
        self,
    ) -> None:
        result = tracking_error(
            portfolio_returns=(12.0, 14.0, 16.0),
            benchmark_returns=(10.0, 12.0, 14.0),
        )

        assert result == pytest.approx(0.0)

    def test_calculates_tracking_error(self) -> None:
        result = tracking_error(
            portfolio_returns=(0.10, 0.05, 0.15),
            benchmark_returns=(0.08, 0.06, 0.09),
        )

        assert result == pytest.approx(
            0.028674417556808753
        )

    def test_rejects_empty_series_for_tracking_error(self) -> None:
        with pytest.raises(
            ValueError,
            match=(
                "At least one portfolio and benchmark return "
                "is required"
            ),
        ):
            tracking_error(
                portfolio_returns=(),
                benchmark_returns=(),
            )

    def test_calculates_information_ratio(self) -> None:
        result = information_ratio(
            portfolio_returns=(0.10, 0.05, 0.15),
            benchmark_returns=(0.08, 0.06, 0.09),
        )

        assert result == pytest.approx(
            0.8137334712067351
        )

    def test_rejects_zero_tracking_error_for_information_ratio(
        self,
    ) -> None:
        with pytest.raises(
            ValueError,
            match=(
                "Information ratio is undefined when "
                "tracking error is zero"
            ),
        ):
            information_ratio(
                portfolio_returns=(12.0, 14.0, 16.0),
                benchmark_returns=(10.0, 12.0, 14.0),
            )

    def test_rejects_empty_series_for_information_ratio(
        self,
    ) -> None:
        with pytest.raises(
            ValueError,
            match=(
                "At least one portfolio and benchmark return "
                "is required"
            ),
        ):
            information_ratio(
                portfolio_returns=(),
                benchmark_returns=(),
            )