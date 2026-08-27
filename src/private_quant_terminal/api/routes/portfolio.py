from fastapi import APIRouter, HTTPException, Request

from private_quant_terminal.api.container import ApplicationContainer
from private_quant_terminal.api.schemas.portfolio import (
    PortfolioRiskRequest,
    PortfolioRiskResponse,
    PortfolioSnapshotRequest,
    PortfolioSnapshotResponse,
    PositionResponse,
)


router = APIRouter(
    prefix="/portfolio",
    tags=["portfolio"],
)


@router.get(
    "/positions",
    response_model=list[PositionResponse],
)
def get_positions(request: Request) -> list[PositionResponse]:
    """Return all currently open portfolio positions."""
    container: ApplicationContainer = request.app.state.container

    return [
        PositionResponse(
            symbol=position.symbol,
            quantity=position.quantity,
            average_price=position.average_price,
        )
        for position in container.portfolio_service.positions()
    ]


@router.post(
    "/snapshot",
    response_model=PortfolioSnapshotResponse,
)
def get_portfolio_snapshot(
    snapshot_request: PortfolioSnapshotRequest,
    request: Request,
) -> PortfolioSnapshotResponse:
    """Return the current portfolio valuation snapshot."""
    container: ApplicationContainer = request.app.state.container

    snapshot = container.portfolio_service.snapshot(
        prices=snapshot_request.prices,
    )

    return PortfolioSnapshotResponse(
        positions=[
            PositionResponse(
                symbol=position.symbol,
                quantity=position.quantity,
                average_price=position.average_price,
            )
            for position in snapshot.positions
        ],
        realized_pnl=snapshot.realized_pnl,
        unrealized_pnl=snapshot.unrealized_pnl,
        total_pnl=snapshot.total_pnl,
        open_position_count=snapshot.open_position_count,
    )


@router.post(
    "/risk",
    response_model=PortfolioRiskResponse,
)
def get_portfolio_risk(
    risk_request: PortfolioRiskRequest,
    request: Request,
) -> PortfolioRiskResponse:
    """Return portfolio exposure and concentration risk metrics."""
    container: ApplicationContainer = request.app.state.container

    try:
        risk = container.portfolio_service.risk(
            prices=risk_request.prices,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=500,
            detail=str(error),
        ) from error

    return PortfolioRiskResponse(
        gross_exposure=risk.gross_exposure,
        net_exposure=risk.net_exposure,
        long_exposure=risk.long_exposure,
        short_exposure=risk.short_exposure,
        largest_position_weight=risk.largest_position_weight,
        position_count=risk.position_count,
    )
