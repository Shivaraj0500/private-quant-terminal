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

        assert result == pytest.approx(8.0 / 3.0)

    def test_uses_previous_close_in_true_range(self) -> None:
        result = average_true_range(
            highs=[10.0, 15.0],
            lows=[8.0, 13.0],
            closes=[9.0, 14.0],
            period=2,
        )

        assert result == pytest.approx(4.0)

    def test_uses_most_recent_periods(self) -> None:
        result = average_true_range(
            highs=[10.0, 12.0, 14.0, 16.0],
            lows=[8.0, 10.0, 12.0, 14.0],
            closes=[9.0, 11.0, 13.0, 15.0],
            period=2,
        )

        assert result == pytest.approx(3.0)

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

    def test_applies_annualization_factor(self) -> None:
        base_result = historical_volatility(
            closes=[100.0, 110.0, 100.0],
            period=2,
            annualization_factor=1,
        )

        annualized_result = historical_volatility(
            closes=[100.0, 110.0, 100.0],
            period=2,
            annualization_factor=4,
        )

        assert annualized_result == pytest.approx(
            base_result * 2
        )

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

    def test_calculates_zero_for_identical_values(self) -> None:
        result = standard_deviation(
            [5.0, 5.0, 5.0]
        )

        assert result == pytest.approx(0.0)

    def test_requires_at_least_two_values(self) -> None:
        with pytest.raises(
            ValueError,
            match="at least two values are required",
        ):
            standard_deviation([1.0])