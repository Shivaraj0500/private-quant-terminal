from pydantic import BaseModel


class TechnicalAnalysisRequest(BaseModel):
    """API request model for technical signal generation."""

    trend_score: int
    momentum_score: int
    volume_score: int
    volatility_score: int


class TechnicalAnalysisResponse(BaseModel):
    """API response model for technical signal generation."""

    trend_score: int
    momentum_score: int
    volume_score: int
    volatility_score: int
    overall_score: int
    signal: str