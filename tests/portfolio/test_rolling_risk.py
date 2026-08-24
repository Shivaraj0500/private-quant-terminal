import pytest

from private_quant_terminal.portfolio.rolling_risk import (
    rolling_downside_volatility,
    rolling_sharpe_ratio,
    rolling_sortino_ratio,
)


class TestRollingRisk:
    def test_calculates_rolling_sharpe_ratio(self) -> None:
        result = rolling_sharpe_ratio(
            returns=(0.01, 0.03, 0.05),
            window=2,
        )

        assert result == pytest.approx(
            (
                2.0,
                4.0,
            )
        )

    def test_calculates_rolling_sharpe_with_risk_free_rate(
        self,
    ) -> None:
        result = rolling_sharpe_ratio(
            returns=(0.02, 0.04),
            window=2,
            risk_free_rate=0.01,
        )

        assert result == pytest.approx((2.0,))

    def test_calculates_rolling_downside_volatility(
        self,
    ) -> None:
        result = rolling_downside_volatility(
            returns=(0.02, -0.03, 0.01),
            window=2,
        )

        expected = (0.00045) ** 0.5

        assert result == pytest.approx(
            (
                expected,
                expected,
            )
        )

    def test_calculates_downside_volatility_with_target(
        self,
    ) -> None:
        result = rolling_downside_volatility(
            returns=(0.03, 0.01),
            window=2,
            target_return=0.02,
        )

        expected = (0.00005) ** 0.5

        assert result == pytest.approx((expected,))

    def test_calculates_rolling_sortino_ratio(self) -> None:
        result = rolling_sortino_ratio(
            returns=(0.02, -0.01, 0.03),
            window=2,
        )

        assert result == pytest.approx(
            (
                0.7071067811865476,
                1.414213562373095,
            )
        )

    def test_rejects_non_positive_window(self) -> None:
        with pytest.raises(
            ValueError,
            match="window must be greater than zero",
        ):
            rolling_sharpe_ratio(
                returns=(0.01, 0.02),
                window=0,
            )

    def test_rejects_window_larger_than_returns(self) -> None:
        with pytest.raises(
            ValueError,
            match=(
                "window cannot be greater than "
                "the number of returns"
            ),
        ):
            rolling_downside_volatility(
                returns=(0.01, 0.02),
                window=3,
            )

    def test_rejects_zero_volatility_for_sharpe(self) -> None:
        with pytest.raises(
            ValueError,
            match=(
                "rolling Sharpe ratio is undefined "
                "when volatility is zero"
            ),
        ):
            rolling_sharpe_ratio(
                returns=(0.02, 0.02),
                window=2,
            )

    def test_rejects_zero_downside_volatility_for_sortino(
        self,
    ) -> None:
        with pytest.raises(
            ValueError,
            match=(
                "rolling Sortino ratio is undefined "
                "when downside volatility is zero"
            ),
        ):
            rolling_sortino_ratio(
                returns=(0.02, 0.03),
                window=2,
            )