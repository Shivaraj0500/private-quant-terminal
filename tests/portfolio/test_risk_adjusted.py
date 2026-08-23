from math import isclose

from private_quant_terminal.portfolio.risk_adjusted import (
    RiskAdjustedMetrics,
    calculate_risk_adjusted_metrics,
)


class TestCalculateRiskAdjustedMetrics:
    def test_calculates_risk_adjusted_metrics(
        self,
    ) -> None:
        result = calculate_risk_adjusted_metrics(
            (
                0.10,
                -0.05,
                0.15,
                0.00,
            ),
            max_drawdown=0.10,
        )

        assert isclose(
            result.sharpe_ratio,
            0.6324555320,
            rel_tol=1e-9,
        )
        assert isclose(
            result.downside_deviation,
            0.025,
            rel_tol=1e-9,
        )
        assert isclose(
            result.sortino_ratio,
            2.0,
            rel_tol=1e-9,
        )
        assert isclose(
            result.calmar_ratio,
            2.0,
            rel_tol=1e-9,
        )

    def test_uses_risk_free_rate_and_target_return(
        self,
    ) -> None:
        result = calculate_risk_adjusted_metrics(
            (
                0.10,
                0.00,
            ),
            risk_free_rate=0.02,
            target_return=0.01,
            max_drawdown=-0.05,
        )

        assert result.downside_deviation > 0.0
        assert result.sharpe_ratio > 0.0
        assert result.sortino_ratio > 0.0
        assert result.calmar_ratio == 2.0

    def test_returns_zero_ratios_when_returns_are_empty(
        self,
    ) -> None:
        result = calculate_risk_adjusted_metrics(
            (),
        )

        assert result == RiskAdjustedMetrics(
            sharpe_ratio=0.0,
            sortino_ratio=0.0,
            downside_deviation=0.0,
            calmar_ratio=0.0,
        )

    def test_returns_zero_ratios_when_volatility_and_downside_are_zero(
        self,
    ) -> None:
        result = calculate_risk_adjusted_metrics(
            (
                0.10,
                0.10,
            ),
        )

        assert result.sharpe_ratio == 0.0
        assert result.sortino_ratio == 0.0
        assert result.downside_deviation == 0.0
        assert result.calmar_ratio == 0.0