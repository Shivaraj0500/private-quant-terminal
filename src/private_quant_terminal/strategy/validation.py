from dataclasses import dataclass

from private_quant_terminal.strategy.conditions import (
    ComparisonCondition,
    CrossingCondition,
    LogicalCondition,
)
from private_quant_terminal.strategy.enums import (
    PositionSizingMethod,
    StopLossType,
    TakeProfitType,
)
from private_quant_terminal.strategy.expressions import (
    ArithmeticExpression,
    ConstantExpression,
    Expression,
    IndicatorExpression,
    PositionExpression,
    PriceExpression,
    TimeExpression,
    UnaryExpression,
    VariableExpression,
)
from private_quant_terminal.strategy.ir import StrategyDefinition, StrategyIR


@dataclass(frozen=True)
class ValidationIssue:
    """A deterministic validation issue."""

    field: str
    message: str


@dataclass(frozen=True)
class StrategyValidationResult:
    """Result of deterministic strategy validation."""

    valid: bool
    issues: tuple[ValidationIssue, ...] = ()


def validate_strategy(
    strategy: StrategyDefinition,
) -> StrategyValidationResult:
    """Validate a strategy definition deterministically."""

    issues: list[ValidationIssue] = []

    if not strategy.strategy_id.strip():
        issues.append(
            ValidationIssue(
                field="strategy_id",
                message="Strategy ID cannot be empty.",
            )
        )

    if not strategy.name.strip():
        issues.append(
            ValidationIssue(
                field="name",
                message="Strategy name cannot be empty.",
            )
        )

    if not strategy.description.strip():
        issues.append(
            ValidationIssue(
                field="description",
                message="Strategy description cannot be empty.",
            )
        )

    if not strategy.instruments:
        issues.append(
            ValidationIssue(
                field="instruments",
                message="Strategy must define at least one instrument.",
            )
        )

    normalized_instruments = {
        instrument.strip().upper()
        for instrument in strategy.instruments
    }

    if "" in normalized_instruments:
        issues.append(
            ValidationIssue(
                field="instruments",
                message="Instrument symbols cannot be empty.",
            )
        )

    if not strategy.entry_conditions:
        issues.append(
            ValidationIssue(
                field="entry_conditions",
                message="Strategy must define at least one entry condition.",
            )
        )

    if not strategy.exit_conditions:
        issues.append(
            ValidationIssue(
                field="exit_conditions",
                message="Strategy must define at least one exit condition.",
            )
        )

    if strategy.position_sizing.value <= 0:
        issues.append(
            ValidationIssue(
                field="position_sizing.value",
                message="Position sizing value must be greater than zero.",
            )
        )

    if (
        strategy.position_sizing.method
        is PositionSizingMethod.PERCENT_OF_EQUITY
        and strategy.position_sizing.value > 100
    ):
        issues.append(
            ValidationIssue(
                field="position_sizing.value",
                message="Percent-of-equity sizing cannot exceed 100.",
            )
        )

    if strategy.stop_loss.type is StopLossType.NONE:
        if strategy.stop_loss.value is not None:
            issues.append(
                ValidationIssue(
                    field="stop_loss.value",
                    message="Stop-loss value must be omitted when stop-loss type is NONE.",
                )
            )
    elif strategy.stop_loss.value is None:
        issues.append(
            ValidationIssue(
                field="stop_loss.value",
                message="Stop-loss value is required for the selected stop-loss type.",
            )
        )
    elif strategy.stop_loss.value <= 0:
        issues.append(
            ValidationIssue(
                field="stop_loss.value",
                message="Stop-loss value must be greater than zero.",
            )
        )

    if strategy.take_profit.type is TakeProfitType.NONE:
        if strategy.take_profit.value is not None:
            issues.append(
                ValidationIssue(
                    field="take_profit.value",
                    message="Take-profit value must be omitted when take-profit type is NONE.",
                )
            )
    elif strategy.take_profit.value is None:
        issues.append(
            ValidationIssue(
                field="take_profit.value",
                message="Take-profit value is required for the selected take-profit type.",
            )
        )
    elif strategy.take_profit.value <= 0:
        issues.append(
            ValidationIssue(
                field="take_profit.value",
                message="Take-profit value must be greater than zero.",
            )
        )

    if strategy.execution.slippage_bps < 0:
        issues.append(
            ValidationIssue(
                field="execution.slippage_bps",
                message="Slippage cannot be negative.",
            )
        )

    if strategy.execution.transaction_cost_bps < 0:
        issues.append(
            ValidationIssue(
                field="execution.transaction_cost_bps",
                message="Transaction cost cannot be negative.",
            )
        )

    return StrategyValidationResult(
        valid=not issues,
        issues=tuple(issues),
    )



def _validate_expression(
    expression: Expression,
    *,
    field: str,
    declared_variable_names: set[str],
    issues: list[ValidationIssue],
) -> None:
    """Recursively validate an expression tree and its variable references."""

    if isinstance(expression, ConstantExpression):
        return

    if isinstance(expression, PriceExpression):
        return

    if isinstance(expression, IndicatorExpression):
        return

    if isinstance(expression, TimeExpression):
        return

    if isinstance(expression, PositionExpression):
        return

    if isinstance(expression, VariableExpression):
        normalized_name = expression.name.strip().lower()

        if normalized_name not in declared_variable_names:
            issues.append(
                ValidationIssue(
                    field=field,
                    message=(
                        "Expression references undeclared strategy variable: "
                        f"{expression.name}."
                    ),
                )
            )
        return

    if isinstance(expression, ArithmeticExpression):
        _validate_expression(
            expression.left,
            field=f"{field}.left",
            declared_variable_names=declared_variable_names,
            issues=issues,
        )
        _validate_expression(
            expression.right,
            field=f"{field}.right",
            declared_variable_names=declared_variable_names,
            issues=issues,
        )
        return

    if isinstance(expression, UnaryExpression):
        _validate_expression(
            expression.operand,
            field=f"{field}.operand",
            declared_variable_names=declared_variable_names,
            issues=issues,
        )
        return

    issues.append(
        ValidationIssue(
            field=field,
            message=(
                "Unsupported expression type: "
                f"{type(expression).__name__}."
            ),
        )
    )


def _validate_condition(
    condition: object,
    *,
    field: str,
    declared_variable_names: set[str],
    issues: list[ValidationIssue],
) -> None:
    """Recursively validate a condition and all nested expressions."""

    if isinstance(condition, (ComparisonCondition, CrossingCondition)):
        _validate_expression(
            condition.left,
            field=f"{field}.left",
            declared_variable_names=declared_variable_names,
            issues=issues,
        )
        _validate_expression(
            condition.right,
            field=f"{field}.right",
            declared_variable_names=declared_variable_names,
            issues=issues,
        )
        return

    if isinstance(condition, LogicalCondition):
        for index, child in enumerate(condition.conditions):
            _validate_condition(
                child,
                field=f"{field}.conditions[{index}]",
                declared_variable_names=declared_variable_names,
                issues=issues,
            )
        return

    issues.append(
        ValidationIssue(
            field=field,
            message=(
                "Unsupported condition type: "
                f"{type(condition).__name__}."
            ),
        )
    )


def _validate_rule_actions(
    actions: tuple[object, ...],
    *,
    field: str,
    issues: list[ValidationIssue],
) -> None:
    """Validate statically provable action identity conflicts."""

    from private_quant_terminal.strategy.actions import (
        EnterAction,
        HedgeAction,
        RollAction,
    )

    entered_groups: set[str] = set()

    for index, action in enumerate(actions):
        action_field = f"{field}[{index}]"

        if isinstance(action, EnterAction):
            group_id = action.position.group_id

            if group_id in entered_groups:
                issues.append(
                    ValidationIssue(
                        field=action_field,
                        message=(
                            "Rule contains multiple ENTER actions for the "
                            f"same position group: {group_id}."
                        ),
                    )
                )

            entered_groups.add(group_id)
            continue

        if isinstance(action, RollAction):
            source_group_id = action.group_id
            replacement_group_id = action.replacement.group_id

            if source_group_id == replacement_group_id:
                issues.append(
                    ValidationIssue(
                        field=action_field,
                        message=(
                            "Roll action source and replacement must use "
                            f"different position groups: {source_group_id}."
                        ),
                    )
                )
            continue

        if isinstance(action, HedgeAction):
            parent_group_id = action.group_id
            hedge_group_id = action.hedge.group_id

            if parent_group_id == hedge_group_id:
                issues.append(
                    ValidationIssue(
                        field=action_field,
                        message=(
                            "Hedge action parent and hedge must use "
                            f"different position groups: {parent_group_id}."
                        ),
                    )
                )

def validate_strategy_ir(strategy: StrategyIR) -> StrategyValidationResult:
    """Validate canonical StrategyIR semantic cross-references."""

    from private_quant_terminal.strategy.actions import (
        EnterAction,
        ExitAction,
        HedgeAction,
        ModifyAction,
        RollAction,
    )

    issues: list[ValidationIssue] = []

    declared_group_ids = {
        group.group_id
        for group in strategy.position_groups
    }

    declared_variable_names = {
        variable.name.strip().lower()
        for variable in strategy.variables
    }

    for rule in strategy.rules:
        _validate_condition(
            rule.condition,
            field=f"rules.{rule.rule_id}.condition",
            declared_variable_names=declared_variable_names,
            issues=issues,
        )

        for assignment in rule.variable_assignments:
            assignment_name = assignment.name.strip().lower()

            if assignment_name not in declared_variable_names:
                issues.append(
                    ValidationIssue(
                        field=f"rules.{rule.rule_id}.variable_assignments",
                        message=(
                            "Variable assignment references undeclared "
                            f"strategy variable: {assignment.name}."
                        ),
                    )
                )

            _validate_expression(
                assignment.value,
                field=(
                    f"rules.{rule.rule_id}."
                    f"variable_assignments.{assignment.name}"
                ),
                declared_variable_names=declared_variable_names,
                issues=issues,
            )

        for mutation in rule.variable_mutations:
            mutation_name = mutation.name.strip().lower()

            if mutation_name not in declared_variable_names:
                issues.append(
                    ValidationIssue(
                        field=f"rules.{rule.rule_id}.variable_mutations",
                        message=(
                            "Variable mutation references undeclared "
                            f"strategy variable: {mutation.name}."
                        ),
                    )
                )

        _validate_rule_actions(
            rule.actions,
            field=f"rules.{rule.rule_id}.actions",
            issues=issues,
        )

        for action in rule.actions:
            field = f"rules.{rule.rule_id}.actions"

            if isinstance(action, EnterAction):
                group_id = action.position.group_id

                if group_id not in declared_group_ids:
                    issues.append(
                        ValidationIssue(
                            field=field,
                            message=(
                                "Enter action references undeclared "
                                f"position group: {group_id}."
                            ),
                        )
                    )

            elif isinstance(action, (ExitAction, ModifyAction)):
                group_id = action.group_id

                if group_id not in declared_group_ids:
                    issues.append(
                        ValidationIssue(
                            field=field,
                            message=(
                                "Action references undeclared position "
                                f"group: {group_id}."
                            ),
                        )
                    )

            elif isinstance(action, RollAction):
                source_group_id = action.group_id
                replacement_group_id = action.replacement.group_id

                if source_group_id not in declared_group_ids:
                    issues.append(
                        ValidationIssue(
                            field=field,
                            message=(
                                "Roll action references undeclared source "
                                f"position group: {source_group_id}."
                            ),
                        )
                    )

                if replacement_group_id not in declared_group_ids:
                    issues.append(
                        ValidationIssue(
                            field=field,
                            message=(
                                "Roll action replacement references "
                                "undeclared position group: "
                                f"{replacement_group_id}."
                            ),
                        )
                    )

            elif isinstance(action, HedgeAction):
                parent_group_id = action.group_id
                hedge_group_id = action.hedge.group_id

                if parent_group_id not in declared_group_ids:
                    issues.append(
                        ValidationIssue(
                            field=field,
                            message=(
                                "Hedge action references undeclared parent "
                                f"position group: {parent_group_id}."
                            ),
                        )
                    )

                if hedge_group_id not in declared_group_ids:
                    issues.append(
                        ValidationIssue(
                            field=field,
                            message=(
                                "Hedge action references undeclared "
                                f"position group: {hedge_group_id}."
                            ),
                        )
                    )

    return StrategyValidationResult(
        valid=not issues,
        issues=tuple(issues),
    )
