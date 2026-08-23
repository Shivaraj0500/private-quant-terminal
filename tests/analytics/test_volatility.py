import pytest

from private_quant_terminal.analytics.volatility import (
    average_true_range,
    historical_volatility,
    standard_deviation,
)


class TestAverageTrueRange:
    def test_calculates_average_true_range(self) -> None:
        result = average_true_range(
            highs=[10.0, 12.0, 14.0],
            lows=[8.0, 10.0, 12.0],
            closes=[9.0, 11.0, 13.0],
            period=3,
        )

        # TR values:
        # First = 10 - 8 = 2
        # Second = max(12 - 10, abs(12 - 9), abs(10 - 9)) = 3
        # Third = max(14 - 12, abs(14 - 11), abs(12 - 11)) = 3
        # ATR = (2 + 3 + 3) / 3
        assert result == pytest.approx(8.0 / 3.0)

    def test_uses_previous_close_in_true_range(self) -> None:
        result = average_true_range(
            highs=[10.0, 15.0],
            lows=[8.0, 13.0],
            closes=[9.0, 14.0],
            period=2,
        )

        # First TR = 10 - 8 = 2
        # Second TR = max(15 - 13, abs(15 - 9), abs(13 - 9)) = 6
        # ATR = (2 + 6) / 2 = 4
        assert result == 4.0

    def test_uses_most_recent_periods(self) -> None:
        result = average_true_range(
            highs=[10.0, 12.0, 14.0, 16.0],
            lows=[8.0, 10.0, 12.0, 14.0],
            closes=[9.0, 11.0, 13.0, 15.0],
            period=2,
        )

        # TR values are 2, 3, 3, 3.
        # The most recent two True Range values are 3 and 3.
        # ATR = (3 + 3) / 2 = 3.
        assert result == 3.0

    def test_requires_matching_lengths(self) -> None:
        with pytest.raises(
            ValueError,
            match="matching lengths",
        ):
            average_true_range(
                highs=[10.0, 12.0],
                lows=[8.0],
                closes=[9.0, 11.0],
                period=1,
            )

    def test_rejects_invalid_period(self) -> None:
        with pytest.raises(
            ValueError,
            match="period must be greater than zero",
        ):
            average_true_range(
                highs=[10.0],
                lows=[8.0],
                closes=[9.0],
                period=0,
            )

    def test_requires_enough_data(self) -> None:
        with pytest.raises(
            ValueError,
            match="not enough price data",
        ):
            average_true_range(
                highs=[10.0],
                lows=[8.0],
                closes=[9.0],
                period=2,
            )


class TestHistoricalVolatility:
    def test_calculates_historical_volatility(self) -> None:
        result = historical_volatility(
            closes=[100.0, 110.0, 121.0],
            period=2,
            annualization_factor=1,
        )

        assert result == pytest.approx(0.0)

    def test_requires_enough_closes(self) -> None:
        with pytest.raises(
            ValueError,
            match="not enough closing prices",
        ):
            historical_volatility(
                closes=[100.0, 110.0],
                period=2,
            )

    def test_rejects_non_positive_close(self) -> None:
        with pytest.raises(
            ValueError,
            match="close prices must be greater than zero",
        ):
            historical_volatility(
                closes=[100.0, 0.0, 110.0],
                period=2,
            )

    def test_rejects_invalid_period(self) -> None:
        with pytest.raises(
            ValueError,
            match="period must be greater than zero",
        ):
            historical_volatility(
                closes=[100.0, 110.0],
                period=0,
            )

    def test_rejects_invalid_annualization_factor(self) -> None:
        with pytest.raises(
            ValueError,
            match="annualization_factor must be greater than zero",
        ):
            historical_volatility(
                closes=[100.0, 110.0],
                period=1,
                annualization_factor=0,
            )


class TestStandardDeviation:
    def test_calculates_population_standard_deviation(self) -> None:
        result = standard_deviation(
            [2.0, 4.0, 4.0, 4.0, 5.0, 5.0, 7.0, 9.0]
        )

        assert result == pytest.approx(2.0)

    def test_requires_at_least_two_values(self) -> None:
        with pytest.raises(
            ValueError,
            match="at least two values are required",
        ):
            standard_deviation([100.0])