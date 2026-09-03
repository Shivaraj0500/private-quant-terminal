from dataclasses import replace

from private_quant_terminal.strategy.conditions import compare
from private_quant_terminal.strategy.expressions import constant

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
    ValidationIssue,
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


def test_ir_rejects_duplicate_enter_for_same_position_group() -> None:
    from private_quant_terminal.strategy.actions import EnterAction
    from private_quant_terminal.strategy.ir import StrategyIR
    from private_quant_terminal.strategy.rules import StrategyRule
    from private_quant_terminal.strategy.enums import StrategyStatus

    group = _make_test_position_group("entry", "Entry")

    strategy = StrategyIR(
        strategy_id="duplicate-enter",
        name="Duplicate Enter",
        description="Duplicate enter validation test.",
        version=1,
        status=StrategyStatus.DRAFT,
        instruments=("RELIANCE",),
        timeframe=StrategyTimeframe.ONE_HOUR,
        position_groups=(group,),
        rules=(
            StrategyRule(
                condition=compare(
                    constant(1),
                    ">",
                    constant(0),
                ),
                rule_id="duplicate-enter-rule",
                name="Duplicate enter rule",
                actions=(
                    EnterAction(position=group),
                    EnterAction(position=group),
                ),
            ),
        ),
    )

    result = _validate_ir(strategy)

    assert result.valid is False
    assert result.issues == (
        ValidationIssue(
            field="rules.duplicate-enter-rule.actions[1]",
            message=(
                "Rule contains multiple ENTER actions for the same "
                "position group: entry."
            ),
        ),
    )


def test_ir_rejects_roll_with_same_source_and_replacement_group() -> None:
    from private_quant_terminal.strategy.actions import RollAction
    from private_quant_terminal.strategy.enums import StrategyStatus
    from private_quant_terminal.strategy.ir import StrategyIR
    from private_quant_terminal.strategy.rules import StrategyRule

    group = _make_test_position_group("entry", "Entry")

    strategy = StrategyIR(
        strategy_id="invalid-roll",
        name="Invalid Roll",
        description="Invalid roll validation test.",
        version=1,
        status=StrategyStatus.DRAFT,
        instruments=("RELIANCE",),
        timeframe=StrategyTimeframe.ONE_HOUR,
        position_groups=(group,),
        rules=(
            StrategyRule(
                condition=compare(
                    constant(1),
                    ">",
                    constant(0),
                ),
                rule_id="invalid-roll-rule",
                name="Invalid roll rule",
                actions=(RollAction("entry", group),),
            ),
        ),
    )

    result = _validate_ir(strategy)

    assert result.valid is False
    assert result.issues == (
        ValidationIssue(
            field="rules.invalid-roll-rule.actions[0]",
            message=(
                "Roll action source and replacement must use different "
                "position groups: entry."
            ),
        ),
    )


def test_ir_rejects_hedge_with_same_parent_and_hedge_group() -> None:
    from private_quant_terminal.strategy.actions import HedgeAction
    from private_quant_terminal.strategy.enums import StrategyStatus
    from private_quant_terminal.strategy.ir import StrategyIR
    from private_quant_terminal.strategy.rules import StrategyRule

    group = _make_test_position_group("entry", "Entry")

    strategy = StrategyIR(
        strategy_id="invalid-hedge",
        name="Invalid Hedge",
        description="Invalid hedge validation test.",
        version=1,
        status=StrategyStatus.DRAFT,
        instruments=("RELIANCE",),
        timeframe=StrategyTimeframe.ONE_HOUR,
        position_groups=(group,),
        rules=(
            StrategyRule(
                condition=compare(
                    constant(1),
                    ">",
                    constant(0),
                ),
                rule_id="invalid-hedge-rule",
                name="Invalid hedge rule",
                actions=(HedgeAction("entry", group),),
            ),
        ),
    )

    result = _validate_ir(strategy)

    assert result.valid is False
    assert result.issues == (
        ValidationIssue(
            field="rules.invalid-hedge-rule.actions[0]",
            message=(
                "Hedge action parent and hedge must use different "
                "position groups: entry."
            ),
        ),
    )


def test_ir_accepts_enter_then_exit() -> None:
    from private_quant_terminal.strategy.actions import EnterAction, ExitAction
    from private_quant_terminal.strategy.enums import StrategyStatus
    from private_quant_terminal.strategy.ir import StrategyIR
    from private_quant_terminal.strategy.rules import StrategyRule

    group = _make_test_position_group("entry", "Entry")

    strategy = StrategyIR(
        strategy_id="enter-exit",
        name="Enter Exit",
        description="Enter exit validation test.",
        version=1,
        status=StrategyStatus.DRAFT,
        instruments=("RELIANCE",),
        timeframe=StrategyTimeframe.ONE_HOUR,
        position_groups=(group,),
        rules=(
            StrategyRule(
                condition=compare(
                    constant(1),
                    ">",
                    constant(0),
                ),
                rule_id="enter-exit-rule",
                name="Enter exit rule",
                actions=(
                    EnterAction(position=group),
                    ExitAction(group_id="entry"),
                ),
            ),
        ),
    )

    assert _validate_ir(strategy).valid is True


def test_ir_accepts_enter_then_modify() -> None:
    from private_quant_terminal.strategy.actions import EnterAction, ModifyAction
    from private_quant_terminal.strategy.enums import StrategyStatus
    from private_quant_terminal.strategy.ir import StrategyIR
    from private_quant_terminal.strategy.rules import StrategyRule

    group = _make_test_position_group("entry", "Entry")

    strategy = StrategyIR(
        strategy_id="enter-modify",
        name="Enter Modify",
        description="Enter modify validation test.",
        version=1,
        status=StrategyStatus.DRAFT,
        instruments=("RELIANCE",),
        timeframe=StrategyTimeframe.ONE_HOUR,
        position_groups=(group,),
        rules=(
            StrategyRule(
                condition=compare(
                    constant(1),
                    ">",
                    constant(0),
                ),
                rule_id="enter-modify-rule",
                name="Enter modify rule",
                actions=(
                    EnterAction(position=group),
                    ModifyAction("entry", (("quantity", 2),)),
                ),
            ),
        ),
    )

    assert _validate_ir(strategy).valid is True


def test_ir_accepts_enter_then_roll() -> None:
    from private_quant_terminal.strategy.actions import EnterAction, RollAction
    from private_quant_terminal.strategy.enums import StrategyStatus
    from private_quant_terminal.strategy.ir import StrategyIR
    from private_quant_terminal.strategy.rules import StrategyRule

    entry = _make_test_position_group("entry", "Entry")
    replacement = _make_test_position_group("replacement", "Replacement")

    strategy = StrategyIR(
        strategy_id="enter-roll",
        name="Enter Roll",
        description="Enter roll validation test.",
        version=1,
        status=StrategyStatus.DRAFT,
        instruments=("RELIANCE",),
        timeframe=StrategyTimeframe.ONE_HOUR,
        position_groups=(entry, replacement),
        rules=(
            StrategyRule(
                condition=compare(
                    constant(1),
                    ">",
                    constant(0),
                ),
                rule_id="enter-roll-rule",
                name="Enter roll rule",
                actions=(
                    EnterAction(position=entry),
                    RollAction("entry", replacement),
                ),
            ),
        ),
    )

    assert _validate_ir(strategy).valid is True


def test_ir_accepts_enter_then_hedge() -> None:
    from private_quant_terminal.strategy.actions import EnterAction, HedgeAction
    from private_quant_terminal.strategy.enums import StrategyStatus
    from private_quant_terminal.strategy.ir import StrategyIR
    from private_quant_terminal.strategy.rules import StrategyRule

    entry = _make_test_position_group("entry", "Entry")
    hedge = _make_test_position_group("hedge", "Hedge")

    strategy = StrategyIR(
        strategy_id="enter-hedge",
        name="Enter Hedge",
        description="Enter hedge validation test.",
        version=1,
        status=StrategyStatus.DRAFT,
        instruments=("RELIANCE",),
        timeframe=StrategyTimeframe.ONE_HOUR,
        position_groups=(entry, hedge),
        rules=(
            StrategyRule(
                condition=compare(
                    constant(1),
                    ">",
                    constant(0),
                ),
                rule_id="enter-hedge-rule",
                name="Enter hedge rule",
                actions=(
                    EnterAction(position=entry),
                    HedgeAction("entry", hedge),
                ),
            ),
        ),
    )

    assert _validate_ir(strategy).valid is True


def test_ir_accepts_modify_without_prior_enter() -> None:
    from private_quant_terminal.strategy.actions import ModifyAction
    from private_quant_terminal.strategy.enums import StrategyStatus
    from private_quant_terminal.strategy.ir import StrategyIR
    from private_quant_terminal.strategy.rules import StrategyRule

    group = _make_test_position_group("entry", "Entry")

    strategy = StrategyIR(
        strategy_id="modify-only",
        name="Modify Only",
        description="Modify-only validation test.",
        version=1,
        status=StrategyStatus.DRAFT,
        instruments=("RELIANCE",),
        timeframe=StrategyTimeframe.ONE_HOUR,
        position_groups=(group,),
        rules=(
            StrategyRule(
                condition=compare(
                    constant(1),
                    ">",
                    constant(0),
                ),
                rule_id="modify-only-rule",
                name="Modify-only rule",
                actions=(ModifyAction("entry", (("quantity", 2),)),),
            ),
        ),
    )

    assert _validate_ir(strategy).valid is True


def test_ir_accepts_exit_without_prior_enter() -> None:
    from private_quant_terminal.strategy.actions import ExitAction
    from private_quant_terminal.strategy.enums import StrategyStatus
    from private_quant_terminal.strategy.ir import StrategyIR
    from private_quant_terminal.strategy.rules import StrategyRule

    group = _make_test_position_group("entry", "Entry")

    strategy = StrategyIR(
        strategy_id="exit-only",
        name="Exit Only",
        description="Exit-only validation test.",
        version=1,
        status=StrategyStatus.DRAFT,
        instruments=("RELIANCE",),
        timeframe=StrategyTimeframe.ONE_HOUR,
        position_groups=(group,),
        rules=(
            StrategyRule(
                condition=compare(
                    constant(1),
                    ">",
                    constant(0),
                ),
                rule_id="exit-only-rule",
                name="Exit-only rule",
                actions=(ExitAction(group_id="entry"),),
            ),
        ),
    )

    assert _validate_ir(strategy).valid is True


def test_ir_reports_action_conflicts_in_deterministic_order() -> None:
    from private_quant_terminal.strategy.actions import HedgeAction, RollAction
    from private_quant_terminal.strategy.enums import StrategyStatus
    from private_quant_terminal.strategy.ir import StrategyIR
    from private_quant_terminal.strategy.rules import StrategyRule

    group = _make_test_position_group("entry", "Entry")

    strategy = StrategyIR(
        strategy_id="multiple-conflicts",
        name="Multiple Conflicts",
        description="Deterministic action diagnostic test.",
        version=1,
        status=StrategyStatus.DRAFT,
        instruments=("RELIANCE",),
        timeframe=StrategyTimeframe.ONE_HOUR,
        position_groups=(group,),
        rules=(
            StrategyRule(
                condition=compare(
                    constant(1),
                    ">",
                    constant(0),
                ),
                rule_id="multiple-conflicts-rule",
                name="Multiple conflicts rule",
                actions=(
                    RollAction("entry", group),
                    HedgeAction("entry", group),
                ),
            ),
        ),
    )

    result = _validate_ir(strategy)

    assert result.valid is False
    assert result.issues == (
        ValidationIssue(
            field="rules.multiple-conflicts-rule.actions[0]",
            message=(
                "Roll action source and replacement must use different "
                "position groups: entry."
            ),
        ),
        ValidationIssue(
            field="rules.multiple-conflicts-rule.actions[1]",
            message=(
                "Hedge action parent and hedge must use different "
                "position groups: entry."
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


def _make_ir_with_condition(
    condition,
    *,
    variables=(),
    variable_assignments=(),
    variable_mutations=(),
):
    from private_quant_terminal.strategy.actions import EnterAction
    from private_quant_terminal.strategy.enums import StrategyStatus
    from private_quant_terminal.strategy.rules import StrategyRule

    position_group = _make_test_position_group(
        "expression-test-group",
        "Expression test group",
    )

    return StrategyIR(
        strategy_id="strategy-ir-expression-validation",
        name="IR Expression Validation",
        description="Expression semantic validation test.",
        version=1,
        status=StrategyStatus.DRAFT,
        instruments=("RELIANCE",),
        timeframe=StrategyTimeframe.ONE_HOUR,
        variables=tuple(variables),
        position_groups=(position_group,),
        rules=(
            StrategyRule(
                rule_id="expression-rule",
                name="Expression rule",
                condition=condition,
                actions=(
                    EnterAction(position=position_group),
                ),
                variable_assignments=tuple(variable_assignments),
                variable_mutations=tuple(variable_mutations),
            ),
        ),
    )


def _number_variable(name: str):
    from private_quant_terminal.strategy.variables import (
        StrategyVariable,
        VariableScope,
        VariableType,
    )

    return StrategyVariable(
        name=name,
        variable_type=VariableType.NUMBER,
        scope=VariableScope.STRATEGY,
        value=0.0,
    )


def test_ir_accepts_declared_variable_in_condition() -> None:
    from private_quant_terminal.strategy.conditions import compare
    from private_quant_terminal.strategy.expressions import (
        price,
        variable,
        PriceField,
    )

    strategy = _make_ir_with_condition(
        compare(
            price(PriceField.CLOSE),
            ">",
            variable("threshold"),
        ),
        variables=(_number_variable("threshold"),),
    )

    result = _validate_ir(strategy)

    assert result.valid is True
    assert result.issues == ()


def test_ir_rejects_undeclared_variable_in_condition() -> None:
    from private_quant_terminal.strategy.conditions import compare
    from private_quant_terminal.strategy.expressions import (
        price,
        variable,
        PriceField,
    )

    strategy = _make_ir_with_condition(
        compare(
            price(PriceField.CLOSE),
            ">",
            variable("missing_threshold"),
        ),
    )

    result = _validate_ir(strategy)

    assert result.valid is False
    assert any(
        "missing_threshold" in issue.message
        for issue in result.issues
    )


def test_ir_rejects_undeclared_variable_nested_in_arithmetic() -> None:
    from private_quant_terminal.strategy.conditions import compare
    from private_quant_terminal.strategy.expressions import (
        arithmetic,
        constant,
        price,
        variable,
        PriceField,
    )

    strategy = _make_ir_with_condition(
        compare(
            price(PriceField.CLOSE),
            ">",
            arithmetic(
                variable("missing_threshold"),
                "+",
                constant(10),
            ),
        ),
    )

    result = _validate_ir(strategy)

    assert result.valid is False
    assert any(
        "missing_threshold" in issue.message
        for issue in result.issues
    )


def test_ir_rejects_undeclared_variable_in_crossover() -> None:
    from private_quant_terminal.strategy.conditions import cross_above
    from private_quant_terminal.strategy.expressions import (
        price,
        variable,
        PriceField,
    )

    strategy = _make_ir_with_condition(
        cross_above(
            price(PriceField.CLOSE),
            variable("missing_threshold"),
        ),
    )

    result = _validate_ir(strategy)

    assert result.valid is False
    assert any(
        "missing_threshold" in issue.message
        for issue in result.issues
    )


def test_ir_rejects_undeclared_variable_in_nested_logical_condition() -> None:
    from private_quant_terminal.strategy.conditions import all_of, compare
    from private_quant_terminal.strategy.expressions import (
        constant,
        price,
        variable,
        PriceField,
    )

    strategy = _make_ir_with_condition(
        all_of(
            compare(
                price(PriceField.CLOSE),
                ">",
                constant(100),
            ),
            all_of(
                compare(
                    variable("missing_threshold"),
                    ">",
                    constant(10),
                ),
            ),
        ),
    )

    result = _validate_ir(strategy)

    assert result.valid is False
    assert any(
        "missing_threshold" in issue.message
        for issue in result.issues
    )


def test_ir_variable_references_are_case_insensitive() -> None:
    from private_quant_terminal.strategy.conditions import compare
    from private_quant_terminal.strategy.expressions import (
        constant,
        variable,
    )

    strategy = _make_ir_with_condition(
        compare(
            variable("THRESHOLD"),
            ">",
            constant(0),
        ),
        variables=(_number_variable("threshold"),),
    )

    result = _validate_ir(strategy)

    assert result.valid is True
    assert result.issues == ()


def test_ir_rejects_undeclared_variable_assignment_target() -> None:
    from private_quant_terminal.strategy.conditions import compare
    from private_quant_terminal.strategy.expressions import constant
    from private_quant_terminal.strategy.variables import VariableAssignment

    strategy = _make_ir_with_condition(
        compare(
            constant(1),
            ">",
            constant(0),
        ),
        variable_assignments=(
            VariableAssignment(
                name="missing_variable",
                value=constant(10),
            ),
        ),
    )

    result = _validate_ir(strategy)

    assert result.valid is False
    assert any(
        "missing_variable" in issue.message
        for issue in result.issues
    )


def test_ir_rejects_undeclared_variable_inside_assignment_expression() -> None:
    from private_quant_terminal.strategy.conditions import compare
    from private_quant_terminal.strategy.expressions import (
        arithmetic,
        constant,
        variable,
    )
    from private_quant_terminal.strategy.variables import VariableAssignment

    strategy = _make_ir_with_condition(
        compare(
            constant(1),
            ">",
            constant(0),
        ),
        variables=(_number_variable("target"),),
        variable_assignments=(
            VariableAssignment(
                name="target",
                value=arithmetic(
                    variable("missing_variable"),
                    "+",
                    constant(1),
                ),
            ),
        ),
    )

    result = _validate_ir(strategy)

    assert result.valid is False
    assert any(
        "missing_variable" in issue.message
        for issue in result.issues
    )


def test_ir_rejects_undeclared_variable_mutation_target() -> None:
    from private_quant_terminal.strategy.conditions import compare
    from private_quant_terminal.strategy.expressions import constant
    from private_quant_terminal.strategy.variables import VariableMutation

    strategy = _make_ir_with_condition(
        compare(
            constant(1),
            ">",
            constant(0),
        ),
        variable_mutations=(
            VariableMutation(
                name="missing_variable",
                value=10,
            ),
        ),
    )

    result = _validate_ir(strategy)

    assert result.valid is False
    assert any(
        "missing_variable" in issue.message
        for issue in result.issues
    )


def test_ir_expression_validation_issue_order_is_deterministic() -> None:
    from private_quant_terminal.strategy.conditions import compare
    from private_quant_terminal.strategy.expressions import variable

    strategy = _make_ir_with_condition(
        compare(
            variable("missing_left"),
            ">",
            variable("missing_right"),
        ),
    )

    first = _validate_ir(strategy)
    second = _validate_ir(strategy)

    assert first.valid is False
    assert first.issues == second.issues
    assert len(first.issues) == 2
    assert "missing_left" in first.issues[0].message
    assert "missing_right" in first.issues[1].message


def test_ir_accepts_or_condition_with_declared_variables() -> None:
    from private_quant_terminal.strategy.conditions import any_of, compare
    from private_quant_terminal.strategy.expressions import (
        constant,
        variable,
    )

    strategy = _make_ir_with_condition(
        any_of(
            compare(variable("lower"), ">", constant(10)),
            compare(variable("upper"), "<", constant(100)),
        ),
        variables=(
            _number_variable("lower"),
            _number_variable("upper"),
        ),
    )

    result = _validate_ir(strategy)

    assert result.valid is True
    assert result.issues == ()


def test_ir_rejects_undeclared_variable_inside_not_condition() -> None:
    from private_quant_terminal.strategy.conditions import not_, compare
    from private_quant_terminal.strategy.expressions import (
        constant,
        variable,
    )

    strategy = _make_ir_with_condition(
        not_(
            compare(
                variable("missing_flag"),
                "==",
                constant(1),
            ),
        ),
    )

    result = _validate_ir(strategy)

    assert result.valid is False
    assert any(
        "missing_flag" in issue.message
        for issue in result.issues
    )


def test_ir_accepts_nested_unary_expression() -> None:
    from private_quant_terminal.strategy.conditions import compare
    from private_quant_terminal.strategy.expressions import (
        absolute,
        constant,
        negate,
    )

    strategy = _make_ir_with_condition(
        compare(
            absolute(negate(constant(10))),
            "==",
            constant(10),
        ),
    )

    result = _validate_ir(strategy)

    assert result.valid is True
    assert result.issues == ()


def test_ir_accepts_nested_arithmetic_expression() -> None:
    from private_quant_terminal.strategy.conditions import compare
    from private_quant_terminal.strategy.expressions import (
        arithmetic,
        constant,
    )

    strategy = _make_ir_with_condition(
        compare(
            arithmetic(
                arithmetic(
                    constant(10),
                    "+",
                    constant(5),
                ),
                "*",
                constant(2),
            ),
            "==",
            constant(30),
        ),
    )

    result = _validate_ir(strategy)

    assert result.valid is True
    assert result.issues == ()


def test_ir_accepts_position_expression() -> None:
    from private_quant_terminal.strategy.conditions import compare
    from private_quant_terminal.strategy.expressions import (
        constant,
        position,
        PositionField,
    )

    strategy = _make_ir_with_condition(
        compare(
            position(PositionField.UNREALIZED_PNL),
            ">",
            constant(0),
        ),
    )

    result = _validate_ir(strategy)

    assert result.valid is True
    assert result.issues == ()


def test_ir_accepts_time_expression() -> None:
    from private_quant_terminal.strategy.conditions import compare
    from private_quant_terminal.strategy.expressions import (
        constant,
        time_value,
        TimeField,
    )

    strategy = _make_ir_with_condition(
        compare(
            time_value(TimeField.DAY_OF_WEEK),
            ">=",
            constant(0),
        ),
    )

    result = _validate_ir(strategy)

    assert result.valid is True
    assert result.issues == ()


def test_ir_accepts_indicator_expression() -> None:
    from private_quant_terminal.strategy.conditions import compare
    from private_quant_terminal.strategy.expressions import (
        constant,
        indicator,
    )

    strategy = _make_ir_with_condition(
        compare(
            indicator(
                "EMA",
                parameters={"period": 20},
            ),
            ">",
            constant(100),
        ),
    )

    result = _validate_ir(strategy)

    assert result.valid is True
    assert result.issues == ()


def test_ir_accepts_nested_expression_with_declared_variable() -> None:
    from private_quant_terminal.strategy.conditions import compare
    from private_quant_terminal.strategy.expressions import (
        arithmetic,
        constant,
        negate,
        variable,
    )

    strategy = _make_ir_with_condition(
        compare(
            arithmetic(
                negate(variable("threshold")),
                "*",
                constant(-1),
            ),
            ">",
            constant(0),
        ),
        variables=(_number_variable("threshold"),),
    )

    result = _validate_ir(strategy)

    assert result.valid is True
    assert result.issues == ()
