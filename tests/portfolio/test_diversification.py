import pytest

from private_quant_terminal.portfolio.diversification import (
    diversification_score,
    effective_number_of_positions,
    herfindahl_index,
    largest_weight,
)


class TestHerfindahlIndex:
    def test_returns_zero_for_empty_weights(
        self,
    ) -> None:
        assert herfindahl_index(()) == 0.0

    def test_returns_zero_for_all_zero_weights(
        self,
    ) -> None:
        assert herfindahl_index(
            (0.0, 0.0),
        ) == 0.0

    def test_calculates_equal_weight_concentration(
        self,
    ) -> None:
        result = herfindahl_index(
            (0.5, 0.5),
        )

        assert result == 0.5

    def test_normalizes_weights(
        self,
    ) -> None:
        result = herfindahl_index(
            (50.0, 50.0),
        )

        assert result == 0.5

    def test_raises_for_negative_weights(
        self,
    ) -> None:
        with pytest.raises(
            ValueError,
            match="Weights must not contain negative values.",
        ):
            herfindahl_index(
                (0.5, -0.5),
            )


class TestEffectiveNumberOfPositions:
    def test_returns_zero_for_empty_weights(
        self,
    ) -> None:
        assert effective_number_of_positions(()) == 0.0

    def test_returns_zero_for_all_zero_weights(
        self,
    ) -> None:
        assert effective_number_of_positions(
            (0.0, 0.0),
        ) == 0.0

    def test_returns_effective_position_count(
        self,
    ) -> None:
        result = effective_number_of_positions(
            (0.5, 0.5),
        )

        assert result == 2.0

    def test_reflects_unequal_weights(
        self,
    ) -> None:
        result = effective_number_of_positions(
            (0.8, 0.2),
        )

        assert result == pytest.approx(
            1.4705882353,
        )


class TestLargestWeight:
    def test_returns_zero_for_empty_weights(
        self,
    ) -> None:
        assert largest_weight(()) == 0.0

    def test_returns_zero_for_all_zero_weights(
        self,
    ) -> None:
        assert largest_weight(
            (0.0, 0.0),
        ) == 0.0

    def test_returns_largest_normalized_weight(
        self,
    ) -> None:
        result = largest_weight(
            (20.0, 30.0, 50.0),
        )

        assert result == 0.5


class TestDiversificationScore:
    def test_returns_zero_for_empty_weights(
        self,
    ) -> None:
        assert diversification_score(()) == 0.0

    def test_returns_zero_for_all_zero_weights(
        self,
    ) -> None:
        assert diversification_score(
            (0.0, 0.0),
        ) == 0.0

    def test_returns_zero_for_single_position(
        self,
    ) -> None:
        assert diversification_score(
            (1.0,),
        ) == 0.0

    def test_returns_one_for_equal_weights(
        self,
    ) -> None:
        result = diversification_score(
            (0.5, 0.5),
        )

        assert result == 1.0

    def test_returns_lower_score_for_unequal_weights(
        self,
    ) -> None:
        result = diversification_score(
            (0.8, 0.2),
        )

        assert result == pytest.approx(
            0.64,
        )