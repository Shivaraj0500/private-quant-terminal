import pytest

from private_quant_terminal.analytics.indicators import (
    atr,
    ema,
    rsi,
    sma,
)


class TestSMA:
    def test_returns_expected_values(self) -> None:
        prices = [10, 20, 30, 40, 50]

        result = sma(prices, period=3)

        assert result == [20.0, 30.0, 40.0]

    def test_requires_positive_period(self) -> None:
        with pytest.raises(ValueError):
            sma([10, 20, 30], period=0)

    def test_requires_enough_values(self) -> None:
        with pytest.raises(ValueError):
            sma([10, 20], period=3)


class TestEMA:
    def test_returns_expected_values(self) -> None:
        prices = [10, 20, 30, 40]

        result = ema(prices, period=3)

        assert result == pytest.approx(
            [10.0, 15.0, 22.5, 31.25]
        )

    def test_requires_positive_period(self) -> None:
        with pytest.raises(ValueError):
            ema([10, 20, 30], period=0)

    def test_requires_enough_values(self) -> None:
        with pytest.raises(ValueError):
            ema([10, 20], period=3)


class TestRSI:
    def test_returns_100_for_continuous_gains(self) -> None:
        prices = [10, 11, 12, 13, 14, 15]

        result = rsi(prices, period=3)

        assert result[-1] == pytest.approx(100.0)

    def test_returns_0_for_continuous_losses(self) -> None:
        prices = [15, 14, 13, 12, 11, 10]

        result = rsi(prices, period=3)

        assert result[-1] == pytest.approx(0.0)

    def test_requires_positive_period(self) -> None:
        with pytest.raises(ValueError):
            rsi([10, 11, 12, 13], period=0)

    def test_requires_enough_values(self) -> None:
        with pytest.raises(ValueError):
            rsi([10, 11, 12], period=3)


class TestATR:
    def test_returns_expected_atr(self) -> None:
        highs = [12, 13, 15, 16]
        lows = [10, 11, 12, 14]
        closes = [11, 12, 14, 15]

        result = atr(
            highs=highs,
            lows=lows,
            closes=closes,
            period=2,
        )

        assert result == pytest.approx([2.0, 2.5, 2.25])

    def test_requires_matching_lengths(self) -> None:
        with pytest.raises(ValueError):
            atr(
                highs=[12, 13],
                lows=[10],
                closes=[11, 12],
                period=2,
            )

    def test_requires_positive_period(self) -> None:
        with pytest.raises(ValueError):
            atr(
                highs=[12, 13, 14],
                lows=[10, 11, 12],
                closes=[11, 12, 13],
                period=0,
            )

    def test_requires_enough_values(self) -> None:
        with pytest.raises(ValueError):
            atr(
                highs=[12, 13],
                lows=[10, 11],
                closes=[11, 12],
                period=3,
            )