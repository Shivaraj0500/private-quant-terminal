from fastapi import APIRouter, HTTPException, Request

from private_quant_terminal.api.schemas.strategy import (
    ExecutionAssumptionsRequest,
    PositionSizingRequest,
    StopLossRequest,
    StrategyConditionRequest,
    StrategyCreateRequest,
    StrategyCreateResponse,
    StrategyVersionListResponse,
    StrategyVersionResponse,
    TakeProfitRequest,
)
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
    StrategyTimeframe,
    TakeProfit,
    TakeProfitType,
)

router = APIRouter(
    prefix="/strategies",
    tags=["strategies"],
)
@router.get(
    "",
    response_model=StrategyVersionListResponse,
)
def list_strategies(
    request: Request,
) -> StrategyVersionListResponse:
    """Return the latest persisted version of every strategy."""

    repository = request.app.state.container.strategy_repository

    versions = repository.list_latest()

    return StrategyVersionListResponse(
        versions=[
            _to_response(version)
            for version in versions
        ]
    )


@router.post(
    "",
    response_model=StrategyCreateResponse,
)
def create_strategy(
    payload: StrategyCreateRequest,
    request: Request,
) -> StrategyCreateResponse:
    """Validate and persist a new immutable strategy version."""

    try:
        strategy = StrategyDefinition(
            strategy_id=payload.strategy_id,
            name=payload.name,
            description=payload.description,
            instruments=tuple(payload.instruments),
            timeframe=StrategyTimeframe(payload.timeframe),
            entry_conditions=tuple(
                _condition(condition)
                for condition in payload.entry_conditions
            ),
            exit_conditions=tuple(
                _condition(condition)
                for condition in payload.exit_conditions
            ),
            position_sizing=PositionSizing(
                method=PositionSizingMethod(
                    payload.position_sizing.method
                ),
                value=payload.position_sizing.value,
            ),
            stop_loss=StopLoss(
                type=StopLossType(payload.stop_loss.type),
                value=payload.stop_loss.value,
            ),
            take_profit=TakeProfit(
                type=TakeProfitType(payload.take_profit.type),
                value=payload.take_profit.value,
            ),
            execution=ExecutionAssumptions(
                order_type=OrderType(
                    payload.execution.order_type
                ),
                slippage_bps=payload.execution.slippage_bps,
                transaction_cost_bps=(
                    payload.execution.transaction_cost_bps
                ),
            ),
        )

        result = StrategyLifecycleService(
            request.app.state.container.strategy_repository
        ).create_version(strategy)

    except (ValueError, KeyError) as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    return StrategyCreateResponse(
        version=_to_response(result.version)
    )


@router.get(
    "",
    response_model=StrategyVersionListResponse,
)
def list_all_strategies(
    request: Request,
) -> StrategyVersionListResponse:
    """Return all persisted strategy versions."""

    repository = request.app.state.container.strategy_repository

    versions = repository.list_all()

    return StrategyVersionListResponse(
        versions=[
            _to_response(version)
            for version in versions
        ]
    )


@router.get(
    "/{strategy_id}/versions/{version}",
    response_model=StrategyVersionResponse,
)
def get_strategy_version(
    strategy_id: str,
    version: int,
    request: Request,
) -> StrategyVersionResponse:
    """Return one immutable strategy version."""

    repository = request.app.state.container.strategy_repository

    try:
        result = repository.get(
            strategy_id=strategy_id,
            version=version,
        )
    except KeyError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    return _to_response(result)


@router.get(
    "/{strategy_id}/versions",
    response_model=StrategyVersionListResponse,
)
def list_strategy_versions(
    strategy_id: str,
    request: Request,
) -> StrategyVersionListResponse:
    """Return all persisted versions of a strategy."""

    repository = request.app.state.container.strategy_repository

    versions = []

    version_number = 1

    while True:
        try:
            versions.append(
                repository.get(
                    strategy_id=strategy_id,
                    version=version_number,
                )
            )
        except KeyError:
            break

        version_number += 1

    return StrategyVersionListResponse(
        versions=[
            _to_response(version)
            for version in versions
        ]
    )


def _condition(
    condition: StrategyConditionRequest,
) -> StrategyCondition:
    return StrategyCondition(
        indicator=condition.indicator,
        operator=ConditionOperator(condition.operator),
        value=condition.value,
    )


def _to_response(version) -> StrategyVersionResponse:
    specification = version.specification

    return StrategyVersionResponse(
        strategy_id=version.strategy_id,
        version=version.version,
        strategy_hash=_strategy_hash(version),
        name=specification.name,
        description=specification.description,
        instruments=list(specification.instruments),
        timeframe=specification.timeframe.value,
        entry_conditions=[
            _condition_response(condition)
            for condition in specification.entry_conditions
        ],
        exit_conditions=[
            _condition_response(condition)
            for condition in specification.exit_conditions
        ],
        position_sizing=PositionSizingRequest(
            method=specification.position_sizing.method.value,
            value=specification.position_sizing.value,
        ),
        stop_loss=StopLossRequest(
            type=specification.stop_loss.type.value,
            value=specification.stop_loss.value,
        ),
        take_profit=TakeProfitRequest(
            type=specification.take_profit.type.value,
            value=specification.take_profit.value,
        ),
        execution=ExecutionAssumptionsRequest(
            order_type=specification.execution.order_type.value,
            slippage_bps=specification.execution.slippage_bps,
            transaction_cost_bps=(
                specification.execution.transaction_cost_bps
            ),
        ),
        status=specification.status.value,
        created_at=version.created_at,
    )


def _condition_response(
    condition: StrategyCondition,
) -> StrategyConditionRequest:
    return StrategyConditionRequest(
        indicator=condition.indicator,
        operator=condition.operator.value,
        value=condition.value,
    )


def _strategy_hash(version) -> str:
    from private_quant_terminal.strategy.canonical import (
        strategy_hash,
    )

    return strategy_hash(version.specification)
