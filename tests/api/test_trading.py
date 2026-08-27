from fastapi.testclient import TestClient

from private_quant_terminal.api.app import create_app


def test_execute_buy_signal_returns_completed_execution() -> None:
    app = create_app()
    client = TestClient(app)

    response = client.post(
        "/trading/execute",
        json={
            "symbol": "NIFTY",
            "signal_type": "BUY",
            "price": 22000.0,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["completed"] is True
    assert data["reason"] is None
    assert data["order_id"] == "ORDER-1"
    assert data["average_price"] == 22000.0
    assert data["filled_quantity"] == 1


def test_execute_hold_signal_does_not_create_order() -> None:
    app = create_app()
    client = TestClient(app)

    response = client.post(
        "/trading/execute",
        json={
            "symbol": "NIFTY",
            "signal_type": "HOLD",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["completed"] is False
    assert data["order_id"] is None
    assert data["average_price"] is None
    assert data["filled_quantity"] is None
    assert data["reason"] == "Signal type HOLD does not create an order"


def test_execute_buy_without_price_returns_not_completed() -> None:
    app = create_app()
    client = TestClient(app)

    response = client.post(
        "/trading/execute",
        json={
            "symbol": "NIFTY",
            "signal_type": "BUY",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["completed"] is False
    assert data["order_id"] is None
    assert data["average_price"] is None
    assert data["filled_quantity"] is None
    assert data["reason"] == "Executable signals require a price"


def test_execute_rejects_invalid_signal_type() -> None:
    app = create_app()
    client = TestClient(app)

    response = client.post(
        "/trading/execute",
        json={
            "symbol": "NIFTY",
            "signal_type": "INVALID",
            "price": 22000.0,
        },
    )

    assert response.status_code == 422