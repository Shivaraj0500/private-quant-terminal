from datetime import UTC, datetime

from fastapi.testclient import TestClient

from private_quant_terminal.api.app import app
from private_quant_terminal.api.dependencies import (
    get_market_data_service,
)
from private_quant_terminal.models.candle import Candle
from private_quant_terminal.models.quote import Quote


class StubMarketDataService:
    def __init__(
        self,
        quote: Quote,
        candles: tuple[Candle, ...],
    ) -> None:
        self.quote = quote
        self.candles = candles
        self.requested_symbols: list[str] = []
        self.candle_requests: list[tuple[str, int | None]] = []

    def get_latest_quote(self, symbol: str) -> Quote:
        self.requested_symbols.append(symbol)
        return self.quote

    def get_candles(
        self,
        symbol: str,
        limit: int | None = None,
    ) -> tuple[Candle, ...]:
        self.candle_requests.append(
            (symbol, limit)
        )

        if limit is None:
            return self.candles

        return self.candles[-limit:]


def create_service() -> StubMarketDataService:
    quote = Quote(
        symbol="NIFTY",
        exchange="NSE",
        timestamp=datetime(
            2026,
            8,
            28,
            10,
            0,
            0,
        ),
        last_price=25000.0,
        open=24900.0,
        high=25100.0,
        low=24850.0,
        previous_close=24800.0,
        volume=1000000.0,
    )

    candles = (
        Candle(
            timestamp=datetime(
                2026,
                8,
                28,
                9,
                15,
                0,
            ),
            open=24900.0,
            high=25000.0,
            low=24850.0,
            close=24950.0,
            volume=500000.0,
        ),
        Candle(
            timestamp=datetime(
                2026,
                8,
                28,
                9,
                16,
                0,
            ),
            open=24950.0,
            high=25100.0,
            low=24900.0,
            close=25000.0,
            volume=600000.0,
        ),
    )

    return StubMarketDataService(
        quote=quote,
        candles=candles,
    )


def test_get_latest_quote_returns_quote() -> None:
    service = create_service()

    app.dependency_overrides[
        get_market_data_service
    ] = lambda: service

    client = TestClient(app)

    try:
        response = client.get(
            "/market-data/NIFTY/quote"
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200

    assert response.json() == {
        "symbol": "NIFTY",
        "exchange": "NSE",
        "timestamp": "2026-08-28T10:00:00",
        "last_price": 25000.0,
        "open": 24900.0,
        "high": 25100.0,
        "low": 24850.0,
        "previous_close": 24800.0,
        "volume": 1000000.0,
    }

    assert service.requested_symbols == ["NIFTY"]


def test_get_candles_returns_all_candles() -> None:
    service = create_service()

    app.dependency_overrides[
        get_market_data_service
    ] = lambda: service

    client = TestClient(app)

    try:
        response = client.get(
            "/market-data/NIFTY/candles"
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200

    assert response.json() == [
        {
            "timestamp": "2026-08-28T09:15:00",
            "open": 24900.0,
            "high": 25000.0,
            "low": 24850.0,
            "close": 24950.0,
            "volume": 500000.0,
        },
        {
            "timestamp": "2026-08-28T09:16:00",
            "open": 24950.0,
            "high": 25100.0,
            "low": 24900.0,
            "close": 25000.0,
            "volume": 600000.0,
        },
    ]

    assert service.candle_requests == [
        ("NIFTY", None)
    ]


def test_get_candles_returns_limited_candles() -> None:
    service = create_service()

    app.dependency_overrides[
        get_market_data_service
    ] = lambda: service

    client = TestClient(app)

    try:
        response = client.get(
            "/market-data/NIFTY/candles?limit=1"
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200

    assert response.json() == [
        {
            "timestamp": "2026-08-28T09:16:00",
            "open": 24950.0,
            "high": 25100.0,
            "low": 24900.0,
            "close": 25000.0,
            "volume": 600000.0,
        },
    ]

    assert service.candle_requests == [
        ("NIFTY", 1)
    ]


def test_get_candles_rejects_invalid_limit() -> None:
    service = create_service()

    app.dependency_overrides[
        get_market_data_service
    ] = lambda: service

    client = TestClient(app)

    try:
        response = client.get(
            "/market-data/NIFTY/candles?limit=0"
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 422
    assert service.candle_requests == []
