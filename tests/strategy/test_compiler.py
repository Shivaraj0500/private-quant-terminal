from private_quant_terminal.strategy import (
    ExecutionAssumptions,
    OrderType,
    StrategyIR,
    StrategyStatus,
    StrategyTimeframe,
)
from private_quant_terminal.strategy.actions import EnterAction
from private_quant_terminal.strategy.data_requirements import DataRequirement, DataField
from private_quant_terminal.strategy.variables import StrategyVariable, VariableScope, VariableType
from private_quant_terminal.strategy.canonical import strategy_hash
from private_quant_terminal.strategy.conditions import compare
from private_quant_terminal.strategy.expressions import constant, price
from private_quant_terminal.strategy.positions import (
    LegAction,
    LegInstrumentType,
    PositionGroup,
    StrategyLeg,
)
from private_quant_terminal.strategy.rules import StrategyRule
from private_quant_terminal.strategy.states import (
    StateTransition,
    StrategyState,
)
from private_quant_terminal.strategy.compiler import (
    CompiledStrategyPlan,
    StrategyCompiler,
)


def make_position_group(group_id: str = "entry") -> PositionGroup:
    return PositionGroup(
        group_id=group_id,
        name=group_id.title(),
        legs=(
            StrategyLeg(
                action=LegAction.BUY,
                instrument_type=LegInstrumentType.EQUITY,
                symbol="RELIANCE",
            ),
        ),
    )


def make_action(group_id: str = "entry") -> EnterAction:
    return EnterAction(position=make_position_group(group_id))


def make_rule(
    rule_id: str,
    *,
    priority: int,
    enabled: bool = True,
) -> StrategyRule:
    return StrategyRule(
        rule_id=rule_id,
        name=rule_id.title(),
        condition=compare(
            price("close"),
            ">",
            constant(100.0),
        ),
        actions=(make_action(rule_id),),
        priority=priority,
        enabled=enabled,
    )


def make_transition(
    transition_id: str,
    *,
    priority: int,
    enabled: bool = True,
) -> StateTransition:
    return StateTransition(
        transition_id=transition_id,
        from_state="ENTRY",
        to_state="ACTIVE",
        condition=compare(
            price("close"),
            ">",
            constant(100.0),
        ),
        actions=(make_action("transition-" + transition_id),),
        priority=priority,
        enabled=enabled,
    )


def make_strategy() -> StrategyIR:
    return StrategyIR(
        strategy_id="compiler-test-001",
        name="Compiler Test Strategy",
        description="Deterministic compiler contract test.",
        version=3,
        status=StrategyStatus.DRAFT,
        instruments=("RELIANCE",),
        timeframe=StrategyTimeframe.ONE_HOUR,
        variables=(
            StrategyVariable(
                name="roll_count",
                variable_type=VariableType.NUMBER,
                scope=VariableScope.STRATEGY,
                value=0,
            ),
        ),
        rules=(
            make_rule("same_priority_b", priority=10),
            make_rule("high_priority", priority=20),
            make_rule("disabled", priority=30, enabled=False),
            make_rule("same_priority_a", priority=10),
        ),
        states=(
            StrategyState("ENTRY", "Entry", initial=True),
            StrategyState("ACTIVE", "Active"),
        ),
        transitions=(
            make_transition("same_priority_b", priority=10),
            make_transition("high_priority", priority=20),
            make_transition("disabled", priority=30, enabled=False),
            make_transition("same_priority_a", priority=10),
        ),
        data_requirements=(
            DataRequirement(
                symbol="RELIANCE",
                timeframe="1h",
                fields=(DataField.CLOSE,),
                lookback=20,
            ),
        ),
        position_groups=(make_position_group(),),
        execution=ExecutionAssumptions(
            order_type=OrderType.MARKET,
            slippage_bps=2.0,
            transaction_cost_bps=1.0,
        ),
    )


def test_compiled_plan_preserves_strategy_identity_and_hash():
    strategy = make_strategy()

    plan = StrategyCompiler().compile(strategy)

    assert plan.strategy_id == strategy.strategy_id
    assert plan.version == strategy.version
    assert plan.strategy_hash == strategy_hash(strategy)


def test_compiled_plan_preserves_strategy_components():
    strategy = make_strategy()

    plan = StrategyCompiler().compile(strategy)

    assert plan.variables == strategy.variables
    assert plan.states == strategy.states
    assert plan.position_groups == strategy.position_groups
    assert plan.data_requirements == strategy.data_requirements
    assert plan.session == strategy.session
    assert plan.position_sizing == strategy.position_sizing
    assert plan.stop_loss == strategy.stop_loss
    assert plan.take_profit == strategy.take_profit
    assert plan.execution == strategy.execution


def test_compiler_orders_enabled_rules_deterministically():
    strategy = make_strategy()

    plan = StrategyCompiler().compile(strategy)

    assert tuple(rule.rule_id for rule in plan.rules) == (
        "high_priority",
        "same_priority_a",
        "same_priority_b",
    )


def test_compiler_excludes_disabled_rules():
    strategy = make_strategy()

    plan = StrategyCompiler().compile(strategy)

    assert "disabled" not in tuple(rule.rule_id for rule in plan.rules)


def test_compiler_orders_enabled_transitions_deterministically():
    strategy = make_strategy()

    plan = StrategyCompiler().compile(strategy)

    assert tuple(
        transition.transition_id
        for transition in plan.transitions["ENTRY"]
    ) == (
        "high_priority",
        "same_priority_a",
        "same_priority_b",
    )


def test_compiler_excludes_disabled_transitions():
    strategy = make_strategy()

    plan = StrategyCompiler().compile(strategy)

    assert "disabled" not in tuple(
        transition.transition_id
        for transition in plan.transitions["ENTRY"]
    )


def test_compiled_plan_is_immutable():
    strategy = make_strategy()

    plan = StrategyCompiler().compile(strategy)

    try:
        plan.strategy_id = "changed"
    except Exception:
        pass
    else:
        raise AssertionError("CompiledStrategyPlan must be immutable.")


def test_compiling_same_strategy_produces_equivalent_plans():
    strategy = make_strategy()

    first = StrategyCompiler().compile(strategy)
    second = StrategyCompiler().compile(strategy)

    assert first == second
