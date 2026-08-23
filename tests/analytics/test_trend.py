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
        result = sma(
            [10.0, 20.0, 30.0, 40.0, 50.0],
            period=3,
        )

        assert result == 40.0

    def test_sma_requires_enough_values(self) -> None:
        with pytest.raises(
            ValueError,
            match="values must contain at least period items",
        ):
            sma(
                [10.0, 20.0],
                period=3,
            )

    def test_sma_rejects_invalid_period(self) -> None:
        with pytest.raises(
            ValueError,
            match="period must be greater than zero",
        ):
            sma(
                [10.0, 20.0, 30.0],
                period=0,
            )

    def test_ema_calculates_correctly_for_single_value(self) -> None:
        result = ema(
            [100.0],
            period=1,
        )

        assert result == 100.0

    def test_ema_calculates_correctly_for_multiple_values(self) -> None:
        result = ema(
            [10.0, 20.0, 30.0],
            period=3,
        )

        assert result == 22.5

    def test_ema_returns_float(self) -> None:
        result = ema(
            [10.0, 20.0, 30.0],
            period=3,
        )

        assert isinstance(result, float)

    def test_ema_requires_enough_values(self) -> None:
        with pytest.raises(
            ValueError,
            match="values must contain at least period items",
        ):
            ema(
                [10.0, 20.0],
                period=3,
            )

    def test_ema_rejects_invalid_period(self) -> None:
        with pytest.raises(
            ValueError,
            match="period must be greater than zero",
        ):
            ema(
                [10.0, 20.0, 30.0],
                period=0,
            )


class TestTrendDetection:
    def test_detects_bullish_trend(self) -> None:
        result = detect_trend(
            [100.0, 105.0, 110.0]
        )

        assert result == TrendDirection.BULLISH

    def test_detects_bearish_trend(self) -> None:
        result = detect_trend(
            [110.0, 105.0, 100.0]
        )

        assert result == TrendDirection.BEARISH

    def test_detects_sideways_trend(self) -> None:
        result = detect_trend(
            [100.0, 105.0, 100.0]
        )

        assert result == TrendDirection.SIDEWAYS

    def test_requires_at_least_two_values(self) -> None:
        with pytest.raises(
            ValueError,
            match="values must contain at least two items",
        ):
            detect_trend(
                [100.0]
            )


class TestCrossover:
    def test_detects_bullish_crossover(self) -> None:
        result = detect_crossover(
            fast_previous=10.0,
            fast_current=12.0,
            slow_previous=11.0,
            slow_current=11.0,
        )

        assert result == "bullish"

    def test_detects_bearish_crossover(self) -> None:
        result = detect_crossover(
            fast_previous=12.0,
            fast_current=10.0,
            slow_previous=11.0,
            slow_current=11.0,
        )

        assert result == "bearish"

    def test_detects_no_crossover(self) -> None:
        result = detect_crossover(
            fast_previous=12.0,
            fast_current=13.0,
            slow_previous=10.0,
            slow_current=11.0,
        )

        assert result is None


class TestPriceVsMA:
    def test_price_above_ma(self) -> None:
        result = price_vs_ma(
            price=110.0,
            moving_average=100.0,
        )

        assert result == "above"

    def test_price_below_ma(self) -> None:
        result = price_vs_ma(
            price=90.0,
            moving_average=100.0,
        )

        assert result == "below"

    def test_price_equal_to_ma(self) -> None:
        result = price_vs_ma(
            price=100.0,
            moving_average=100.0,
        )

        assert result == "at"