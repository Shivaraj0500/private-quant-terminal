from fastapi.testclient import TestClient

from private_quant_terminal.api.app import create_app


def test_closed_trades_endpoint_returns_empty_list() -> None:
    app = create_app()
    client = TestClient(app)

    response = client.get("/portfolio/closed-trades")

    assert response.status_code == 200
    assert response.json() == []


def test_closed_trades_endpoint_returns_completed_long_trade() -> None:
    app = create_app()
    client = TestClient(app)

    buy_response = client.post(
        "/trading/execute",
        json={
            "symbol": "NIFTY",
            "signal_type": "BUY",
            "price": 22000.0,
        },
    )

    assert buy_response.status_code == 200
    assert buy_response.json()["completed"] is True

    sell_response = client.post(
        "/trading/execute",
        json={
            "symbol": "NIFTY",
            "signal_type": "SELL",
            "price": 22500.0,
        },
    )

    assert sell_response.status_code == 200
    assert sell_response.json()["completed"] is True

    response = client.get("/portfolio/closed-trades")

    assert response.status_code == 200

    data = response.json()

    assert data == [
        {
            "symbol": "NIFTY",
            "quantity": 1,
            "entry_price": 22000.0,
            "exit_price": 22500.0,
            "realized_pnl": 500.0,
        }
    ]


def test_closed_trades_endpoint_returns_completed_short_trade() -> None:
    app = create_app()
    client = TestClient(app)

    sell_response = client.post(
        "/trading/execute",
        json={
            "symbol": "BANKNIFTY",
            "signal_type": "SELL",
            "price": 48000.0,
        },
    )

    assert sell_response.status_code == 200
    assert sell_response.json()["completed"] is True

    buy_response = client.post(
        "/trading/execute",
        json={
            "symbol": "BANKNIFTY",
            "signal_type": "BUY",
            "price": 47000.0,
        },
    )

    assert buy_response.status_code == 200
    assert buy_response.json()["completed"] is True

    response = client.get("/portfolio/closed-trades")

    assert response.status_code == 200

    data = response.json()

    assert data == [
        {
            "symbol": "BANKNIFTY",
            "quantity": 1,
            "entry_price": 48000.0,
            "exit_price": 47000.0,
            "realized_pnl": 1000.0,
        }
    ]


def test_closed_trades_endpoint_returns_multiple_completed_trades() -> None:
    app = create_app()
    client = TestClient(app)

    executions = [
        {
            "symbol": "NIFTY",
            "signal_type": "BUY",
            "price": 22000.0,
        },
        {
            "symbol": "NIFTY",
            "signal_type": "SELL",
            "price": 22500.0,
        },
        {
            "symbol": "BANKNIFTY",
            "signal_type": "SELL",
            "price": 48000.0,
        },
        {
            "symbol": "BANKNIFTY",
            "signal_type": "BUY",
            "price": 47000.0,
        },
    ]

    for execution in executions:
        response = client.post(
            "/trading/execute",
            json=execution,
        )

        assert response.status_code == 200
        assert response.json()["completed"] is True

    response = client.get("/portfolio/closed-trades")

    assert response.status_code == 200

    data = response.json()

    assert data == [
        {
            "symbol": "NIFTY",
            "quantity": 1,
            "entry_price": 22000.0,
            "exit_price": 22500.0,
            "realized_pnl": 500.0,
        },
        {
            "symbol": "BANKNIFTY",
            "quantity": 1,
            "entry_price": 48000.0,
            "exit_price": 47000.0,
            "realized_pnl": 1000.0,
        },
    ]