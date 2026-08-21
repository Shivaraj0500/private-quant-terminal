import pytest

from private_quant_terminal.analytics.volume import (
    on_balance_volume,
    relative_volume,
    volume_rate_of_change,
    volume_sma,
)


class TestVolumeSMA:

    def test_calculates_volume_sma(self) -> None:
        volumes = [100.0, 200.0, 300.0]

        result = volume_sma(
            volumes,
            period=3,
        )

        assert result == pytest.approx(200.0)

    def test_uses_most_recent_periods(self) -> None:
        volumes = [100.0, 200.0, 300.0, 400.0]

        result = volume_sma(
            volumes,
            period=2,
        )

        assert result == pytest.approx(350.0)

    def test_rejects_invalid_period(self) -> None:
        with pytest.raises(ValueError):
            volume_sma(
                [100.0, 200.0],
                period=0,
            )

    def test_requires_enough_data(self) -> None:
        with pytest.raises(ValueError):
            volume_sma(
                [100.0, 200.0],
                period=3,
            )


class TestRelativeVolume:

    def test_calculates_relative_volume(self) -> None:
        volumes = [
            100.0,
            200.0,
            300.0,
            400.0,
        ]

        # Previous three average:
        # (100 + 200 + 300) / 3 = 200
        #
        # RVOL = 400 / 200 = 2

        result = relative_volume(
            volumes,
            period=3,
        )

        assert result == pytest.approx(2.0)

    def test_returns_one_for_average_volume(self) -> None:
        volumes = [
            100.0,
            100.0,
            100.0,
        ]

        result = relative_volume(
            volumes,
            period=2,
        )

        assert result == pytest.approx(1.0)

    def test_requires_enough_data(self) -> None:
        with pytest.raises(ValueError):
            relative_volume(
                [100.0, 200.0],
                period=2,
            )

    def test_rejects_zero_average_volume(self) -> None:
        with pytest.raises(ValueError):
            relative_volume(
                [0.0, 0.0, 100.0],
                period=2,
            )


class TestVolumeRateOfChange:

    def test_calculates_volume_rate_of_change(self) -> None:
        volumes = [
            100.0,
            150.0,
            200.0,
        ]

        # (200 - 100) / 100 * 100 = 100%

        result = volume_rate_of_change(
            volumes,
            period=2,
        )

        assert result == pytest.approx(100.0)

    def test_calculates_negative_volume_change(self) -> None:
        volumes = [
            200.0,
            100.0,
        ]

        result = volume_rate_of_change(
            volumes,
            period=1,
        )

        assert result == pytest.approx(-50.0)

    def test_requires_enough_data(self) -> None:
        with pytest.raises(ValueError):
            volume_rate_of_change(
                [100.0],
                period=1,
            )

    def test_rejects_zero_previous_volume(self) -> None:
        with pytest.raises(ValueError):
            volume_rate_of_change(
                [0.0, 100.0],
                period=1,
            )


class TestOnBalanceVolume:

    def test_calculates_on_balance_volume(self) -> None:
        closes = [
            100.0,
            105.0,
            103.0,
            110.0,
        ]

        volumes = [
            1000.0,
            2000.0,
            1500.0,
            3000.0,
        ]

        # Start: 0
        #
        # 105 > 100:
        # +2000 = 2000
        #
        # 103 < 105:
        # -1500 = 500
        #
        # 110 > 103:
        # +3000 = 3500

        result = on_balance_volume(
            closes,
            volumes,
        )

        assert result == pytest.approx(3500.0)

    def test_equal_close_does_not_change_obv(self) -> None:
        closes = [
            100.0,
            100.0,
            105.0,
        ]

        volumes = [
            1000.0,
            2000.0,
            3000.0,
        ]

        # Equal close: no change
        # Higher close: +3000

        result = on_balance_volume(
            closes,
            volumes,
        )

        assert result == pytest.approx(3000.0)

    def test_requires_matching_lengths(self) -> None:
        with pytest.raises(ValueError):
            on_balance_volume(
                [100.0, 105.0],
                [1000.0],
            )

    def test_requires_at_least_two_periods(self) -> None:
        with pytest.raises(ValueError):
            on_balance_volume(
                [100.0],
                [1000.0],
            )