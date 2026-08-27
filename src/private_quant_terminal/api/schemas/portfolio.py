from pydantic import BaseModel, Field


class PositionResponse(BaseModel):
    symbol: str
    quantity: int
    average_price: float


class ClosedTradeResponse(BaseModel):
    symbol: str
    quantity: int
    entry_price: float
    exit_price: float
    realized_pnl: float


class TradingPerformanceResponse(BaseModel):
    realized_pnl: float
    unrealized_pnl: float
    total_pnl: float
    winning_trades: int
    losing_trades: int
    win_rate: float
    average_win: float
    average_loss: float
    profit_factor: float


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


class PortfolioPerformanceRequest(BaseModel):
    returns: list[float] = Field(default_factory=list)


class PortfolioPerformanceResponse(BaseModel):
    total_return: float
    average_return: float
    best_return: float
    worst_return: float
    volatility: float
