from datetime import UTC, datetime

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
from private_quant_terminal.strategy.conditions import compare
from private_quant_terminal.strategy.expressions import constant
from private_quant_terminal.strategy.ir import StrategyIR
from private_quant_terminal.strategy.positions import (
    LegAction,
    LegInstrumentType,
    PositionGroup,
    StrategyLeg,
)
from private_quant_terminal.strategy.rules import StrategyRule
from private_quant_terminal.strategy.variables import (
    StrategyVariable,
    VariableScope,
    VariableType,
)


def make_strategy() -> StrategyDefinition:
    return StrategyDefinition(
        strategy_id="strategy-001",
        name="EMA Momentum",
        description="Example declarative momentum strategy.",
        instruments=("RELIANCE", "TCS"),
        timeframe=StrategyTimeframe.ONE_HOUR,
        entry_conditions=(
            StrategyCondition(
                indicator="EMA_20",
                operator=ConditionOperator.GREATER_THAN,
                value=0.0,
            ),
        ),
        exit_conditions=(
            StrategyCondition(
                indicator="RSI_14",
                operator=ConditionOperator.GREATER_THAN,
                value=70.0,
            ),
        ),
        position_sizing=PositionSizing(
            method=PositionSizingMethod.PERCENT_OF_EQUITY,
            value=10.0,
        ),
        stop_loss=StopLoss(
            type=StopLossType.PERCENT,
            value=2.0,
        ),
        take_profit=TakeProfit(
            type=TakeProfitType.RISK_REWARD,
            value=2.0,
        ),
        execution=ExecutionAssumptions(
            order_type=OrderType.MARKET,
            slippage_bps=5.0,
            transaction_cost_bps=10.0,
        ),
    )


def test_strategy_definition_is_immutable() -> None:
    strategy = make_strategy()

    assert strategy.status is StrategyStatus.DRAFT

    try:
        strategy.name = "Changed"
    except AttributeError:
        pass
    else:
        raise AssertionError("StrategyDefinition must be immutable.")


def test_strategy_definition_contains_canonical_fields() -> None:
    strategy = make_strategy()

    assert strategy.strategy_id == "strategy-001"
    assert strategy.instruments == ("RELIANCE", "TCS")
    assert strategy.timeframe is StrategyTimeframe.ONE_HOUR
    assert len(strategy.entry_conditions) == 1
    assert len(strategy.exit_conditions) == 1
    assert strategy.position_sizing.value == 10.0
    assert strategy.stop_loss.value == 2.0
    assert strategy.take_profit.value == 2.0


def test_strategy_version_is_immutable() -> None:
    strategy = make_strategy()

    version = StrategyVersion(
        strategy_id=strategy.strategy_id,
        version=1,
        specification=strategy,
        created_at=datetime.now(UTC),
    )

    assert version.version == 1
    assert version.specification is strategy

    try:
        version.version = 2
    except AttributeError:
        pass
    else:
        raise AssertionError("StrategyVersion must be immutable.")


def make_strategy_ir() -> StrategyIR:
    group = PositionGroup(
        group_id="entry",
        name="Entry Position",
        legs=(
            StrategyLeg(
                action=LegAction.BUY,
                instrument_type=LegInstrumentType.EQUITY,
                symbol="RELIANCE",
            ),
        ),
    )

    from private_quant_terminal.strategy.actions import EnterAction

    rule = StrategyRule(
        rule_id="entry-rule",
        name="Enter on close",
        condition=compare(constant(1), ">", constant(0)),
        actions=(EnterAction(position=group),),
    )

    return StrategyIR(
        strategy_id=" strategy-002 ",
        name=" Momentum Strategy ",
        description=" Test strategy ",
        version=1,
        status=StrategyStatus.DRAFT,
        instruments=(" reliance ", "TCS"),
        timeframe=StrategyTimeframe.ONE_HOUR,
        variables=(
            StrategyVariable(
                name="threshold",
                variable_type=VariableType.NUMBER,
                scope=VariableScope.STRATEGY,
                value=10,
            ),
        ),
        rules=(rule,),
        position_groups=(group,),
    )


def test_strategy_ir_contains_canonical_v2_fields() -> None:
    strategy = make_strategy_ir()

    assert strategy.strategy_id == "strategy-002"
    assert strategy.name == "Momentum Strategy"
    assert strategy.description == "Test strategy"
    assert strategy.version == 1
    assert strategy.status is StrategyStatus.DRAFT
    assert strategy.instruments == ("RELIANCE", "TCS")
    assert strategy.timeframe is StrategyTimeframe.ONE_HOUR
    assert len(strategy.variables) == 1
    assert len(strategy.rules) == 1
    assert len(strategy.position_groups) == 1
    assert strategy.session is None
    assert strategy.execution == ExecutionAssumptions()


def test_strategy_ir_is_immutable() -> None:
    strategy = make_strategy_ir()

    try:
        strategy.name = "Changed"
    except AttributeError:
        pass
    else:
        raise AssertionError("StrategyIR must be immutable.")


def test_strategy_ir_requires_positive_version() -> None:
    try:
        make_strategy_ir().__class__(
            strategy_id="strategy-003",
            name="Test",
            description="Test",
            version=0,
            status=StrategyStatus.DRAFT,
            instruments=("RELIANCE",),
            timeframe=StrategyTimeframe.ONE_HOUR,
        )
    except ValueError as exc:
        assert str(exc) == "Strategy version must be greater than zero."
    else:
        raise AssertionError("Expected ValueError")


def test_strategy_ir_rejects_duplicate_instruments() -> None:
    try:
        StrategyIR(
            strategy_id="strategy-003",
            name="Test",
            description="Test",
            version=1,
            status=StrategyStatus.DRAFT,
            instruments=("RELIANCE", " reliance "),
            timeframe=StrategyTimeframe.ONE_HOUR,
        )
    except ValueError as exc:
        assert str(exc) == "Strategy instruments must be unique."
    else:
        raise AssertionError("Expected ValueError")


def test_strategy_ir_rejects_duplicate_rule_ids() -> None:
    strategy = make_strategy_ir()
    rule = strategy.rules[0]

    try:
        StrategyIR(
            strategy_id="strategy-003",
            name="Test",
            description="Test",
            version=1,
            status=StrategyStatus.DRAFT,
            instruments=("RELIANCE",),
            timeframe=StrategyTimeframe.ONE_HOUR,
            rules=(rule, rule),
        )
    except ValueError as exc:
        assert str(exc) == "Strategy rule IDs must be unique."
    else:
        raise AssertionError("Expected ValueError")


def test_strategy_ir_rejects_duplicate_position_group_ids() -> None:
    strategy = make_strategy_ir()
    group = strategy.position_groups[0]

    try:
        StrategyIR(
            strategy_id="strategy-003",
            name="Test",
            description="Test",
            version=1,
            status=StrategyStatus.DRAFT,
            instruments=("RELIANCE",),
            timeframe=StrategyTimeframe.ONE_HOUR,
            position_groups=(group, group),
        )
    except ValueError as exc:
        assert str(exc) == "Strategy position group IDs must be unique."
    else:
        raise AssertionError("Expected ValueError")


def test_strategy_ir_rejects_duplicate_variable_names_case_insensitively() -> None:
    variable_one = StrategyVariable(
        name="threshold",
        variable_type=VariableType.NUMBER,
        scope=VariableScope.STRATEGY,
        value=10,
    )
    variable_two = StrategyVariable(
        name="THRESHOLD",
        variable_type=VariableType.NUMBER,
        scope=VariableScope.STRATEGY,
        value=20,
    )

    try:
        StrategyIR(
            strategy_id="strategy-003",
            name="Test",
            description="Test",
            version=1,
            status=StrategyStatus.DRAFT,
            instruments=("RELIANCE",),
            timeframe=StrategyTimeframe.ONE_HOUR,
            variables=(variable_one, variable_two),
        )
    except ValueError as exc:
        assert str(exc) == "Strategy variable names must be unique."
    else:
        raise AssertionError("Expected ValueError")
