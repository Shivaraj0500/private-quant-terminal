from datetime import UTC, datetime, timedelta

import pytest

from private_quant_terminal.models import Candle
from private_quant_terminal.research import (
    ResearchExecutionRequest,
    ResearchExecutor,
    ResearchParameters,
    ResearchRun,
    ResearchRunStatus,
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


def make_strategy_version(
    *,
    sizing_method: PositionSizingMethod = PositionSizingMethod.FIXED_QUANTITY,
    quantity: float = 1.0,
    slippage_bps: float = 0.0,
    transaction_cost_bps: float = 0.0,
) -> StrategyVersion:
    strategy = StrategyDefinition(
        strategy_id="executor-test",
        name="Executor Test",
        description="Research executor test strategy.",
        instruments=("RELIANCE",),
        timeframe=StrategyTimeframe.FIVE_MINUTES,
        entry_conditions=(
            StrategyCondition(
                indicator="close",
                operator=ConditionOperator.GREATER_THAN,
                value=100.0,
            ),
        ),
        exit_conditions=(
            StrategyCondition(
                indicator="close",
                operator=ConditionOperator.LESS_THAN,
                value=95.0,
            ),
        ),
        position_sizing=PositionSizing(
            method=sizing_method,
            value=quantity,
        ),
        stop_loss=StopLoss(type=StopLossType.NONE),
        take_profit=TakeProfit(type=TakeProfitType.NONE),
        execution=ExecutionAssumptions(
            order_type=OrderType.MARKET,
            slippage_bps=slippage_bps,
            transaction_cost_bps=transaction_cost_bps,
        ),
        status=StrategyStatus.VALIDATED,
    )

    return StrategyVersion(
        strategy_id=strategy.strategy_id,
        version=1,
        specification=strategy,
        created_at=datetime(2026, 1, 1, tzinfo=UTC),
    )


def make_run(
    strategy_version: StrategyVersion,
) -> ResearchRun:
    parameters = ResearchParameters(values={})

    return ResearchRun(
        run_id="executor-run",
        strategy_id=strategy_version.strategy_id,
        strategy_version=strategy_version.version,
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


def make_candle(timestamp: datetime, close: float) -> Candle:
    return Candle(
        timestamp=timestamp,
        open=close,
        high=close + 1.0,
        low=close - 1.0,
        close=close,
        volume=1000.0,
    )


def make_request(
    candles: tuple[Candle, ...],
    *,
    strategy_version: StrategyVersion | None = None,
) -> ResearchExecutionRequest:
    version = strategy_version or make_strategy_version()

    return ResearchExecutionRequest(
        run=make_run(version),
        strategy_version=version,
        candles=candles,
    )


def test_entry_and_exit_create_completed_trade() -> None:
    start = datetime(2026, 1, 1, tzinfo=UTC)

    request = make_request(
        (
            make_candle(start, 101.0),
            make_candle(start + timedelta(minutes=5), 94.0),
        )
    )

    result = ResearchExecutor(initial_equity=100000.0).execute(request)

    assert len(result.trades) == 1
    assert result.trades[0].entry_price == 101.0
    assert result.trades[0].exit_price == 94.0
    assert result.trades[0].quantity == 1.0
    assert result.trades[0].gross_pnl == -7.0
    assert result.trades[0].net_pnl == -7.0


def test_no_entry_produces_no_trade() -> None:
    start = datetime(2026, 1, 1, tzinfo=UTC)

    request = make_request(
        (
            make_candle(start, 99.0),
            make_candle(start + timedelta(minutes=5), 94.0),
        )
    )

    result = ResearchExecutor(initial_equity=100000.0).execute(request)

    assert result.trades == ()
    assert result.events == ()
    assert result.final_equity == 100000.0


def test_exit_without_position_is_ignored() -> None:
    start = datetime(2026, 1, 1, tzinfo=UTC)

    request = make_request(
        (
            make_candle(start, 99.0),
            make_candle(start + timedelta(minutes=5), 94.0),
        )
    )

    result = ResearchExecutor(initial_equity=100000.0).execute(request)

    assert result.trades == ()


def test_open_position_is_not_force_closed() -> None:
    start = datetime(2026, 1, 1, tzinfo=UTC)

    request = make_request(
        (
            make_candle(start, 101.0),
            make_candle(start + timedelta(minutes=5), 110.0),
        )
    )

    result = ResearchExecutor(initial_equity=100000.0).execute(request)

    assert result.trades == ()
    assert [event.event_type.value for event in result.events] == ["ENTRY"]
    assert result.final_equity == 100000.0


def test_fixed_quantity_is_used() -> None:
    strategy_version = make_strategy_version(quantity=10.0)
    start = datetime(2026, 1, 1, tzinfo=UTC)

    request = make_request(
        (
            make_candle(start, 101.0),
            make_candle(start + timedelta(minutes=5), 94.0),
        ),
        strategy_version=strategy_version,
    )

    result = ResearchExecutor(initial_equity=100000.0).execute(request)

    assert result.trades[0].quantity == 10.0
    assert result.trades[0].gross_pnl == -70.0


def test_slippage_is_applied_adversely() -> None:
    strategy_version = make_strategy_version(
        slippage_bps=100.0,
    )
    start = datetime(2026, 1, 1, tzinfo=UTC)

    request = make_request(
        (
            make_candle(start, 101.0),
            make_candle(start + timedelta(minutes=5), 94.0),
        ),
        strategy_version=strategy_version,
    )

    result = ResearchExecutor(initial_equity=100000.0).execute(request)

    trade = result.trades[0]

    assert trade.entry_price == pytest.approx(102.01)
    assert trade.exit_price == pytest.approx(93.06)


def test_transaction_cost_is_deducted() -> None:
    strategy_version = make_strategy_version(
        transaction_cost_bps=100.0,
    )
    start = datetime(2026, 1, 1, tzinfo=UTC)

    request = make_request(
        (
            make_candle(start, 101.0),
            make_candle(start + timedelta(minutes=5), 94.0),
        ),
        strategy_version=strategy_version,
    )

    result = ResearchExecutor(initial_equity=100000.0).execute(request)

    trade = result.trades[0]

    assert trade.gross_pnl == pytest.approx(-7.0)
    assert trade.transaction_cost == pytest.approx(1.95)
    assert trade.net_pnl == pytest.approx(-8.95)


def test_multiple_sequential_trades_are_supported() -> None:
    start = datetime(2026, 1, 1, tzinfo=UTC)

    request = make_request(
        (
            make_candle(start, 101.0),
            make_candle(start + timedelta(minutes=5), 94.0),
            make_candle(start + timedelta(minutes=10), 102.0),
            make_candle(start + timedelta(minutes=15), 93.0),
        )
    )

    result = ResearchExecutor(initial_equity=100000.0).execute(request)

    assert len(result.trades) == 2
    assert result.trades[0].gross_pnl == -7.0
    assert result.trades[1].gross_pnl == -9.0
    assert result.final_equity == 99984.0


@pytest.mark.parametrize(
    "method",
    [
        PositionSizingMethod.FIXED_NOTIONAL,
        PositionSizingMethod.PERCENT_OF_EQUITY,
        PositionSizingMethod.RISK_BASED,
    ],
)
def test_unsupported_sizing_methods_are_rejected(
    method: PositionSizingMethod,
) -> None:
    strategy_version = make_strategy_version(
        sizing_method=method,
    )
    start = datetime(2026, 1, 1, tzinfo=UTC)

    request = make_request(
        (make_candle(start, 101.0),),
        strategy_version=strategy_version,
    )

    with pytest.raises(
        ValueError,
        match="Unsupported research position sizing method",
    ):
        ResearchExecutor(initial_equity=100000.0).execute(request)


def test_strategy_and_run_identity_must_match() -> None:
    strategy_version = make_strategy_version()

    run = make_run(strategy_version)

    mismatched_strategy = StrategyVersion(
        strategy_id="different-strategy",
        version=1,
        specification=strategy_version.specification,
        created_at=strategy_version.created_at,
    )

    request = ResearchExecutionRequest(
        run=run,
        strategy_version=mismatched_strategy,
        candles=(),
    )

    with pytest.raises(
        ValueError,
        match="strategy identity does not match",
    ):
        ResearchExecutor(initial_equity=100000.0).execute(request)


def test_events_are_chronological() -> None:
    start = datetime(2026, 1, 1, tzinfo=UTC)

    request = make_request(
        (
            make_candle(start, 101.0),
            make_candle(start + timedelta(minutes=5), 94.0),
        )
    )

    result = ResearchExecutor(initial_equity=100000.0).execute(request)

    timestamps = [event.timestamp for event in result.events]

    assert timestamps == sorted(timestamps)


def test_executor_result_is_deterministic() -> None:
    start = datetime(2026, 1, 1, tzinfo=UTC)

    request = make_request(
        (
            make_candle(start, 101.0),
            make_candle(start + timedelta(minutes=5), 94.0),
        )
    )

    executor = ResearchExecutor(initial_equity=100000.0)

    first = executor.execute(request)
    second = executor.execute(request)

    assert first == second


def test_equity_curve_contains_one_snapshot_per_candle() -> None:
    start = datetime(2026, 1, 1, tzinfo=UTC)

    request = make_request(
        (
            make_candle(start, 99.0),
            make_candle(start + timedelta(minutes=5), 98.0),
            make_candle(start + timedelta(minutes=10), 97.0),
        )
    )

    result = ResearchExecutor(initial_equity=100000.0).execute(request)

    assert result.equity_curve == (
        100000.0,
        100000.0,
        100000.0,
    )


def test_equity_curve_marks_open_position_to_market() -> None:
    start = datetime(2026, 1, 1, tzinfo=UTC)

    request = make_request(
        (
            make_candle(start, 101.0),
            make_candle(start + timedelta(minutes=5), 105.0),
            make_candle(start + timedelta(minutes=10), 110.0),
        )
    )

    result = ResearchExecutor(initial_equity=100000.0).execute(request)

    assert result.trades == ()
    assert result.equity_curve == (
        100000.0,
        100004.0,
        100009.0,
    )
    assert result.final_equity == 100000.0


def test_equity_curve_records_realized_equity_after_exit() -> None:
    start = datetime(2026, 1, 1, tzinfo=UTC)

    request = make_request(
        (
            make_candle(start, 101.0),
            make_candle(start + timedelta(minutes=5), 94.0),
        )
    )

    result = ResearchExecutor(initial_equity=100000.0).execute(request)

    assert result.equity_curve == (
        100000.0,
        99993.0,
    )
    assert result.final_equity == 99993.0


def test_equity_curve_is_deterministic() -> None:
    start = datetime(2026, 1, 1, tzinfo=UTC)

    request = make_request(
        (
            make_candle(start, 101.0),
            make_candle(start + timedelta(minutes=5), 105.0),
            make_candle(start + timedelta(minutes=10), 94.0),
        )
    )

    executor = ResearchExecutor(initial_equity=100000.0)

    first = executor.execute(request)
    second = executor.execute(request)

    assert first.equity_curve == second.equity_curve
