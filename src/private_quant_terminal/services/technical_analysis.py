from dataclasses import dataclass


@dataclass(frozen=True)
class TechnicalAnalysisResult:
    trend_score: int
    momentum_score: int
    volume_score: int
    volatility_score: int
    overall_score: int
    signal: str


class TechnicalAnalysisService:
    def generate_signal(
        self,
        trend_score: int,
        momentum_score: int,
        volume_score: int,
        volatility_score: int,
    ) -> TechnicalAnalysisResult:
        overall_score = (
            trend_score
            + momentum_score
            + volume_score
            + volatility_score
        )

        if overall_score > 0:
            signal = "BUY"
        elif overall_score < 0:
            signal = "SELL"
        else:
            signal = "NEUTRAL"

        return TechnicalAnalysisResult(
            trend_score=trend_score,
            momentum_score=momentum_score,
            volume_score=volume_score,
            volatility_score=volatility_score,
            overall_score=overall_score,
            signal=signal,
        )