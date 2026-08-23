import pytest

from private_quant_terminal.analytics.momentum import (
    momentum,
    rate_of_change,
    relative_strength_index,
)


class TestMomentum:
    def test_calculates_momentum(self) -> None:
        values = [10, 12, 15, 20]

        result = momentum(values, period=2)

        assert result == 8

    def test_momentum_can_be_negative(self) -> None:
        values = [20, 15, 12, 10]

        result = momentum(values, period=2)

        assert result == -5

    def test_requires_enough_values(self) -> None:
        with pytest.raises(ValueError):
            momentum([10, 20], period=2)

    def test_rejects_invalid_period(self) -> None:
        with pytest.raises(ValueError):
            momentum([10, 20, 30], period=0)


class TestRateOfChange:
    def test_calculates_positive_rate_of_change(self) -> None:
        values = [100, 110, 120]

        result = rate_of_change(values, period=2)

        assert result == pytest.approx(20.0)

    def test_calculates_negative_rate_of_change(self) -> None:
        values = [100, 90, 80]

        result = rate_of_change(values, period=2)

        assert result == pytest.approx(-20.0)

    def test_requires_enough_values(self) -> None:
        with pytest.raises(ValueError):
            rate_of_change([100, 110], period=2)

    def test_rejects_zero_base_value(self) -> None:
        with pytest.raises(ValueError):
            rate_of_change([0, 10], period=1)


class TestRelativeStrengthIndex:
    def test_rsi_for_consistent_gains_is_100(self) -> None:
        values = [10, 11, 12, 13, 14, 15]

        result = relative_strength_index(
            values,
            period=3,
        )

        assert result == pytest.approx(100.0)

    def test_rsi_for_consistent_losses_is_0(self) -> None:
        values = [15, 14, 13, 12, 11, 10]

        result = relative_strength_index(
            values,
            period=3,
        )

        assert result == pytest.approx(0.0)

    def test_rsi_requires_enough_values(self) -> None:
        with pytest.raises(ValueError):
            relative_strength_index(
                [10, 11, 12],
                period=3,
            )

    def test_rsi_rejects_invalid_period(self) -> None:
        with pytest.raises(ValueError):
            relative_strength_index(
                [10, 11, 12, 13],
                period=0,
            )

    def test_rsi_for_mixed_gains_and_losses(self) -> None:
        values = [10, 12, 11, 14]

        result = relative_strength_index(
            values,
            period=3,
        )

        assert result == pytest.approx(83.3333333333)