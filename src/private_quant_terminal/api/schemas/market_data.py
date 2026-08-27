from datetime import datetime

from pydantic import BaseModel


class QuoteResponse(BaseModel):
    """API response model for a market quote."""

    symbol: str
    exchange: str
    timestamp: datetime
    last_price: float
    open: float | None = None
    high: float | None = None
    low: float | None = None
    previous_close: float | None = None
    volume: float | None = None


class CandleResponse(BaseModel):
    """API response model for a market candle."""

    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float