from fastapi import APIRouter, HTTPException, Request

from private_quant_terminal.api.container import ApplicationContainer
from private_quant_terminal.api.schemas.portfolio import (
    ClosedTradeResponse,
    PortfolioDrawdownRequest,
    PortfolioDrawdownResponse,
    PortfolioPerformanceRequest,
    PortfolioRollingDrawdownRequest,
    PortfolioRollingDrawdownResponse,
    PortfolioRollingPerformanceRequest,
    PortfolioRollingPerformanceResponse,
    PortfolioPerformanceResponse,
    PortfolioRiskAdjustedRequest,
    PortfolioRiskAdjustedResponse,
    PortfolioRiskRequest,
    PortfolioRiskResponse,
    PortfolioSnapshotRequest,
    PortfolioSnapshotResponse,
    PositionResponse,
    TradingPerformanceResponse,
)


router = APIRouter(
    prefix="/portfolio",
    tags=["portfolio"],
)


@router.get(
    "/positions",
    response_model=list[PositionResponse],
)
def get_positions(
    request: Request,
) -> list[PositionResponse]:
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


@router.get(
    "/closed-trades",
    response_model=list[ClosedTradeResponse],
)
def get_closed_trades(
    request: Request,
) -> list[ClosedTradeResponse]:
    """Return all completed portfolio trades."""
    container: ApplicationContainer = request.app.state.container

    return [
        ClosedTradeResponse(
            symbol=trade.symbol,
            quantity=trade.quantity,
            entry_price=trade.entry_price,
            exit_price=trade.exit_price,
            realized_pnl=trade.realized_pnl,
        )
        for trade in container.portfolio_service.closed_trades()
    ]


@router.get(
    "/trading-performance",
    response_model=TradingPerformanceResponse,
)
def get_trading_performance(
    request: Request,
) -> TradingPerformanceResponse:
    """Return performance statistics calculated from closed trades."""
    container: ApplicationContainer = request.app.state.container

    performance = container.portfolio_service.trading_performance()

    return TradingPerformanceResponse(
        realized_pnl=performance.realized_pnl,
        unrealized_pnl=performance.unrealized_pnl,
        total_pnl=performance.total_pnl,
        winning_trades=performance.winning_trades,
        losing_trades=performance.losing_trades,
        win_rate=performance.win_rate,
        average_win=performance.average_win,
        average_loss=performance.average_loss,
        profit_factor=performance.profit_factor,
    )


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


@router.post(
    "/performance",
    response_model=PortfolioPerformanceResponse,
)
def get_portfolio_performance(
    performance_request: PortfolioPerformanceRequest,
    request: Request,
) -> PortfolioPerformanceResponse:
    """Return summary performance metrics for a return series."""
    container: ApplicationContainer = request.app.state.container

    performance = container.portfolio_service.performance(
        returns=tuple(performance_request.returns),
    )

    return PortfolioPerformanceResponse(
        total_return=performance.total_return,
        average_return=performance.average_return,
        best_return=performance.best_return,
        worst_return=performance.worst_return,
        volatility=performance.volatility,
    )


@router.post(
    "/drawdown",
    response_model=PortfolioDrawdownResponse,
)
def get_portfolio_drawdown(
    drawdown_request: PortfolioDrawdownRequest,
    request: Request,
) -> PortfolioDrawdownResponse:
    """Return current portfolio drawdown metrics."""
    container: ApplicationContainer = request.app.state.container

    try:
        drawdown = container.portfolio_service.drawdown(
            peak_value=drawdown_request.peak_value,
            current_value=drawdown_request.current_value,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=422,
            detail=str(error),
        ) from error

    return PortfolioDrawdownResponse(
        peak_value=drawdown.peak_value,
        current_value=drawdown.current_value,
        drawdown=drawdown.drawdown,
        drawdown_percent=drawdown.drawdown_percent,
    )

@router.post(
    "/risk-adjusted",
    response_model=PortfolioRiskAdjustedResponse,
)
def get_portfolio_risk_adjusted(
    risk_adjusted_request: PortfolioRiskAdjustedRequest,
    request: Request,
) -> PortfolioRiskAdjustedResponse:
    """Return risk-adjusted metrics for a portfolio return series."""
    container: ApplicationContainer = request.app.state.container

    metrics = container.portfolio_service.risk_adjusted(
        returns=tuple(risk_adjusted_request.returns),
        risk_free_rate=risk_adjusted_request.risk_free_rate,
        target_return=risk_adjusted_request.target_return,
        max_drawdown=risk_adjusted_request.max_drawdown,
    )

    return PortfolioRiskAdjustedResponse(
        sharpe_ratio=metrics.sharpe_ratio,
        sortino_ratio=metrics.sortino_ratio,
        downside_deviation=metrics.downside_deviation,
        calmar_ratio=metrics.calmar_ratio,
    )



@router.post(
    "/rolling-performance",
    response_model=PortfolioRollingPerformanceResponse,
)
def get_portfolio_rolling_performance(
    rolling_request: PortfolioRollingPerformanceRequest,
    request: Request,
) -> PortfolioRollingPerformanceResponse:
    """Return rolling portfolio performance analytics."""
    container: ApplicationContainer = request.app.state.container

    try:
        metrics = container.portfolio_service.rolling_performance(
            returns=tuple(rolling_request.returns),
            window=rolling_request.window,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=422,
            detail=str(error),
        ) from error

    return PortfolioRollingPerformanceResponse(
        rolling_returns=list(metrics.rolling_returns),
        rolling_average=list(metrics.rolling_average),
        rolling_volatility=list(metrics.rolling_volatility),
        rolling_drawdown=list(metrics.rolling_drawdown),
        rolling_max_drawdown=list(metrics.rolling_max_drawdown),
    )


@router.post(
    "/rolling-drawdown",
    response_model=PortfolioRollingDrawdownResponse,
)
def get_portfolio_rolling_drawdown(
    rolling_request: PortfolioRollingDrawdownRequest,
    request: Request,
) -> PortfolioRollingDrawdownResponse:
    """Return rolling portfolio drawdown analytics."""
    container: ApplicationContainer = request.app.state.container

    try:
        drawdown, max_drawdown = (
            container.portfolio_service.rolling_drawdown(
                values=tuple(rolling_request.values),
                window=rolling_request.window,
            )
        )
    except ValueError as error:
        raise HTTPException(
            status_code=422,
            detail=str(error),
        ) from error

    return PortfolioRollingDrawdownResponse(
        rolling_drawdown=list(drawdown),
        rolling_max_drawdown=list(max_drawdown),
    )
