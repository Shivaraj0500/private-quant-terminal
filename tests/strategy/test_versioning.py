from datetime import UTC, datetime

import pytest

from private_quant_terminal.persistence import Database
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
    StrategyTimeframe,
    StrategyVersion,
    StrategyVersionRepository,
    TakeProfit,
    TakeProfitType,
    canonical_strategy_json,
    strategy_hash,
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


def test_canonical_json_is_deterministic() -> None:
    strategy = make_strategy()

    assert canonical_strategy_json(strategy) == (
        canonical_strategy_json(strategy)
    )


def test_strategy_hash_is_deterministic() -> None:
    strategy = make_strategy()

    assert strategy_hash(strategy) == strategy_hash(strategy)
    assert len(strategy_hash(strategy)) == 64


def test_repository_round_trip(tmp_path) -> None:
    database = Database(tmp_path / "strategies.db")
    repository = StrategyVersionRepository(database)

    strategy = make_strategy()

    version = StrategyVersion(
        strategy_id=strategy.strategy_id,
        version=1,
        specification=strategy,
        created_at=datetime.now(UTC),
    )

    repository.save(version)

    restored = repository.get(
        strategy_id="strategy-001",
        version=1,
    )

    assert restored == version


def test_repository_assigns_next_version(tmp_path) -> None:
    database = Database(tmp_path / "strategies.db")
    repository = StrategyVersionRepository(database)

    assert repository.next_version("strategy-001") == 1

    strategy = make_strategy()

    repository.save(
        StrategyVersion(
            strategy_id=strategy.strategy_id,
            version=1,
            specification=strategy,
            created_at=datetime.now(UTC),
        )
    )

    assert repository.next_version("strategy-001") == 2


def test_existing_version_cannot_change(tmp_path) -> None:
    database = Database(tmp_path / "strategies.db")
    repository = StrategyVersionRepository(database)

    strategy = make_strategy()

    repository.save(
        StrategyVersion(
            strategy_id=strategy.strategy_id,
            version=1,
            specification=strategy,
            created_at=datetime.now(UTC),
        )
    )

    changed = StrategyDefinition(
        strategy_id=strategy.strategy_id,
        name="Changed Strategy",
        description=strategy.description,
        instruments=strategy.instruments,
        timeframe=strategy.timeframe,
        entry_conditions=strategy.entry_conditions,
        exit_conditions=strategy.exit_conditions,
        position_sizing=strategy.position_sizing,
        stop_loss=strategy.stop_loss,
        take_profit=strategy.take_profit,
        execution=strategy.execution,
        status=strategy.status,
    )

    with pytest.raises(ValueError, match="immutable"):
        repository.save(
            StrategyVersion(
                strategy_id=strategy.strategy_id,
                version=1,
                specification=changed,
                created_at=datetime.now(UTC),
            )
        )


def test_unknown_version_raises(tmp_path) -> None:
    database = Database(tmp_path / "strategies.db")
    repository = StrategyVersionRepository(database)

    with pytest.raises(KeyError, match="Unknown strategy version"):
        repository.get("missing", 1)
