from datetime import datetime

from pydantic import BaseModel, Field


class StrategyConditionRequest(BaseModel):
    indicator: str
    operator: str
    value: float


class PositionSizingRequest(BaseModel):
    method: str
    value: float


class StopLossRequest(BaseModel):
    type: str
    value: float | None = None


class TakeProfitRequest(BaseModel):
    type: str
    value: float | None = None


class ExecutionAssumptionsRequest(BaseModel):
    order_type: str = "MARKET"
    slippage_bps: float = 0.0
    transaction_cost_bps: float = 0.0


class StrategyCreateRequest(BaseModel):
    strategy_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    description: str = ""
    instruments: list[str] = Field(min_length=1)
    timeframe: str
    entry_conditions: list[StrategyConditionRequest]
    exit_conditions: list[StrategyConditionRequest]
    position_sizing: PositionSizingRequest
    stop_loss: StopLossRequest
    take_profit: TakeProfitRequest
    execution: ExecutionAssumptionsRequest = (
        ExecutionAssumptionsRequest()
    )


class StrategyVersionResponse(BaseModel):
    strategy_id: str
    version: int
    strategy_hash: str
    name: str
    description: str
    instruments: list[str]
    timeframe: str
    entry_conditions: list[StrategyConditionRequest]
    exit_conditions: list[StrategyConditionRequest]
    position_sizing: PositionSizingRequest
    stop_loss: StopLossRequest
    take_profit: TakeProfitRequest
    execution: ExecutionAssumptionsRequest
    status: str
    created_at: datetime


class StrategyCreateResponse(BaseModel):
    version: StrategyVersionResponse


class StrategyVersionListResponse(BaseModel):
    versions: list[StrategyVersionResponse]
