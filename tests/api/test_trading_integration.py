from fastapi.testclient import TestClient

from private_quant_terminal.api.app import create_app


def test_execute_buy_updates_shared_portfolio_position() -> None:
    app = create_app()
    client = TestClient(app)

    execute_response = client.post(
        "/trading/execute",
        json={
            "symbol": "NIFTY",
            "signal_type": "BUY",
            "price": 22000.0,
        },
    )

    assert execute_response.status_code == 200

    execution_data = execute_response.json()

    assert execution_data["completed"] is True
    assert execution_data["order_id"] == "ORDER-1"
    assert execution_data["average_price"] == 22000.0
    assert execution_data["filled_quantity"] is not None

    positions_response = client.get("/portfolio/positions")

    assert positions_response.status_code == 200

    positions = positions_response.json()

    assert len(positions) == 1
    assert positions[0]["symbol"] == "NIFTY"
    assert positions[0]["quantity"] == execution_data["filled_quantity"]
    assert positions[0]["average_price"] == 22000.0


def test_multiple_trades_update_the_same_portfolio_position() -> None:
    app = create_app()
    client = TestClient(app)

    first_response = client.post(
        "/trading/execute",
        json={
            "symbol": "NIFTY",
            "signal_type": "BUY",
            "price": 22000.0,
        },
    )

    assert first_response.status_code == 200
    assert first_response.json()["completed"] is True

    second_response = client.post(
        "/trading/execute",
        json={
            "symbol": "NIFTY",
            "signal_type": "BUY",
            "price": 23000.0,
        },
    )

    assert second_response.status_code == 200
    assert second_response.json()["completed"] is True

    positions_response = client.get("/portfolio/positions")

    assert positions_response.status_code == 200

    positions = positions_response.json()

    assert len(positions) == 1
    assert positions[0]["symbol"] == "NIFTY"

    expected_quantity = (
        first_response.json()["filled_quantity"]
        + second_response.json()["filled_quantity"]
    )

    assert positions[0]["quantity"] == expected_quantity
    assert positions[0]["average_price"] == 22500.0
