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


class ResearchTradeAnalyticsResponse(BaseModel):
    total_trades: int
    average_trade: float
    best_trade: float
    worst_trade: float
    average_holding_time_seconds: float
    shortest_holding_time_seconds: float
    longest_holding_time_seconds: float
    max_consecutive_wins: int
    max_consecutive_losses: int


class ResearchBehaviorFindingResponse(BaseModel):
    category: str
    statement: str
    evidence: str


class ResearchBehaviorDiagnosticsResponse(BaseModel):
    entry_hour_distribution: list[tuple[int, int]]
    exit_hour_distribution: list[tuple[int, int]]
    winning_trade_count: int
    losing_trade_count: int
    zero_pnl_trade_count: int
    winning_pnl: float
    losing_pnl: float
    average_winning_trade: float
    average_losing_trade: float
    loss_by_entry_hour: list[tuple[int, float]]


class ResearchOptionTradeEvidenceResponse(BaseModel):
    group_id: str
    instrument_identifier: str
    option_type: str
    strike: float
    expiry: str
    entry_time: datetime
    exit_time: datetime
    entry_price: float
    exit_price: float
    quantity: float
    net_pnl: float
    holding_time_seconds: float
    expiry_day: bool
    pre_expiry: bool


class ResearchOptionDiagnosticsResponse(BaseModel):
    option_fill_count: int
    option_trade_count: int
    call_trade_count: int
    put_trade_count: int
    winning_option_trade_count: int
    losing_option_trade_count: int
    option_net_pnl: float
    average_option_trade: float
    expiry_day_trade_count: int
    expiry_day_net_pnl: float
    pre_expiry_trade_count: int
    pre_expiry_net_pnl: float
    strike_distribution: list[tuple[float, int]]
    expiry_distribution: list[tuple[str, int]]
    trades: list[ResearchOptionTradeEvidenceResponse]


class ResearchRiskDiagnosticsResponse(BaseModel):
    observation_count: int
    maximum_gross_exposure: float
    average_gross_exposure: float
    maximum_net_exposure: float
    maximum_long_exposure: float
    maximum_short_exposure: float
    maximum_position_concentration: float
    maximum_gross_exposure_ratio: float
    maximum_net_exposure_ratio: float
    worst_observation_loss: float
    worst_daily_loss: float


class ResearchRiskFindingResponse(BaseModel):
    category: str
    statement: str
    evidence: str


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
    trade_analytics: ResearchTradeAnalyticsResponse
    behavior_diagnostics: ResearchBehaviorDiagnosticsResponse
    behavior_findings: list[ResearchBehaviorFindingResponse]
    risk_diagnostics: ResearchRiskDiagnosticsResponse
    risk_findings: list[ResearchRiskFindingResponse]
    option_diagnostics: ResearchOptionDiagnosticsResponse


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
