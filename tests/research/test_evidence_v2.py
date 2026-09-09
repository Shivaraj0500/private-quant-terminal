from datetime import datetime, timedelta, timezone

import pytest

from private_quant_terminal.models.candle import Candle
from private_quant_terminal.research.evidence_v2 import ResearchV2EvidenceAdapter
from private_quant_terminal.research.execution_v2 import (
    ResearchV2ExecutionRequest,
    ResearchV2Executor,
)
from private_quant_terminal.research.execution import (
    ResearchExecutionEventType,
)
from private_quant_terminal.strategy.actions import EnterAction, ExitAction
from private_quant_terminal.strategy.compiler import StrategyCompiler
from private_quant_terminal.strategy.conditions import (
    ComparisonCondition,
    ComparisonOperator,
)
from private_quant_terminal.strategy.expressions import (
    ConstantExpression,
    PriceExpression,
    PriceField,
)
from private_quant_terminal.strategy.ir import StrategyIR
from private_quant_terminal.strategy.positions import (
    LegAction,
    LegInstrumentType,
    PositionGroup,
    StrategyLeg,
)
from private_quant_terminal.strategy.rules import StrategyRule


def _candles():
    start = datetime(2026, 1, 2, tzinfo=timezone.utc)
    return tuple(
        Candle(
            timestamp=start + timedelta(minutes=i),
            open=price,
            high=price,
            low=price,
            close=price,
            volume=1000,
        )
        for i, price in enumerate((100.0, 110.0))
    )


def _strategy(*, leg_action=LegAction.BUY):
    position = PositionGroup(
        group_id="group-1",
        name="Test Position",
        legs=(
            StrategyLeg(
                action=leg_action,
                instrument_type=LegInstrumentType.EQUITY,
                symbol="TEST",
            ),
        ),
    )

    return StrategyIR(
        strategy_id="v2-evidence",
        name="V2 Evidence",
        description="V2 evidence adapter test",
        version=1,
        status="VALIDATED",
        instruments=("TEST",),
        timeframe="1m",
        rules=(
            StrategyRule(
                rule_id="enter",
                name="Enter",
                condition=ComparisonCondition(
                    left=PriceExpression(field=PriceField.CLOSE),
                    operator=ComparisonOperator.GREATER_THAN_OR_EQUAL,
                    right=ConstantExpression(value=99.0),
                ),
                actions=(EnterAction(position=position),),
            ),
            StrategyRule(
                rule_id="exit",
                name="Exit",
                condition=ComparisonCondition(
                    left=PriceExpression(field=PriceField.CLOSE),
                    operator=ComparisonOperator.GREATER_THAN_OR_EQUAL,
                    right=ConstantExpression(value=105.0),
                ),
                actions=(ExitAction(group_id="group-1"),),
            ),
        ),
    )


def _execute(*, leg_action=LegAction.BUY):
    strategy = _strategy(leg_action=leg_action)
    plan = StrategyCompiler().compile(strategy)

    return ResearchV2Executor().execute(
        ResearchV2ExecutionRequest(
            plan=plan,
            candles=_candles(),
            initial_equity=1000.0,
            run_id="run-evidence",
        )
    )


def test_adapter_converts_v2_execution_to_legacy_evidence():
    execution = _execute()
    result = ResearchV2EvidenceAdapter().adapt(execution)

    assert result.run_id == "run-evidence"
    assert len(result.events) == 2
    assert len(result.trades) == 1
    assert len(result.equity_curve) == 2
    assert result.final_equity == 1010.0

    assert result.events[0].event_type is ResearchExecutionEventType.ENTRY
    assert result.events[1].event_type is ResearchExecutionEventType.EXIT

    trade = result.trades[0]
    assert trade.symbol == "TEST"
    assert trade.entry_price == 100.0
    assert trade.exit_price == 110.0
    assert trade.quantity == 1.0
    assert trade.gross_pnl == 10.0
    assert trade.transaction_cost == 0.0
    assert trade.net_pnl == 10.0


def test_adapter_converts_short_v2_execution_to_negative_trade_pnl():
    execution = _execute(leg_action=LegAction.SELL)
    result = ResearchV2EvidenceAdapter().adapt(execution)

    assert len(result.trades) == 1

    trade = result.trades[0]
    assert trade.entry_price == 100.0
    assert trade.exit_price == 110.0
    assert trade.gross_pnl == -10.0
    assert trade.net_pnl == -10.0


def test_adapter_preserves_equity_timestamps_and_values():
    execution = _execute()
    result = ResearchV2EvidenceAdapter().adapt(execution)

    assert tuple(point.equity for point in result.equity_curve) == (
        1000.0,
        1010.0,
    )

    assert tuple(point.timestamp for point in result.equity_curve) == (
        _candles()[0].timestamp,
        _candles()[1].timestamp,
    )


def test_adapter_rejects_wrong_execution_type():
    with pytest.raises(TypeError):
        ResearchV2EvidenceAdapter().adapt(object())


def test_adapter_rejects_missing_run_id():
    execution = _execute()

    from dataclasses import replace

    invalid = replace(execution, run_id=None)

    with pytest.raises(ValueError, match="run_id"):
        ResearchV2EvidenceAdapter().adapt(invalid)

def test_adapter_rejects_open_position_before_legacy_evidence_adaptation():
    execution = _execute()

    from dataclasses import replace

    open_position_execution = replace(
        execution,
        action_events=execution.action_events[:1],
        fills=execution.fills[:1],
    )

    with pytest.raises(
        ValueError,
        match="all positions to be closed",
    ):
        ResearchV2EvidenceAdapter().adapt(open_position_execution)
