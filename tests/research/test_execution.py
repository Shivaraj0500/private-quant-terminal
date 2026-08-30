from datetime import UTC, datetime

from private_quant_terminal.models import Candle
from private_quant_terminal.research import (
    ResearchExecutionEvent,
    ResearchExecutionEventType,
    ResearchExecutionRequest,
    ResearchExecutionResult,
    ResearchParameters,
    ResearchRun,
    ResearchRunStatus,
    ResearchTrade,
    canonical_parameters_json,
    parameters_hash,
)
from private_quant_terminal.strategy import (
    ConditionOperator,
    ExecutionAssumptions,
    OrderType,
    PositionSizing,
    PositionSizingMethod,
    StopLoss,
    StopLossType,
    StrategyCondition,
    StrategyDefinition,
    StrategyStatus,
    StrategyTimeframe,
    StrategyVersion,
    TakeProfit,
    TakeProfitType,
)


def make_strategy_version() -> StrategyVersion:
    strategy = StrategyDefinition(
        strategy_id="research-test",
        name="Research Test",
        description="Research execution contract test.",
        instruments=("RELIANCE",),
        timeframe=StrategyTimeframe.FIVE_MINUTES,
        entry_conditions=(
            StrategyCondition(
                indicator="close",
                operator=ConditionOperator.GREATER_THAN,
                value=100,
            ),
        ),
        exit_conditions=(
            StrategyCondition(
                indicator="close",
                operator=ConditionOperator.LESS_THAN,
                value=90,
            ),
        ),
        position_sizing=PositionSizing(
            method=PositionSizingMethod.FIXED_QUANTITY,
            value=1,
        ),
        stop_loss=StopLoss(type=StopLossType.NONE),
        take_profit=TakeProfit(type=TakeProfitType.NONE),
        execution=ExecutionAssumptions(
            order_type=OrderType.MARKET,
        ),
        status=StrategyStatus.VALIDATED,
    )

    return StrategyVersion(
        strategy_id=strategy.strategy_id,
        version=1,
        specification=strategy,
        created_at=datetime(2026, 1, 1, tzinfo=UTC),
    )


def make_run() -> ResearchRun:
    parameters = ResearchParameters(values={"lookback": 20})

    return ResearchRun(
        run_id="run-1",
        strategy_id="research-test",
        strategy_version=1,
        strategy_hash="a" * 64,
        dataset_hash="b" * 64,
        symbol="RELIANCE",
        timeframe="5m",
        start_time=datetime(2026, 1, 1, tzinfo=UTC),
        end_time=datetime(2026, 1, 1, 1, tzinfo=UTC),
        parameters_json=canonical_parameters_json(parameters),
        parameters_hash=parameters_hash(parameters),
        status=ResearchRunStatus.CREATED,
        created_at=datetime(2026, 1, 1, tzinfo=UTC),
    )


def test_research_execution_request_is_immutable() -> None:
    request = ResearchExecutionRequest(
        run=make_run(),
        strategy_version=make_strategy_version(),
        candles=(
            Candle(
                timestamp=datetime(2026, 1, 1, tzinfo=UTC),
                open=100,
                high=110,
                low=90,
                close=105,
            ),
        ),
    )

    assert request.run.run_id == "run-1"
    assert len(request.candles) == 1


def test_research_execution_event_is_typed() -> None:
    event = ResearchExecutionEvent(
        timestamp=datetime(2026, 1, 1, tzinfo=UTC),
        event_type=ResearchExecutionEventType.ENTRY,
        symbol="RELIANCE",
        price=100.0,
        quantity=1.0,
    )

    assert event.event_type is ResearchExecutionEventType.ENTRY


def test_research_trade_contains_net_pnl() -> None:
    trade = ResearchTrade(
        symbol="RELIANCE",
        entry_time=datetime(2026, 1, 1, tzinfo=UTC),
        exit_time=datetime(2026, 1, 1, 1, tzinfo=UTC),
        entry_price=100.0,
        exit_price=110.0,
        quantity=10.0,
        gross_pnl=100.0,
        transaction_cost=2.0,
        net_pnl=98.0,
    )

    assert trade.net_pnl == 98.0


def test_research_execution_result_is_immutable() -> None:
    result = ResearchExecutionResult(
        run_id="run-1",
        events=(),
        trades=(),
        equity_curve=(),
        final_equity=100000.0,
    )

    assert result.run_id == "run-1"
    assert result.final_equity == 100000.0
