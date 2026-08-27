from pydantic import BaseModel

from private_quant_terminal.strategies.signal import SignalType


class TradingRequest(BaseModel):
    symbol: str
    signal_type: SignalType
    price: float | None = None


class TradingResponse(BaseModel):
    completed: bool
    reason: str | None = None
    order_id: str | None = None
    average_price: float | None = None
    filled_quantity: int | None = None