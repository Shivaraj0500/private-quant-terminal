from fastapi import Depends, Request

from private_quant_terminal.api.container import ApplicationContainer
from private_quant_terminal.services.market_data import MarketDataService
from private_quant_terminal.services.technical_analysis import (
    TechnicalAnalysisService,
)


def get_application_container(
    request: Request,
) -> ApplicationContainer:
    """Return the shared application container."""

    return request.app.state.container


def get_market_data_service(
    container: ApplicationContainer = Depends(
        get_application_container
    ),
) -> MarketDataService:
    """Return the configured market data service."""

    return container.market_data_service


def get_technical_analysis_service() -> TechnicalAnalysisService:
    """Return the technical analysis service."""

    return TechnicalAnalysisService()
