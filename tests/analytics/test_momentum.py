import pytest

from private_quant_terminal.analytics.momentum import (
    momentum,
    rate_of_change,
    relative_strength_index,
)


class TestMomentum:
    def test_calculates_momentum(self) -> None:
        result = momentum([10, 20, 30, 40, 50], period=3)

        assert result == 30

    def test_momentum_can_be_negative(self) -> None:
        result = momentum([50, 40, 30, 20, 10], period=3)

        assert result == -30

    def test_requires_enough_values(self) -> None:
        with pytest.raises(ValueError):
            momentum([10, 20], period=3)

    def test_rejects_invalid_period(self) -> None:
        with pytest.raises(ValueError):
            momentum([10, 20, 30], period=0)


class TestRateOfChange:
    def test_calculates_positive_rate_of_change(self) -> None:
        result = rate_of_change([100, 110, 120], period=2)

        assert result == pytest.approx(20.0)

    def test_calculates_negative_rate_of_change(self) -> None:
        result = rate_of_change([100, 90, 80], period=2)

        assert result == pytest.approx(-20.0)

    def test_requires_enough_values(self) -> None:
        with pytest.raises(ValueError):
            rate_of_change([100, 110], period=2)

    def test_rejects_zero_base_value(self) -> None:
        with pytest.raises(ValueError):
            rate_of_change([0, 10, 20], period=2)


class TestRelativeStrengthIndex:
    def test_rsi_for_consistent_gains_is_100(self) -> None:
        result = relative_strength_index(
            [10, 11, 12, 13, 14, 15],
            period=5,
        )

        assert result == pytest.approx(100.0)

    def test_rsi_for_consistent_losses_is_0(self) -> None:
        result = relative_strength_index(
            [15, 14, 13, 12, 11, 10],
            period=5,
        )

        assert result == pytest.approx(0.0)

    def test_rsi_requires_enough_values(self) -> None:
        with pytest.raises(ValueError):
            relative_strength_index([10, 11, 12], period=5)

    def test_rsi_rejects_invalid_period(self) -> None:
        with pytest.raises(ValueError):
            relative_strength_index([10, 11, 12, 13], period=0)