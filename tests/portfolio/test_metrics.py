from math import isclose

from private_quant_terminal.portfolio.metrics import (
    PortfolioMetrics,
    calculate_metrics,
)


class TestCalculateMetrics:
    def test_calculates_metrics_for_multiple_returns(
        self,
    ) -> None:
        result = calculate_metrics(
            (
                0.10,
                -0.05,
                0.15,
                0.00,
            )
        )

        assert result.total_return == 0.20
        assert result.average_return == 0.05
        assert result.best_return == 0.15
        assert result.worst_return == -0.05
        assert isclose(
            result.volatility,
            0.0790569415,
            rel_tol=1e-9,
        )

    def test_calculates_metrics_for_single_return(
        self,
    ) -> None:
        result = calculate_metrics((0.10,))

        assert result == PortfolioMetrics(
            total_return=0.10,
            average_return=0.10,
            best_return=0.10,
            worst_return=0.10,
            volatility=0.0,
        )

    def test_returns_zero_metrics_for_empty_returns(
        self,
    ) -> None:
        result = calculate_metrics(())

        assert result == PortfolioMetrics(
            total_return=0.0,
            average_return=0.0,
            best_return=0.0,
            worst_return=0.0,
            volatility=0.0,
        )