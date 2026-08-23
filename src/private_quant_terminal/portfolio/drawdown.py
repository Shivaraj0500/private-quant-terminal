from dataclasses import dataclass


@dataclass(frozen=True)
class DrawdownMetrics:
    """Portfolio drawdown metrics."""

    peak_value: float
    current_value: float
    drawdown: float
    drawdown_percent: float


class DrawdownCalculator:
    """Calculate drawdown metrics for a portfolio."""

    def calculate(
        self,
        peak_value: float,
        current_value: float,
    ) -> DrawdownMetrics:
        """Calculate absolute and percentage drawdown."""
        if peak_value <= 0:
            raise ValueError(
                "peak_value must be greater than zero"
            )

        drawdown = max(
            0.0,
            peak_value - current_value,
        )

        drawdown_percent = (
            drawdown / peak_value
        ) * 100

        return DrawdownMetrics(
            peak_value=peak_value,
            current_value=current_value,
            drawdown=drawdown,
            drawdown_percent=drawdown_percent,
        )
