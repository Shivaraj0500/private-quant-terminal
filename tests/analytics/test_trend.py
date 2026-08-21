import pytest

from private_quant_terminal.analytics.trend import (
    TrendDirection,
    detect_crossover,
    detect_trend,
    ema,
    price_vs_ma,
    sma,
)


class TestMovingAverages:
    def test_sma_calculates_correctly(self) -> None:
        assert sma([10, 20, 30, 40, 50], period=3) == 40

    def test_sma_requires_enough_values(self) -> None:
        with pytest.raises(ValueError):
            sma([10, 20], period=3)

    def test_sma_rejects_invalid_period(self) -> None:
        with pytest.raises(ValueError):
            sma([10, 20, 30], period=0)

    def test_ema_calculates_correctly_for_single_value(self) -> None:
        assert ema([100], period=1) == 100

    def test_ema_returns_float(self) -> None:
        result = ema([10, 20, 30, 40, 50], period=3)

        assert isinstance(result, float)

    def test_ema_requires_enough_values(self) -> None:
        with pytest.raises(ValueError):
            ema([10, 20], period=3)


class TestTrendDetection:
    def test_detects_bullish_trend(self) -> None:
        result = detect_trend([10, 20, 30, 40, 50])

        assert result is TrendDirection.BULLISH

    def test_detects_bearish_trend(self) -> None:
        result = detect_trend([50, 40, 30, 20, 10])

        assert result is TrendDirection.BEARISH

    def test_detects_sideways_trend(self) -> None:
        result = detect_trend([10, 10, 10, 10, 10])

        assert result is TrendDirection.SIDEWAYS


class TestCrossover:
    def test_detects_bullish_crossover(self) -> None:
        result = detect_crossover(
            fast_previous=10,
            fast_current=20,
            slow_previous=15,
            slow_current=18,
        )

        assert result == "bullish"

    def test_detects_bearish_crossover(self) -> None:
        result = detect_crossover(
            fast_previous=20,
            fast_current=10,
            slow_previous=15,
            slow_current=12,
        )

        assert result == "bearish"

    def test_detects_no_crossover(self) -> None:
        result = detect_crossover(
            fast_previous=20,
            fast_current=25,
            slow_previous=10,
            slow_current=15,
        )

        assert result is None


class TestPriceVsMA:
    def test_price_above_ma(self) -> None:
        assert price_vs_ma(price=110, moving_average=100) == "above"

    def test_price_below_ma(self) -> None:
        assert price_vs_ma(price=90, moving_average=100) == "below"

    def test_price_equal_to_ma(self) -> None:
        assert price_vs_ma(price=100, moving_average=100) == "at"