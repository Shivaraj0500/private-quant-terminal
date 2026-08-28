from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from private_quant_terminal.models import Candle
from private_quant_terminal.research.run import ResearchRun
from private_quant_terminal.strategy.ir import StrategyVersion


class ResearchExecutionEventType(str, Enum):
    """Events emitted by a deterministic research execution."""

    ENTRY = "ENTRY"
    EXIT = "EXIT"


@dataclass(frozen=True)
class ResearchExecutionRequest:
    """Immutable input contract for research execution."""

    run: ResearchRun
    strategy_version: StrategyVersion
    candles: tuple[Candle, ...]


@dataclass(frozen=True)
class ResearchTrade:
    """One completed simulated trade."""

    symbol: str
    entry_time: datetime
    exit_time: datetime
    entry_price: float
    exit_price: float
    quantity: float
    gross_pnl: float
    transaction_cost: float
    net_pnl: float


@dataclass(frozen=True)
class ResearchExecutionEvent:
    """One event generated during research execution."""

    timestamp: datetime
    event_type: ResearchExecutionEventType
    symbol: str
    price: float
    quantity: float


@dataclass(frozen=True)
class ResearchExecutionResult:
    """Immutable result produced by research execution."""

    run_id: str
    events: tuple[ResearchExecutionEvent, ...]
    trades: tuple[ResearchTrade, ...]
    final_equity: float
