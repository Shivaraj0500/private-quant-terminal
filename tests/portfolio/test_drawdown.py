import pytest

from private_quant_terminal.portfolio.drawdown import (
    DrawdownCalculator,
    DrawdownMetrics,
)


class TestDrawdownCalculator:
    def test_calculates_drawdown(self) -> None:
        calculator = DrawdownCalculator()

        result = calculator.calculate(
            peak_value=100000.0,
            current_value=85000.0,
        )

        assert isinstance(result, DrawdownMetrics)
        assert result.peak_value == 100000.0
        assert result.current_value == 85000.0
        assert result.drawdown == 15000.0
        assert result.drawdown_percent == 15.0

    def test_returns_zero_when_current_value_is_peak(
        self,
    ) -> None:
        calculator = DrawdownCalculator()

        result = calculator.calculate(
            peak_value=100000.0,
            current_value=100000.0,
        )

        assert result.drawdown == 0.0
        assert result.drawdown_percent == 0.0

    def test_returns_zero_when_current_value_exceeds_peak(
        self,
    ) -> None:
        calculator = DrawdownCalculator()

        result = calculator.calculate(
            peak_value=100000.0,
            current_value=110000.0,
        )

        assert result.drawdown == 0.0
        assert result.drawdown_percent == 0.0

    def test_rejects_non_positive_peak_value(
        self,
    ) -> None:
        calculator = DrawdownCalculator()

        with pytest.raises(
            ValueError,
            match="peak_value must be greater than zero",
        ):
            calculator.calculate(
                peak_value=0.0,
                current_value=1000.0,
            )
