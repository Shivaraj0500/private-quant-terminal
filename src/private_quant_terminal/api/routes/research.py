import json

from fastapi import APIRouter, HTTPException, Request

from private_quant_terminal.api.schemas.research import (
    ResearchEquityPointResponse,
    ResearchEventResponse,
    ResearchExecutionResponse,
    ResearchIntegrityResponse,
    ResearchIntelligenceResponse,
    ResearchBehaviorDiagnosticsResponse,
    ResearchBehaviorFindingResponse,
    ResearchPerformanceResponse,
    ResearchRunRequest,
    ResearchRunResponse,
    ResearchRunSummary,
    ResearchTradeAnalyticsResponse,
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

    candles = tuple(container.market_data_service.get_candles(payload.symbol))

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
            parameters=ResearchParameters(values=payload.parameters),
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
    "/runs",
    response_model=list[ResearchRunSummary],
)
def list_research_runs(
    request: Request,
) -> list[ResearchRunSummary]:
    """Return persisted research runs newest first."""

    container = request.app.state.container

    return [_run_summary(run) for run in container.research_repository.list()]


@router.get(
    "/runs/{run_id}",
    response_model=ResearchRunResponse,
)
def get_research_run(
    run_id: str,
    request: Request,
) -> ResearchRunResponse:
    """Return complete persisted evidence for one research run."""

    container = request.app.state.container

    try:
        run = container.research_repository.get(run_id)
        execution, integrity, performance, intelligence = container.research_repository.get_result(
            run_id
        )
    except KeyError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    return _persisted_result_response(
        run=run,
        execution=execution,
        integrity=integrity,
        performance=performance,
        intelligence=intelligence,
    )


def _persisted_result_response(
    *,
    run,
    execution,
    integrity,
    performance,
    intelligence,
) -> ResearchRunResponse:
    """Build the public response from persisted research evidence."""

    return ResearchRunResponse(
        run=_run_summary(run),
        execution=ResearchExecutionResponse(
            run_id=execution.run_id,
            events=[
                ResearchEventResponse(
                    timestamp=event.timestamp,
                    event_type=event.event_type.value,
                    symbol=event.symbol,
                    price=event.price,
                    quantity=event.quantity,
                )
                for event in execution.events
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
                for trade in execution.trades
            ],
            equity_curve=[
                ResearchEquityPointResponse(
                    timestamp=point.timestamp,
                    equity=point.equity,
                )
                for point in execution.equity_curve
            ],
            final_equity=execution.final_equity,
        ),
        performance=ResearchPerformanceResponse(
            realized_pnl=performance["trading_performance"]["realized_pnl"],
            unrealized_pnl=performance["trading_performance"]["unrealized_pnl"],
            total_pnl=performance["trading_performance"]["total_pnl"],
            winning_trades=performance["trading_performance"]["winning_trades"],
            losing_trades=performance["trading_performance"]["losing_trades"],
            win_rate=performance["trading_performance"]["win_rate"],
            average_win=performance["trading_performance"]["average_win"],
            average_loss=performance["trading_performance"]["average_loss"],
            profit_factor=performance["trading_performance"]["profit_factor"],
            returns=list(performance["returns"]),
            max_drawdown=performance["max_drawdown"],
            max_drawdown_percent=performance["max_drawdown_percent"],
            sharpe_ratio=performance["risk_adjusted"]["sharpe_ratio"],
            sortino_ratio=performance["risk_adjusted"]["sortino_ratio"],
            downside_deviation=performance["risk_adjusted"]["downside_deviation"],
            calmar_ratio=performance["risk_adjusted"]["calmar_ratio"],
            trade_analytics=ResearchTradeAnalyticsResponse(
                total_trades=performance["trade_analytics"]["total_trades"],
                average_trade=performance["trade_analytics"]["average_trade"],
                best_trade=performance["trade_analytics"]["best_trade"],
                worst_trade=performance["trade_analytics"]["worst_trade"],
                average_holding_time_seconds=(
                    performance["trade_analytics"]["average_holding_time"]
                ),
                shortest_holding_time_seconds=(
                    performance["trade_analytics"]["shortest_holding_time"]
                ),
                longest_holding_time_seconds=(
                    performance["trade_analytics"]["longest_holding_time"]
                ),
                max_consecutive_wins=performance["trade_analytics"]["max_consecutive_wins"],
                max_consecutive_losses=performance["trade_analytics"]["max_consecutive_losses"],
            ),
            behavior_diagnostics=ResearchBehaviorDiagnosticsResponse(
                entry_hour_distribution=list(
                    performance["behavior_diagnostics"]["entry_hour_distribution"]
                ),
                exit_hour_distribution=list(
                    performance["behavior_diagnostics"]["exit_hour_distribution"]
                ),
                winning_trade_count=performance["behavior_diagnostics"]["winning_trade_count"],
                losing_trade_count=performance["behavior_diagnostics"]["losing_trade_count"],
                zero_pnl_trade_count=performance["behavior_diagnostics"]["zero_pnl_trade_count"],
                winning_pnl=performance["behavior_diagnostics"]["winning_pnl"],
                losing_pnl=performance["behavior_diagnostics"]["losing_pnl"],
                average_winning_trade=performance["behavior_diagnostics"]["average_winning_trade"],
                average_losing_trade=performance["behavior_diagnostics"]["average_losing_trade"],
                loss_by_entry_hour=list(
                    performance["behavior_diagnostics"]["loss_by_entry_hour"]
                ),
            ),
            behavior_findings=[
                ResearchBehaviorFindingResponse(
                    category=finding["category"],
                    statement=finding["statement"],
                    evidence=finding["evidence"],
                )
                for finding in performance["behavior_findings"]
            ],
        ),
        intelligence=(
            ResearchIntelligenceResponse(
                conclusion=intelligence.conclusion.value,
                confidence=intelligence.confidence.value,
                strengths=list(intelligence.strengths),
                limitations=list(intelligence.limitations),
                next_investigations=list(intelligence.next_investigations),
                evidence=[
                    {
                        "category": reference.category,
                        "code": reference.code,
                        "description": reference.description,
                    }
                    for reference in intelligence.evidence
                ],
            )
            if intelligence is not None
            else None
        ),
        integrity=ResearchIntegrityResponse(
            status=integrity.status.value,
            passed=integrity.passed,
            warnings=integrity.warnings,
            failures=integrity.failures,
            findings=[
                {
                    "severity": finding.severity.value,
                    "code": finding.code,
                    "message": finding.message,
                }
                for finding in integrity.findings
            ],
        ),
    )


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
            equity_curve=[
                ResearchEquityPointResponse(
                    timestamp=point.timestamp,
                    equity=point.equity,
                )
                for point in result.execution.equity_curve
            ],
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
            trade_analytics=ResearchTradeAnalyticsResponse(
                total_trades=result.performance.trade_analytics.total_trades,
                average_trade=result.performance.trade_analytics.average_trade,
                best_trade=result.performance.trade_analytics.best_trade,
                worst_trade=result.performance.trade_analytics.worst_trade,
                average_holding_time_seconds=(
                    result.performance.trade_analytics.average_holding_time.total_seconds()
                ),
                shortest_holding_time_seconds=(
                    result.performance.trade_analytics.shortest_holding_time.total_seconds()
                ),
                longest_holding_time_seconds=(
                    result.performance.trade_analytics.longest_holding_time.total_seconds()
                ),
                max_consecutive_wins=(result.performance.trade_analytics.max_consecutive_wins),
                max_consecutive_losses=(result.performance.trade_analytics.max_consecutive_losses),
            ),
            behavior_diagnostics=ResearchBehaviorDiagnosticsResponse(
                entry_hour_distribution=list(
                    result.performance.behavior_diagnostics.entry_hour_distribution
                ),
                exit_hour_distribution=list(
                    result.performance.behavior_diagnostics.exit_hour_distribution
                ),
                winning_trade_count=(
                    result.performance.behavior_diagnostics.winning_trade_count
                ),
                losing_trade_count=(
                    result.performance.behavior_diagnostics.losing_trade_count
                ),
                zero_pnl_trade_count=(
                    result.performance.behavior_diagnostics.zero_pnl_trade_count
                ),
                winning_pnl=result.performance.behavior_diagnostics.winning_pnl,
                losing_pnl=result.performance.behavior_diagnostics.losing_pnl,
                average_winning_trade=(
                    result.performance.behavior_diagnostics.average_winning_trade
                ),
                average_losing_trade=(
                    result.performance.behavior_diagnostics.average_losing_trade
                ),
                loss_by_entry_hour=list(
                    result.performance.behavior_diagnostics.loss_by_entry_hour
                ),
            ),
            behavior_findings=[
                ResearchBehaviorFindingResponse(
                    category=finding.category,
                    statement=finding.statement,
                    evidence=finding.evidence,
                )
                for finding in result.performance.behavior_findings
            ],
        ),
        intelligence=(
            ResearchIntelligenceResponse(
                conclusion=result.intelligence.conclusion.value,
                confidence=result.intelligence.confidence.value,
                strengths=list(result.intelligence.strengths),
                limitations=list(result.intelligence.limitations),
                next_investigations=list(result.intelligence.next_investigations),
                evidence=[
                    {
                        "category": reference.category,
                        "code": reference.code,
                        "description": reference.description,
                    }
                    for reference in result.intelligence.evidence
                ],
            )
            if result.intelligence is not None
            else None
        ),
        integrity=ResearchIntegrityResponse(
            status=result.integrity.status.value,
            passed=result.integrity.passed,
            warnings=result.integrity.warnings,
            failures=result.integrity.failures,
            findings=[
                {
                    "severity": finding.severity.value,
                    "code": finding.code,
                    "message": finding.message,
                }
                for finding in result.integrity.findings
            ],
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
