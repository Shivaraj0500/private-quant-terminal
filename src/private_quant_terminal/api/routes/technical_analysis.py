from fastapi import APIRouter, Depends

from private_quant_terminal.api.dependencies import (
    get_technical_analysis_service,
)
from private_quant_terminal.api.schemas.technical_analysis import (
    TechnicalAnalysisRequest,
    TechnicalAnalysisResponse,
)
from private_quant_terminal.services.technical_analysis import (
    TechnicalAnalysisService,
)

router = APIRouter(
    prefix="/technical-analysis",
    tags=["technical-analysis"],
)


@router.post(
    "/signal",
    response_model=TechnicalAnalysisResponse,
)
def generate_signal(
    request: TechnicalAnalysisRequest,
    service: TechnicalAnalysisService = Depends(
        get_technical_analysis_service
    ),
) -> TechnicalAnalysisResponse:
    """Generate a technical analysis signal from component scores."""
    result = service.generate_signal(
        trend_score=request.trend_score,
        momentum_score=request.momentum_score,
        volume_score=request.volume_score,
        volatility_score=request.volatility_score,
    )

    return TechnicalAnalysisResponse(
        trend_score=result.trend_score,
        momentum_score=result.momentum_score,
        volume_score=result.volume_score,
        volatility_score=result.volatility_score,
        overall_score=result.overall_score,
        signal=result.signal,
    )