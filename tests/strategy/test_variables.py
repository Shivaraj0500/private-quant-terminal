from datetime import UTC, datetime

import pytest

from private_quant_terminal.strategy.variables import (
    MarketContext,
    PositionContext,
    SessionContext,
    StrategyRuntimeContext,
    StrategyVariable,
    StrategyVariableStore,
    VariableMutation,
    VariableScope,
    VariableType,
)


def market() -> MarketContext:
    return MarketContext(
        timestamp=datetime(2026, 8, 30, 10, 0, tzinfo=UTC),
        open=100.0,
        high=105.0,
        low=99.0,
        close=104.0,
        volume=10000.0,
        underlying_price=45000.0,
        option_price=250.0,
    )


def test_strategy_variable() -> None:
    variable = StrategyVariable(
        name="risk_per_trade",
        variable_type=VariableType.NUMBER,
        scope=VariableScope.STRATEGY,
        value=1.0,
    )

    assert variable.name == "risk_per_trade"
    assert variable.value == 1.0


def test_variable_rejects_invalid_name() -> None:
    with pytest.raises(
        ValueError,
        match="must not be empty",
    ):
        StrategyVariable(
            name=" ",
            variable_type=VariableType.NUMBER,
            scope=VariableScope.STRATEGY,
        )


def test_market_context() -> None:
    context = market()

    assert context.close == 104.0
    assert context.underlying_price == 45000.0


def test_market_context_rejects_invalid_range() -> None:
    with pytest.raises(
        ValueError,
        match="high cannot be below low",
    ):
        MarketContext(
            timestamp=datetime(2026, 8, 30, 10, 0, tzinfo=UTC),
            open=100.0,
            high=90.0,
            low=95.0,
            close=100.0,
        )


def test_position_pnl_percentage() -> None:
    position = PositionContext(
        quantity=10,
        entry_price=100,
        current_price=110,
        average_price=100,
        unrealized_pnl=100,
    )

    assert position.unrealized_pnl_percent == 10.0


def test_position_pnl_percentage_without_position() -> None:
    position = PositionContext()

    assert position.unrealized_pnl_percent == 0.0


def test_runtime_context_resolves_market_values() -> None:
    context = StrategyRuntimeContext(
        market=market(),
    )

    assert context.resolve("close") == 104.0
    assert context.resolve("high") == 105.0
    assert context.resolve("underlying_price") == 45000.0


def test_runtime_context_resolves_position_values() -> None:
    context = StrategyRuntimeContext(
        market=market(),
        position=PositionContext(
            quantity=25,
            entry_price=200.0,
            current_price=250.0,
            unrealized_pnl=1250.0,
        ),
    )

    assert context.resolve("entry_price") == 200.0
    assert context.resolve("position_quantity") == 25
    assert context.resolve("current_price") == 250.0
    assert context.resolve("unrealized_pnl") == 1250.0
    assert context.resolve("position_open") is True


def test_runtime_context_resolves_session_values() -> None:
    current_time = datetime(2026, 8, 30, 14, 0, tzinfo=UTC)

    context = StrategyRuntimeContext(
        market=market(),
        session=SessionContext(
            current_time=current_time,
            entries_today=2,
            trades_today=2,
            bars_since_entry=12,
        ),
    )

    assert context.resolve("entries_today") == 2
    assert context.resolve("trades_today") == 2
    assert context.resolve("bars_since_entry") == 12
    assert context.resolve("current_time") == current_time


def test_runtime_context_resolves_custom_variables() -> None:
    context = StrategyRuntimeContext(
        market=market(),
        variables=(
            StrategyVariable(
                name="risk_per_trade",
                variable_type=VariableType.NUMBER,
                scope=VariableScope.STRATEGY,
                value=1.0,
            ),
            StrategyVariable(
                name="strategy_enabled",
                variable_type=VariableType.BOOLEAN,
                scope=VariableScope.STRATEGY,
                value=True,
            ),
        ),
    )

    assert context.resolve("risk_per_trade") == 1.0
    assert context.resolve("strategy_enabled") is True


def test_unknown_variable_is_rejected() -> None:
    context = StrategyRuntimeContext(
        market=market(),
    )

    with pytest.raises(
        KeyError,
        match="Unknown strategy runtime variable",
    ):
        context.resolve("does_not_exist")


def test_variable_store_resolves_declared_value() -> None:
    from private_quant_terminal.strategy.variables import (
        StrategyVariableStore,
    )

    store = StrategyVariableStore(
        (
            StrategyVariable(
                name="trade_count",
                variable_type=VariableType.NUMBER,
                scope=VariableScope.STRATEGY,
                value=3,
            ),
        )
    )

    assert store.resolve("trade_count") == 3


def test_variable_store_updates_value() -> None:
    from private_quant_terminal.strategy.variables import (
        StrategyVariableStore,
    )

    store = StrategyVariableStore(
        (
            StrategyVariable(
                name="trade_count",
                variable_type=VariableType.NUMBER,
                scope=VariableScope.STRATEGY,
                value=3,
            ),
        )
    )

    store.set("trade_count", 4)

    assert store.resolve("trade_count") == 4


def test_variable_store_rejects_unknown_variable() -> None:
    from private_quant_terminal.strategy.variables import (
        StrategyVariableStore,
    )

    store = StrategyVariableStore()

    with pytest.raises(
        KeyError,
        match="Unknown strategy runtime variable",
    ):
        store.set("does_not_exist", 1)


def test_variable_store_rejects_duplicate_variables() -> None:
    from private_quant_terminal.strategy.variables import (
        StrategyVariableStore,
    )

    variable = StrategyVariable(
        name="trade_count",
        variable_type=VariableType.NUMBER,
        scope=VariableScope.STRATEGY,
        value=0,
    )

    with pytest.raises(
        ValueError,
        match="Strategy variable names must be unique",
    ):
        StrategyVariableStore((variable, variable))


def test_variable_store_enforces_variable_type() -> None:
    from private_quant_terminal.strategy.variables import (
        StrategyVariableStore,
    )

    store = StrategyVariableStore(
        (
            StrategyVariable(
                name="trade_count",
                variable_type=VariableType.NUMBER,
                scope=VariableScope.STRATEGY,
                value=3,
            ),
        )
    )

    with pytest.raises(
        ValueError,
        match="NUMBER variable cannot contain a boolean",
    ):
        store.set("trade_count", True)


def test_variable_store_snapshot_contains_current_values() -> None:
    from private_quant_terminal.strategy.variables import (
        StrategyVariableStore,
    )

    store = StrategyVariableStore(
        (
            StrategyVariable(
                name="trade_count",
                variable_type=VariableType.NUMBER,
                scope=VariableScope.STRATEGY,
                value=3,
            ),
        )
    )

    store.set("trade_count", 7)

    snapshot = store.snapshot()

    assert len(snapshot) == 1
    assert snapshot[0].name == "trade_count"
    assert snapshot[0].value == 7


def test_runtime_context_snapshots_variable_store_value() -> None:
    from private_quant_terminal.strategy.variables import (
        StrategyVariableStore,
    )

    store = StrategyVariableStore(
        (
            StrategyVariable(
                name="trade_count",
                variable_type=VariableType.NUMBER,
                scope=VariableScope.STRATEGY,
                value=3,
            ),
        )
    )

    context = StrategyRuntimeContext(
        market=market(),
        variable_store=store,
    )

    assert context.resolve("trade_count") == 3

    store.set("trade_count", 7)

    assert context.resolve("trade_count") == 3

    next_context = StrategyRuntimeContext(
        market=market(),
        variable_store=store,
    )

    assert next_context.resolve("trade_count") == 7


def test_variable_mutation_updates_store() -> None:
    variable = StrategyVariable(
        name="roll_count",
        variable_type=VariableType.NUMBER,
        scope=VariableScope.STRATEGY,
        value=0,
    )
    store = StrategyVariableStore((variable,))

    store.apply(VariableMutation(name="roll_count", value=1))

    assert store.resolve("roll_count") == 1


def test_variable_mutation_preserves_type_validation() -> None:
    variable = StrategyVariable(
        name="roll_count",
        variable_type=VariableType.NUMBER,
        scope=VariableScope.STRATEGY,
        value=0,
    )
    store = StrategyVariableStore((variable,))

    with pytest.raises(ValueError, match="NUMBER variable requires"):
        store.apply(VariableMutation(name="roll_count", value="invalid"))


def test_variable_mutation_rejects_unknown_variable() -> None:
    store = StrategyVariableStore()

    with pytest.raises(KeyError, match="Unknown strategy runtime variable"):
        store.apply(VariableMutation(name="roll_count", value=1))


def test_variable_mutation_requires_mutation_object() -> None:
    store = StrategyVariableStore()

    with pytest.raises(TypeError, match="VariableMutation"):
        store.apply("roll_count")  # type: ignore[arg-type]
