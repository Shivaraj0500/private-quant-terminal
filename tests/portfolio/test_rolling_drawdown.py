from __future__ import annotations

import pytest

from private_quant_terminal.portfolio.rolling_drawdown import (
    rolling_drawdown,
    rolling_max_drawdown,
)


class TestRollingDrawdown:
    def test_calculates_rolling_drawdown(self) -> None:
        result = rolling_drawdown(
            values=(100.0, 120.0, 90.0),
            window=2,
        )

        assert result == pytest.approx(
            (
                0.0,
                -0.25,
            )
        )

    def test_calculates_rolling_drawdown_for_multiple_windows(self) -> None:
        result = rolling_drawdown(
            values=(100.0, 120.0, 90.0, 110.0),
            window=3,
        )

        assert result == pytest.approx(
            (
                -0.25,
                -0.08333333333333333,
            )
        )

    def test_returns_zero_drawdown_when_window_ends_at_peak(self) -> None:
        result = rolling_drawdown(
            values=(100.0, 110.0, 120.0),
            window=2,
        )

        assert result == pytest.approx(
            (
                0.0,
                0.0,
            )
        )

    def test_calculates_rolling_max_drawdown(self) -> None:
        result = rolling_max_drawdown(
            values=(100.0, 120.0, 90.0),
            window=2,
        )

        assert result == pytest.approx(
            (
                0.0,
                -0.25,
            )
        )

    def test_calculates_rolling_max_drawdown_for_multiple_windows(self) -> None:
        result = rolling_max_drawdown(
            values=(100.0, 120.0, 90.0, 110.0),
            window=3,
        )

        assert result == pytest.approx(
            (
                -0.25,
                -0.25,
            )
        )

    def test_returns_zero_max_drawdown_for_rising_values(self) -> None:
        result = rolling_max_drawdown(
            values=(100.0, 110.0, 120.0),
            window=2,
        )

        assert result == pytest.approx(
            (
                0.0,
                0.0,
            )
        )

    def test_rejects_empty_values(self) -> None:
        with pytest.raises(ValueError, match="values must not be empty"):
            rolling_drawdown(
                values=(),
                window=1,
            )

    def test_rejects_zero_window(self) -> None:
        with pytest.raises(ValueError, match="window must be greater than zero"):
            rolling_drawdown(
                values=(100.0,),
                window=0,
            )

    def test_rejects_window_larger_than_values(self) -> None:
        with pytest.raises(
            ValueError,
            match="window must not exceed the number of values",
        ):
            rolling_max_drawdown(
                values=(100.0, 110.0),
                window=3,
            )

    def test_rejects_non_positive_values(self) -> None:
        with pytest.raises(ValueError, match="values must be greater than zero"):
            rolling_drawdown(
                values=(100.0, 0.0),
                window=2,
            )