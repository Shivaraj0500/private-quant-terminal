import math

import pytest

from private_quant_terminal.analytics.volatility import (
    average_true_range,
    historical_volatility,
    standard_deviation,
)


class TestAverageTrueRange:

    def test_calculates_average_true_range(self) -> None:
        """
        Expected True Ranges:

        Period 1:
            High = 12
            Low = 9
            TR = 12 - 9 = 3

        Period 2:
            High = 14
            Low = 10
            Previous Close = 10

            TR = max(
                14 - 10,
                abs(14 - 10),
                abs(10 - 10),
            ) = 4

        Period 3:
            High = 15
            Low = 11
            Previous Close = 13

            TR = max(
                15 - 11,
                abs(15 - 13),
                abs(11 - 13),
            ) = 4

        ATR = (3 + 4 + 4) / 3
            = 11 / 3
        """

        highs = [12, 14, 15]
        lows = [9, 10, 11]
        closes = [10, 13, 14]

        result = average_true_range(
            highs,
            lows,
            closes,
            period=3,
        )

        assert result == pytest.approx(11 / 3)

    def test_uses_previous_close_in_true_range(self) -> None:
        highs = [10, 15]
        lows = [8, 12]
        closes = [9, 10]

        # TR1 = 10 - 8 = 2
        # TR2 = max(15 - 12, abs(15 - 9), abs(12 - 9))
        #     = max(3, 6, 3)
        #     = 6
        # ATR = (2 + 6) / 2 = 4

        result = average_true_range(
            highs,
            lows,
            closes,
            period=2,
        )

        assert result == pytest.approx(4.0)

    def test_uses_most_recent_periods(self) -> None:
        highs = [10, 11, 12, 14]
        lows = [8, 9, 10, 11]
        closes = [9, 10, 11, 13]

        # TR values:
        # 2, 2, 2, 3
        #
        # Last 3 TR values:
        # 2, 2, 3
        #
        # ATR = 7 / 3

        result = average_true_range(
            highs,
            lows,
            closes,
            period=3,
        )

        assert result == pytest.approx(7 / 3)

    def test_requires_matching_lengths(self) -> None:
        with pytest.raises(ValueError):
            average_true_range(
                [12, 13],
                [9],
                [10, 11],
                period=2,
            )

    def test_rejects_invalid_period(self) -> None:
        with pytest.raises(ValueError):
            average_true_range(
                [12, 13],
                [9, 10],
                [10, 11],
                period=0,
            )

    def test_requires_enough_data(self) -> None:
        with pytest.raises(ValueError):
            average_true_range(
                [12, 13],
                [9, 10],
                [10, 11],
                period=3,
            )


class TestHistoricalVolatility:

    def test_calculates_historical_volatility(self) -> None:
        closes = [100.0, 110.0, 121.0]

        log_return_1 = math.log(110.0 / 100.0)
        log_return_2 = math.log(121.0 / 110.0)

        mean = (
            log_return_1 + log_return_2
        ) / 2

        variance = (
            (log_return_1 - mean) ** 2
            + (log_return_2 - mean) ** 2
        ) / 2

        expected = math.sqrt(variance) * math.sqrt(252)

        result = historical_volatility(
            closes,
            period=2,
            annualization_factor=252,
        )

        assert result == pytest.approx(expected)

    def test_requires_enough_closes(self) -> None:
        with pytest.raises(ValueError):
            historical_volatility(
                [100.0, 101.0],
                period=2,
            )

    def test_rejects_non_positive_close(self) -> None:
        with pytest.raises(ValueError):
            historical_volatility(
                [100.0, 0.0, 102.0],
                period=2,
            )


class TestStandardDeviation:

    def test_calculates_population_standard_deviation(self) -> None:
        result = standard_deviation([2.0, 4.0, 4.0, 4.0])

        expected = math.sqrt(
            (
                (2.0 - 3.5) ** 2
                + (4.0 - 3.5) ** 2
                + (4.0 - 3.5) ** 2
                + (4.0 - 3.5) ** 2
            ) / 4
        )

        assert result == pytest.approx(expected)

    def test_requires_at_least_two_values(self) -> None:
        with pytest.raises(ValueError):
            standard_deviation([1.0])