from datetime import datetime, timedelta, timezone

from private_quant_terminal.models.candle import Candle
from private_quant_terminal.research.execution_v2 import (
    ResearchV2ExecutionRequest,
    ResearchV2Executor,
)
from private_quant_terminal.strategy.actions import EnterAction, ExitAction
from private_quant_terminal.strategy.compiler import StrategyCompiler
from private_quant_terminal.strategy.conditions import ComparisonCondition, ComparisonOperator
from private_quant_terminal.strategy.expressions import ConstantExpression, PriceExpression, PriceField
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


def _strategy():
    position = PositionGroup(
        group_id="group-1",
        name="Test Position",
        legs=(
            StrategyLeg(
                action=LegAction.BUY,
                instrument_type=LegInstrumentType.EQUITY,
                symbol="TEST",
            ),
        ),
    )

    return StrategyIR(
        strategy_id="v2-e2e",
        name="V2 E2E",
        description="Canonical V2 execution test",
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


def test_v2_executor_runs_compiled_strategy_end_to_end():
    strategy = _strategy()
    plan = StrategyCompiler().compile(strategy)

    result = ResearchV2Executor(initial_equity=1000.0).execute(
        ResearchV2ExecutionRequest(
            plan=plan,
            candles=_candles(),
            initial_equity=1000.0,
            run_id="run-v2-e2e",
        )
    )

    assert result.run_id == "run-v2-e2e"
    assert result.strategy_id == "v2-e2e"
    assert result.strategy_version == 1
    assert len(result.action_events) == 2
    assert len(result.fills) == 2
    assert result.realized_pnl == 10.0
    assert result.transaction_cost == 0.0
    assert result.final_equity == 1010.0


def test_v2_executor_runs_multi_leg_position_group_end_to_end():
    start = datetime(2026, 1, 2, tzinfo=timezone.utc)

    candles = tuple(
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

    position = PositionGroup(
        group_id="multi-leg-group",
        name="Multi Leg Test",
        legs=(
            StrategyLeg(
                action=LegAction.BUY,
                instrument_type=LegInstrumentType.EQUITY,
                symbol="TEST",
                quantity=2,
            ),
            StrategyLeg(
                action=LegAction.SELL,
                instrument_type=LegInstrumentType.EQUITY,
                symbol="TEST2",
                quantity=3,
            ),
        ),
    )

    strategy = StrategyIR(
        strategy_id="v2-multi-leg-e2e",
        name="V2 Multi Leg E2E",
        description="Canonical V2 multi-leg execution test",
        version=1,
        status="VALIDATED",
        instruments=("TEST", "TEST2"),
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
                actions=(ExitAction(group_id="multi-leg-group"),),
            ),
        ),
    )

    plan = StrategyCompiler().compile(strategy)

    result = ResearchV2Executor(initial_equity=1000.0).execute(
        ResearchV2ExecutionRequest(
            plan=plan,
            candles=candles,
            initial_equity=1000.0,
            run_id="run-v2-multi-leg-e2e",
        )
    )

    assert result.run_id == "run-v2-multi-leg-e2e"
    assert len(result.action_events) == 4
    assert len(result.fills) == 4

    entry_fills = result.fills[:2]
    exit_fills = result.fills[2:]

    assert {fill.instrument.symbol for fill in entry_fills} == {
        "TEST",
        "TEST2",
    }
    assert {fill.quantity for fill in entry_fills} == {2.0, 3.0}

    assert {fill.instrument.symbol for fill in exit_fills} == {
        "TEST",
        "TEST2",
    }

    assert result.realized_pnl == -10.0
    assert result.transaction_cost == 0.0
    assert result.final_equity == 990.0

    assert result.simulation_steps[0].positions
    assert len(result.simulation_steps[0].positions) == 2
    assert result.simulation_steps[-1].positions == ()
