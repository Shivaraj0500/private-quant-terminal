import pytest

from private_quant_terminal.analytics.signals import (
    SignalDirection,
    SignalResult,
    generate_signal,
    momentum_score,
    trend_score,
    volatility_score,
    volume_score,
)


class TestTrendScore:

    def test_returns_bullish_for_short_ma_above_long_ma(self) -> None:
        assert trend_score(110.0, 100.0) == 1

    def test_returns_bearish_for_short_ma_below_long_ma(self) -> None:
        assert trend_score(90.0, 100.0) == -1

    def test_returns_neutral_for_equal_moving_averages(self) -> None:
        assert trend_score(100.0, 100.0) == 0


class TestMomentumScore:

    def test_returns_bullish_for_oversold_rsi(self) -> None:
        assert momentum_score(25.0) == 1

    def test_returns_bearish_for_overbought_rsi(self) -> None:
        assert momentum_score(75.0) == -1

    def test_returns_neutral_for_normal_rsi(self) -> None:
        assert momentum_score(50.0) == 0

    def test_accepts_rsi_at_zero(self) -> None:
        assert momentum_score(0.0) == 1

    def test_accepts_rsi_at_one_hundred(self) -> None:
        assert momentum_score(100.0) == -1

    def test_rejects_negative_rsi(self) -> None:
        with pytest.raises(ValueError):
            momentum_score(-1.0)

    def test_rejects_rsi_above_one_hundred(self) -> None:
        with pytest.raises(ValueError):
            momentum_score(101.0)

    def test_rejects_invalid_threshold_order(self) -> None:
        with pytest.raises(ValueError):
            momentum_score(
                50.0,
                oversold=70.0,
                overbought=30.0,
            )


class TestVolumeScore:

    def test_returns_positive_for_above_average_volume(self) -> None:
        assert volume_score(1.5) == 1

    def test_returns_neutral_for_average_volume(self) -> None:
        assert volume_score(1.0) == 0

    def test_returns_negative_for_below_average_volume(self) -> None:
        assert volume_score(0.5) == -1

    def test_rejects_negative_relative_volume(self) -> None:
        with pytest.raises(ValueError):
            volume_score(-0.1)


class TestVolatilityScore:

    def test_returns_positive_for_lower_volatility(self) -> None:
        assert volatility_score(10.0, 20.0) == 1

    def test_returns_negative_for_higher_volatility(self) -> None:
        assert volatility_score(30.0, 20.0) == -1

    def test_returns_neutral_for_equal_volatility(self) -> None:
        assert volatility_score(20.0, 20.0) == 0

    def test_rejects_negative_current_volatility(self) -> None:
        with pytest.raises(ValueError):
            volatility_score(-1.0, 10.0)

    def test_rejects_negative_average_volatility(self) -> None:
        with pytest.raises(ValueError):
            volatility_score(10.0, -1.0)


class TestGenerateSignal:

    def test_generates_strong_buy(self) -> None:
        result = generate_signal(
            short_moving_average=110.0,
            long_moving_average=100.0,
            rsi=20.0,
            relative_volume_value=1.5,
            current_volatility=10.0,
            average_volatility=20.0,
        )

        assert isinstance(result, SignalResult)
        assert result.direction == SignalDirection.STRONG_BUY
        assert result.score == 4

    def test_generates_buy(self) -> None:
        result = generate_signal(
            short_moving_average=110.0,
            long_moving_average=100.0,
            rsi=50.0,
            relative_volume_value=1.5,
            current_volatility=30.0,
            average_volatility=20.0,
        )

        assert result.direction == SignalDirection.BUY
        assert result.score == 1

    def test_generates_hold(self) -> None:
        result = generate_signal(
            short_moving_average=100.0,
            long_moving_average=100.0,
            rsi=50.0,
            relative_volume_value=1.0,
            current_volatility=20.0,
            average_volatility=20.0,
        )

        assert result.direction == SignalDirection.HOLD
        assert result.score == 0

    def test_generates_sell(self) -> None:
        result = generate_signal(
            short_moving_average=90.0,
            long_moving_average=100.0,
            rsi=50.0,
            relative_volume_value=1.5,
            current_volatility=30.0,
            average_volatility=20.0,
        )

        assert result.direction == SignalDirection.SELL
        assert result.score == -1

    def test_generates_strong_sell(self) -> None:
        result = generate_signal(
            short_moving_average=90.0,
            long_moving_average=100.0,
            rsi=80.0,
            relative_volume_value=0.5,
            current_volatility=30.0,
            average_volatility=20.0,
        )

        assert result.direction == SignalDirection.STRONG_SELL
        assert result.score == -4

    def test_preserves_component_scores(self) -> None:
        result = generate_signal(
            short_moving_average=110.0,
            long_moving_average=100.0,
            rsi=20.0,
            relative_volume_value=1.5,
            current_volatility=10.0,
            average_volatility=20.0,
        )

        assert result.trend_score == 1
        assert result.momentum_score == 1
        assert result.volume_score == 1
        assert result.volatility_score == 1