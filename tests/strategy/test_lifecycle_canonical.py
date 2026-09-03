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
    StrategyLifecycleService,
    StrategyStatus,
    StrategyTimeframe,
    StrategyVersionRepository,
    TakeProfit,
    TakeProfitType,
)
from private_quant_terminal.strategy.compatibility import (
    strategy_definition_to_ir,
)
from private_quant_terminal.strategy.validation import validate_strategy_ir


def make_strategy() -> StrategyDefinition:
    return StrategyDefinition(
        strategy_id="lifecycle-canonical",
        name="Lifecycle Canonical",
        description="Canonical lifecycle boundary test.",
        instruments=("RELIANCE",),
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
            method=PositionSizingMethod.FIXED_QUANTITY,
            value=1.0,
        ),
        stop_loss=StopLoss(
            type=StopLossType.NONE,
        ),
        take_profit=TakeProfit(
            type=TakeProfitType.NONE,
        ),
        execution=ExecutionAssumptions(
            order_type=OrderType.MARKET,
        ),
    )


def test_legacy_strategy_has_valid_canonical_representation() -> None:
    strategy = make_strategy()

    canonical = strategy_definition_to_ir(strategy, version=1)

    result = validate_strategy_ir(canonical)

    assert result.valid is True
    assert result.issues == ()
    assert canonical.status is StrategyStatus.DRAFT


def test_lifecycle_still_persists_legacy_compatibility_version(tmp_path) -> None:
    repository = StrategyVersionRepository(
        Database(tmp_path / "strategy.db")
    )
    service = StrategyLifecycleService(repository)

    result = service.create_version(make_strategy())

    assert result.version.version == 1
    assert result.version.specification.status is StrategyStatus.VALIDATED

    restored = repository.get(
        strategy_id="lifecycle-canonical",
        version=1,
    )

    assert restored == result.version


def test_lifecycle_rejects_invalid_canonical_ir_before_persistence(
    tmp_path,
    monkeypatch,
) -> None:
    from private_quant_terminal.strategy.ir import StrategyIR
    from private_quant_terminal.strategy.validation import (
        StrategyValidationResult,
        ValidationIssue,
    )

    repository = StrategyVersionRepository(
        Database(tmp_path / "strategy.db")
    )
    service = StrategyLifecycleService(repository)

    original_converter = strategy_definition_to_ir

    def invalid_converter(strategy, *, version):
        canonical = original_converter(strategy, version=version)

        return StrategyIR(
            strategy_id=canonical.strategy_id,
            name=canonical.name,
            description=canonical.description,
            version=canonical.version,
            status=canonical.status,
            instruments=canonical.instruments,
            timeframe=canonical.timeframe,
            variables=canonical.variables,
            rules=canonical.rules,
            states=canonical.states,
            transitions=canonical.transitions,
            data_requirements=canonical.data_requirements,
            position_groups=(),
            session=canonical.session,
            position_sizing=canonical.position_sizing,
            stop_loss=canonical.stop_loss,
            take_profit=canonical.take_profit,
            execution=canonical.execution,
        )

    monkeypatch.setattr(
        "private_quant_terminal.strategy.lifecycle.strategy_definition_to_ir",
        invalid_converter,
    )

    with monkeypatch.context():
        monkeypatch.setattr(
            "private_quant_terminal.strategy.lifecycle.validate_strategy_ir",
            lambda strategy: StrategyValidationResult(
                valid=False,
                issues=(
                    ValidationIssue(
                        field="position_groups",
                        message="Canonical IR test rejection.",
                    ),
                ),
            ),
        )

        import pytest

        with pytest.raises(
            ValueError,
            match="Canonical IR test rejection",
        ):
            service.create_version(make_strategy())

    assert repository.next_version("lifecycle-canonical") == 1
