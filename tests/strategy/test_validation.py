from dataclasses import replace

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
    StrategyIR,
    StrategyTimeframe,
    TakeProfit,
    TakeProfitType,
    validate_strategy,
    validate_strategy_ir,
)


def make_strategy() -> StrategyDefinition:
    return StrategyDefinition(
        strategy_id="strategy-001",
        name="EMA Momentum",
        description="Example strategy.",
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


def test_valid_strategy_passes() -> None:
    result = validate_strategy(make_strategy())

    assert result.valid is True
    assert result.issues == ()


def test_empty_universe_is_rejected() -> None:
    strategy = replace(
        make_strategy(),
        instruments=(),
    )

    result = validate_strategy(strategy)

    assert result.valid is False
    assert any(
        issue.field == "instruments"
        for issue in result.issues
    )


def test_missing_entry_conditions_are_rejected() -> None:
    strategy = replace(
        make_strategy(),
        entry_conditions=(),
    )

    result = validate_strategy(strategy)

    assert result.valid is False
    assert any(
        issue.field == "entry_conditions"
        for issue in result.issues
    )


def test_invalid_position_sizing_is_rejected() -> None:
    strategy = replace(
        make_strategy(),
        position_sizing=PositionSizing(
            method=PositionSizingMethod.PERCENT_OF_EQUITY,
            value=101.0,
        ),
    )

    result = validate_strategy(strategy)

    assert result.valid is False
    assert any(
        issue.field == "position_sizing.value"
        for issue in result.issues
    )


def test_negative_execution_cost_is_rejected() -> None:
    strategy = replace(
        make_strategy(),
        execution=ExecutionAssumptions(
            order_type=OrderType.MARKET,
            slippage_bps=-1.0,
            transaction_cost_bps=10.0,
        ),
    )

    result = validate_strategy(strategy)

    assert result.valid is False
    assert any(
        issue.field == "execution.slippage_bps"
        for issue in result.issues
    )


def test_missing_stop_loss_value_is_rejected() -> None:
    strategy = replace(
        make_strategy(),
        stop_loss=StopLoss(
            type=StopLossType.PERCENT,
            value=None,
        ),
    )

    result = validate_strategy(strategy)

    assert result.valid is False
    assert any(
        issue.field == "stop_loss.value"
        for issue in result.issues
    )

def _make_test_position_group(group_id: str, name: str):
    from private_quant_terminal.strategy.positions import (
        LegAction,
        LegInstrumentType,
        PositionGroup,
        StrategyLeg,
    )

    return PositionGroup(
        group_id=group_id,
        name=name,
        legs=(
            StrategyLeg(
                action=LegAction.BUY,
                instrument_type=LegInstrumentType.EQUITY,
                symbol="RELIANCE",
            ),
        ),
    )


def _make_ir_with_action(action, position_groups=()):
    from private_quant_terminal.strategy.conditions import compare
    from private_quant_terminal.strategy.enums import StrategyStatus
    from private_quant_terminal.strategy.expressions import constant
    from private_quant_terminal.strategy.ir import StrategyIR
    from private_quant_terminal.strategy.rules import StrategyRule

    return StrategyIR(
        strategy_id="strategy-ir-action-validation",
        name="IR Action Validation",
        description="Action cross-reference validation test.",
        version=1,
        status=StrategyStatus.DRAFT,
        instruments=("RELIANCE",),
        timeframe=StrategyTimeframe.ONE_HOUR,
        position_groups=tuple(position_groups),
        rules=(
            StrategyRule(
                rule_id="action-rule",
                name="Action rule",
                condition=compare(
                    constant(1),
                    ">",
                    constant(0),
                ),
                actions=(action,),
            ),
        ),
    )


def _validate_ir(strategy):
    from private_quant_terminal.strategy.validation import validate_strategy_ir

    return validate_strategy_ir(strategy)


def test_ir_rejects_enter_action_with_unknown_position_group() -> None:
    from private_quant_terminal.strategy.actions import EnterAction

    strategy = _make_ir_with_action(
        EnterAction(
            position=_make_test_position_group(
                "missing-group",
                "Missing group",
            ),
        ),
    )

    result = _validate_ir(strategy)

    assert result.valid is False
    assert any("missing-group" in issue.message for issue in result.issues)


def test_ir_rejects_modify_action_with_unknown_position_group() -> None:
    from private_quant_terminal.strategy.actions import ModifyAction

    strategy = _make_ir_with_action(
        ModifyAction(
            group_id="missing-group",
            changes=(("quantity", 1.0),),
        ),
    )

    result = _validate_ir(strategy)

    assert result.valid is False
    assert any("missing-group" in issue.message for issue in result.issues)


def test_ir_rejects_exit_action_with_unknown_position_group() -> None:
    from private_quant_terminal.strategy.actions import ExitAction

    strategy = _make_ir_with_action(
        ExitAction(group_id="missing-group"),
    )

    result = _validate_ir(strategy)

    assert result.valid is False
    assert any("missing-group" in issue.message for issue in result.issues)


def test_ir_rejects_roll_action_with_unknown_source_group() -> None:
    from private_quant_terminal.strategy.actions import RollAction

    replacement = _make_test_position_group(
        "declared-replacement",
        "Replacement group",
    )

    strategy = _make_ir_with_action(
        RollAction(
            group_id="missing-source",
            replacement=replacement,
        ),
        position_groups=(replacement,),
    )

    result = _validate_ir(strategy)

    assert result.valid is False
    assert any("missing-source" in issue.message for issue in result.issues)


def test_ir_rejects_roll_action_with_unknown_replacement_group() -> None:
    from private_quant_terminal.strategy.actions import RollAction

    source = _make_test_position_group(
        "declared-source",
        "Source group",
    )
    replacement = _make_test_position_group(
        "missing-replacement",
        "Missing replacement",
    )

    strategy = _make_ir_with_action(
        RollAction(
            group_id="declared-source",
            replacement=replacement,
        ),
        position_groups=(source,),
    )

    result = _validate_ir(strategy)

    assert result.valid is False
    assert any(
        "missing-replacement" in issue.message
        for issue in result.issues
    )


def test_ir_rejects_hedge_action_with_unknown_parent_group() -> None:
    from private_quant_terminal.strategy.actions import HedgeAction

    hedge = _make_test_position_group(
        "declared-hedge",
        "Hedge group",
    )

    strategy = _make_ir_with_action(
        HedgeAction(
            group_id="missing-parent",
            hedge=hedge,
        ),
        position_groups=(hedge,),
    )

    result = _validate_ir(strategy)

    assert result.valid is False
    assert any("missing-parent" in issue.message for issue in result.issues)


def test_ir_rejects_hedge_action_with_unknown_hedge_group() -> None:
    from private_quant_terminal.strategy.actions import HedgeAction

    parent = _make_test_position_group(
        "declared-parent",
        "Parent group",
    )
    hedge = _make_test_position_group(
        "missing-hedge",
        "Missing hedge",
    )

    strategy = _make_ir_with_action(
        HedgeAction(
            group_id="declared-parent",
            hedge=hedge,
        ),
        position_groups=(parent,),
    )

    result = _validate_ir(strategy)

    assert result.valid is False
    assert any("missing-hedge" in issue.message for issue in result.issues)


def test_ir_accepts_actions_referencing_declared_position_groups() -> None:
    from private_quant_terminal.strategy.actions import (
        EnterAction,
        ExitAction,
        HedgeAction,
        ModifyAction,
        RollAction,
    )

    source = _make_test_position_group(
        "source",
        "Source",
    )
    replacement = _make_test_position_group(
        "replacement",
        "Replacement",
    )
    hedge = _make_test_position_group(
        "hedge",
        "Hedge",
    )

    actions = (
        EnterAction(position=source),
        ExitAction(group_id="source"),
        ModifyAction(
            group_id="source",
            changes=(("quantity", 1.0),),
        ),
        RollAction(
            group_id="source",
            replacement=replacement,
        ),
        HedgeAction(
            group_id="source",
            hedge=hedge,
        ),
    )

    for action in actions:
        strategy = _make_ir_with_action(
            action,
            position_groups=(source, replacement, hedge),
        )

        result = _validate_ir(strategy)

        assert result.valid is True
        assert result.issues == ()
