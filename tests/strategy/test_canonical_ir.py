from private_quant_terminal.strategy import (
    ExecutionAssumptions,
    OrderType,
    StrategyIR,
    StrategyStatus,
    StrategyTimeframe,
    canonical_strategy_json,
    strategy_hash,
)


def make_ir() -> StrategyIR:
    return StrategyIR(
        strategy_id="canonical-ir-001",
        name="Canonical IR Strategy",
        description="Canonical IR identity test.",
        version=1,
        status=StrategyStatus.DRAFT,
        instruments=("RELIANCE",),
        timeframe=StrategyTimeframe.ONE_HOUR,
        execution=ExecutionAssumptions(
            order_type=OrderType.MARKET,
            slippage_bps=2.0,
            transaction_cost_bps=1.0,
        ),
    )


def test_canonical_ir_json_is_deterministic() -> None:
    strategy = make_ir()

    assert canonical_strategy_json(strategy) == (
        canonical_strategy_json(strategy)
    )


def test_canonical_ir_hash_is_deterministic() -> None:
    strategy = make_ir()

    assert strategy_hash(strategy) == strategy_hash(strategy)
    assert len(strategy_hash(strategy)) == 64


def test_canonical_ir_hash_changes_when_semantics_change() -> None:
    strategy = make_ir()

    changed = StrategyIR(
        strategy_id=strategy.strategy_id,
        name=strategy.name,
        description=strategy.description,
        version=strategy.version,
        status=strategy.status,
        instruments=strategy.instruments,
        timeframe=strategy.timeframe,
        execution=ExecutionAssumptions(
            order_type=OrderType.MARKET,
            slippage_bps=3.0,
            transaction_cost_bps=1.0,
        ),
    )

    assert strategy_hash(strategy) != strategy_hash(changed)
