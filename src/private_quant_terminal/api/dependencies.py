from private_quant_terminal.services.market_data import MarketDataService
from private_quant_terminal.services.technical_analysis import (
    TechnicalAnalysisService,
)


def get_market_data_service() -> MarketDataService:
    """Return the configured market data service."""
    raise NotImplementedError(
        "MarketDataService dependency has not been configured"
    )


def get_technical_analysis_service() -> TechnicalAnalysisService:
    """Return the technical analysis service."""
    return TechnicalAnalysisService()