from dataclasses import FrozenInstanceError

import pytest

from private_quant_terminal.services.technical_analysis import (
    TechnicalAnalysisResult,
    TechnicalAnalysisService,
)


class TestTechnicalAnalysisResult:
    def test_preserves_component_scores(self) -> None:
        result = TechnicalAnalysisResult(
            trend_score=1,
            momentum_score=1,
            volume_score=0,
            volatility_score=-1,
            overall_score=1,
            signal="BUY",
        )

        assert result.trend_score == 1
        assert result.momentum_score == 1
        assert result.volume_score == 0
        assert result.volatility_score == -1
        assert result.overall_score == 1
        assert result.signal == "BUY"

    def test_result_is_immutable(self) -> None:
        result = TechnicalAnalysisResult(
            trend_score=1,
            momentum_score=1,
            volume_score=0,
            volatility_score=-1,
            overall_score=1,
            signal="BUY",
        )

        with pytest.raises(FrozenInstanceError):
            result.signal = "SELL"

    def test_equal_results_are_equal(self) -> None:
        first = TechnicalAnalysisResult(
            trend_score=1,
            momentum_score=0,
            volume_score=1,
            volatility_score=-1,
            overall_score=1,
            signal="BUY",
        )

        second = TechnicalAnalysisResult(
            trend_score=1,
            momentum_score=0,
            volume_score=1,
            volatility_score=-1,
            overall_score=1,
            signal="BUY",
        )

        assert first == second

    def test_different_results_are_not_equal(self) -> None:
        first = TechnicalAnalysisResult(
            trend_score=1,
            momentum_score=0,
            volume_score=1,
            volatility_score=-1,
            overall_score=1,
            signal="BUY",
        )

        second = TechnicalAnalysisResult(
            trend_score=-1,
            momentum_score=0,
            volume_score=1,
            volatility_score=-1,
            overall_score=-1,
            signal="SELL",
        )

        assert first != second


class TestTechnicalAnalysisService:
    def test_generates_buy_signal_for_positive_score(self) -> None:
        service = TechnicalAnalysisService()

        result = service.generate_signal(
            trend_score=1,
            momentum_score=1,
            volume_score=0,
            volatility_score=-1,
        )

        assert result.trend_score == 1
        assert result.momentum_score == 1
        assert result.volume_score == 0
        assert result.volatility_score == -1
        assert result.overall_score == 1
        assert result.signal == "BUY"

    def test_generates_sell_signal_for_negative_score(self) -> None:
        service = TechnicalAnalysisService()

        result = service.generate_signal(
            trend_score=-1,
            momentum_score=-1,
            volume_score=0,
            volatility_score=0,
        )

        assert result.overall_score == -2
        assert result.signal == "SELL"

    def test_generates_neutral_signal_for_zero_score(self) -> None:
        service = TechnicalAnalysisService()

        result = service.generate_signal(
            trend_score=1,
            momentum_score=-1,
            volume_score=0,
            volatility_score=0,
        )

        assert result.overall_score == 0
        assert result.signal == "NEUTRAL"

    def test_adds_all_four_component_scores(self) -> None:
        service = TechnicalAnalysisService()

        result = service.generate_signal(
            trend_score=2,
            momentum_score=-1,
            volume_score=3,
            volatility_score=-2,
        )

        assert result.trend_score == 2
        assert result.momentum_score == -1
        assert result.volume_score == 3
        assert result.volatility_score == -2
        assert result.overall_score == 2
        assert result.signal == "BUY"