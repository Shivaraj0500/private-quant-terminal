from fastapi.testclient import TestClient

from private_quant_terminal.api.app import create_app


def test_risk_endpoint_returns_empty_portfolio_risk() -> None:
    app = create_app()
    client = TestClient(app)

    response = client.post(
        "/portfolio/risk",
        json={
            "prices": {},
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["gross_exposure"] == 0.0
    assert data["net_exposure"] == 0.0
    assert data["long_exposure"] == 0.0
    assert data["short_exposure"] == 0.0
    assert data["largest_position_weight"] == 0.0
    assert data["position_count"] == 0


def test_risk_endpoint_calculates_long_position_risk() -> None:
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
    assert execute_response.json()["completed"] is True

    response = client.post(
        "/portfolio/risk",
        json={
            "prices": {
                "NIFTY": 23000.0,
            },
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["gross_exposure"] == 23000.0
    assert data["net_exposure"] == 23000.0
    assert data["long_exposure"] == 23000.0
    assert data["short_exposure"] == 0.0
    assert data["largest_position_weight"] == 1.0
    assert data["position_count"] == 1


def test_risk_endpoint_calculates_multiple_position_risk() -> None:
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

    second_response = client.post(
        "/trading/execute",
        json={
            "symbol": "BANKNIFTY",
            "signal_type": "BUY",
            "price": 48000.0,
        },
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 200

    response = client.post(
        "/portfolio/risk",
        json={
            "prices": {
                "NIFTY": 23000.0,
                "BANKNIFTY": 50000.0,
            },
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["gross_exposure"] == 73000.0
    assert data["net_exposure"] == 73000.0
    assert data["long_exposure"] == 73000.0
    assert data["short_exposure"] == 0.0
    assert data["largest_position_weight"] == 50000.0 / 73000.0
    assert data["position_count"] == 2


def test_risk_endpoint_requires_market_price_for_open_position() -> None:
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

    response = client.post(
        "/portfolio/risk",
        json={
            "prices": {},
        },
    )

    assert response.status_code == 500
