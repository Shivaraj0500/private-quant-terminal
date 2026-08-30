import json

from fastapi import APIRouter, HTTPException, Request

from private_quant_terminal.api.schemas.research import (
    ResearchEventResponse,
    ResearchExecutionResponse,
    ResearchPerformanceResponse,
    ResearchRunRequest,
    ResearchRunResponse,
    ResearchRunSummary,
    ResearchTradeResponse,
)
from private_quant_terminal.data.identity import create_dataset_identity
from private_quant_terminal.research import ResearchParameters

router = APIRouter(
    prefix="/research",
    tags=["research"],
)


@router.post(
    "/runs",
    response_model=ResearchRunResponse,
)
def execute_research_run(
    payload: ResearchRunRequest,
    request: Request,
) -> ResearchRunResponse:
    """Create and execute one deterministic research run."""

    container = request.app.state.container

    try:
        strategy_version = container.strategy_repository.get(
            strategy_id=payload.strategy_id,
            version=payload.strategy_version,
        )
    except KeyError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    candles = tuple(
        container.market_data_service.get_candles(
            payload.symbol
        )
    )

    if not candles:
        raise HTTPException(
            status_code=404,
            detail=f"No candles available for {payload.symbol}.",
        )

    try:
        dataset = create_dataset_identity(
            symbol=payload.symbol,
            timeframe=payload.timeframe,
            candles=list(candles),
        )

        result = container.research_service.create_run(
            strategy_version=strategy_version,
            dataset=dataset,
            parameters=ResearchParameters(
                values=payload.parameters
            ),
        )

        analysis = container.research_service.execute_run(
            run=result.run,
            strategy_version=strategy_version,
            candles=candles,
            initial_equity=payload.initial_equity,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    return _to_response(analysis)


@router.get(
    "/runs/{run_id}",
    response_model=ResearchRunSummary,
)
def get_research_run(
    run_id: str,
    request: Request,
) -> ResearchRunSummary:
    """Return the persisted metadata for one research run."""

    container = request.app.state.container

    try:
        run = container.research_repository.get(run_id)
    except KeyError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    return _run_summary(run)


def _to_response(result) -> ResearchRunResponse:
    trading = result.performance.trading_performance
    risk = result.performance.risk_adjusted

    return ResearchRunResponse(
        run=_run_summary(result.run),
        execution=ResearchExecutionResponse(
            run_id=result.execution.run_id,
            events=[
                ResearchEventResponse(
                    timestamp=event.timestamp,
                    event_type=event.event_type.value,
                    symbol=event.symbol,
                    price=event.price,
                    quantity=event.quantity,
                )
                for event in result.execution.events
            ],
            trades=[
                ResearchTradeResponse(
                    symbol=trade.symbol,
                    entry_time=trade.entry_time,
                    exit_time=trade.exit_time,
                    entry_price=trade.entry_price,
                    exit_price=trade.exit_price,
                    quantity=trade.quantity,
                    gross_pnl=trade.gross_pnl,
                    transaction_cost=trade.transaction_cost,
                    net_pnl=trade.net_pnl,
                )
                for trade in result.execution.trades
            ],
            equity_curve=list(result.execution.equity_curve),
            final_equity=result.execution.final_equity,
        ),
        performance=ResearchPerformanceResponse(
            realized_pnl=trading.realized_pnl,
            unrealized_pnl=trading.unrealized_pnl,
            total_pnl=trading.total_pnl,
            winning_trades=trading.winning_trades,
            losing_trades=trading.losing_trades,
            win_rate=trading.win_rate,
            average_win=trading.average_win,
            average_loss=trading.average_loss,
            profit_factor=trading.profit_factor,
            returns=list(result.performance.returns),
            max_drawdown=result.performance.max_drawdown,
            max_drawdown_percent=result.performance.max_drawdown_percent,
            sharpe_ratio=risk.sharpe_ratio,
            sortino_ratio=risk.sortino_ratio,
            downside_deviation=risk.downside_deviation,
            calmar_ratio=risk.calmar_ratio,
        ),
    )


def _run_summary(run) -> ResearchRunSummary:
    return ResearchRunSummary(
        run_id=run.run_id,
        strategy_id=run.strategy_id,
        strategy_version=run.strategy_version,
        strategy_hash=run.strategy_hash,
        dataset_hash=run.dataset_hash,
        symbol=run.symbol,
        timeframe=run.timeframe,
        start_time=run.start_time,
        end_time=run.end_time,
        parameters=json.loads(run.parameters_json),
        parameters_hash=run.parameters_hash,
        status=run.status.value,
        created_at=run.created_at,
    )
