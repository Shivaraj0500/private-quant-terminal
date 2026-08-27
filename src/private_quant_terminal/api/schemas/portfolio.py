from pydantic import BaseModel, Field


class PositionResponse(BaseModel):
    symbol: str
    quantity: int
    average_price: float


class PortfolioSnapshotRequest(BaseModel):
    prices: dict[str, float] = Field(default_factory=dict)


class PortfolioSnapshotResponse(BaseModel):
    positions: list[PositionResponse]
    realized_pnl: float
    unrealized_pnl: float
    total_pnl: float
    open_position_count: int


class PortfolioRiskRequest(BaseModel):
    prices: dict[str, float] = Field(default_factory=dict)


class PortfolioRiskResponse(BaseModel):
    gross_exposure: float
    net_exposure: float
    long_exposure: float
    short_exposure: float
    largest_position_weight: float
    position_count: int
