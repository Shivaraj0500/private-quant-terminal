from collections.abc import Sequence

from fastapi import APIRouter, Depends, Query

from private_quant_terminal.api.dependencies import (
    get_market_data_service,
)
from private_quant_terminal.api.schemas.market_data import (
    CandleResponse,
    QuoteResponse,
)
from private_quant_terminal.services.market_data import (
    MarketDataService,
)

router = APIRouter(
    prefix="/market-data",
    tags=["market-data"],
)


@router.get(
    "/{symbol}/quote",
    response_model=QuoteResponse,
)
def get_latest_quote(
    symbol: str,
    service: MarketDataService = Depends(
        get_market_data_service
    ),
) -> QuoteResponse:
    """Return the latest market quote for a symbol."""
    quote = service.get_latest_quote(symbol)

    return QuoteResponse(
        symbol=quote.symbol,
        exchange=quote.exchange,
        timestamp=quote.timestamp,
        last_price=quote.last_price,
        open=quote.open,
        high=quote.high,
        low=quote.low,
        previous_close=quote.previous_close,
        volume=quote.volume,
    )


@router.get(
    "/{symbol}/candles",
    response_model=list[CandleResponse],
)
def get_candles(
    symbol: str,
    limit: int | None = Query(
        default=None,
        ge=1,
    ),
    service: MarketDataService = Depends(
        get_market_data_service
    ),
) -> Sequence[CandleResponse]:
    """Return cached candles for a symbol."""
    candles = service.get_candles(
        symbol=symbol,
        limit=limit,
    )

    return tuple(
        CandleResponse(
            timestamp=candle.timestamp,
            open=candle.open,
            high=candle.high,
            low=candle.low,
            close=candle.close,
            volume=candle.volume,
        )
        for candle in candles
    )