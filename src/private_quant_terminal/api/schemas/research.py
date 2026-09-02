from datetime import datetime
from typing import Any

from pydantic import BaseModel


class ResearchRunRequest(BaseModel):
    strategy_id: str
    strategy_version: int
    symbol: str
    timeframe: str
    parameters: dict[str, Any] = {}
    initial_equity: float = 100000.0


class ResearchRunSummary(BaseModel):
    run_id: str
    strategy_id: str
    strategy_version: int
    strategy_hash: str
    dataset_hash: str
    symbol: str
    timeframe: str
    start_time: datetime
    end_time: datetime
    parameters: dict[str, Any]
    parameters_hash: str
    status: str
    created_at: datetime


class ResearchTradeResponse(BaseModel):
    symbol: str
    entry_time: datetime
    exit_time: datetime
    entry_price: float
    exit_price: float
    quantity: float
    gross_pnl: float
    transaction_cost: float
    net_pnl: float


class ResearchEventResponse(BaseModel):
    timestamp: datetime
    event_type: str
    symbol: str
    price: float
    quantity: float


class ResearchEvidenceReferenceResponse(BaseModel):
    category: str
    code: str
    description: str


class ResearchIntelligenceResponse(BaseModel):
    conclusion: str
    confidence: str
    strengths: list[str]
    limitations: list[str]
    next_investigations: list[str]
    evidence: list[ResearchEvidenceReferenceResponse]


class ResearchIntegrityFindingResponse(BaseModel):
    severity: str
    code: str
    message: str


class ResearchIntegrityResponse(BaseModel):
    status: str
    passed: bool
    warnings: int
    failures: int
    findings: list[ResearchIntegrityFindingResponse]


class ResearchPerformanceResponse(BaseModel):
    realized_pnl: float
    unrealized_pnl: float
    total_pnl: float
    winning_trades: int
    losing_trades: int
    win_rate: float
    average_win: float
    average_loss: float
    profit_factor: float
    returns: list[float]
    max_drawdown: float
    max_drawdown_percent: float
    sharpe_ratio: float
    sortino_ratio: float
    downside_deviation: float
    calmar_ratio: float


class ResearchEquityPointResponse(BaseModel):
    timestamp: datetime
    equity: float


class ResearchExecutionResponse(BaseModel):
    run_id: str
    events: list[ResearchEventResponse]
    trades: list[ResearchTradeResponse]
    equity_curve: list[ResearchEquityPointResponse]
    final_equity: float


class ResearchRunResponse(BaseModel):
    run: ResearchRunSummary
    execution: ResearchExecutionResponse
    performance: ResearchPerformanceResponse
    integrity: ResearchIntegrityResponse
    intelligence: ResearchIntelligenceResponse | None = None
