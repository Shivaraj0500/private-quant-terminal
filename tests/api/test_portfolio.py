from fastapi.testclient import TestClient

from private_quant_terminal.api.app import create_app
from private_quant_terminal.brokers.execution_report import (
    ExecutionReport,
)
from private_quant_terminal.brokers.order_side import OrderSide
from private_quant_terminal.brokers.order_status import OrderStatus


def test_positions_endpoint_returns_empty_list() -> None:
    app = create_app()
    client = TestClient(app)

    response = client.get("/portfolio/positions")

    assert response.status_code == 200
    assert response.json() == []


def test_positions_endpoint_returns_shared_positions() -> None:
    app = create_app()

    app.state.container.position_manager.apply_execution(
        symbol="NIFTY",
        side=OrderSide.BUY,
        quantity=50,
        price=22000.0,
        report=ExecutionReport(
            order_id="ORDER-1",
            status=OrderStatus.FILLED,
            filled_quantity=50,
            remaining_quantity=0,
            average_price=22000.0,
        ),
    )

    client = TestClient(app)

    response = client.get("/portfolio/positions")

    assert response.status_code == 200
    assert response.json() == [
        {
            "symbol": "NIFTY",
            "quantity": 50,
            "average_price": 22000.0,
        }
    ]


def test_snapshot_endpoint_returns_empty_portfolio() -> None:
    app = create_app()
    client = TestClient(app)

    response = client.post(
        "/portfolio/snapshot",
        json={
            "prices": {},
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "positions": [],
        "realized_pnl": 0.0,
        "unrealized_pnl": 0.0,
        "total_pnl": 0.0,
        "open_position_count": 0,
    }


def test_snapshot_endpoint_calculates_portfolio_pnl() -> None:
    app = create_app()

    app.state.container.position_manager.apply_execution(
        symbol="NIFTY",
        side=OrderSide.BUY,
        quantity=10,
        price=100.0,
        report=ExecutionReport(
            order_id="ORDER-1",
            status=OrderStatus.FILLED,
            filled_quantity=10,
            remaining_quantity=0,
            average_price=100.0,
        ),
    )

    client = TestClient(app)

    response = client.post(
        "/portfolio/snapshot",
        json={
            "prices": {
                "NIFTY": 110.0,
            },
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "positions": [
            {
                "symbol": "NIFTY",
                "quantity": 10,
                "average_price": 100.0,
            }
        ],
        "realized_pnl": 0.0,
        "unrealized_pnl": 100.0,
        "total_pnl": 100.0,
        "open_position_count": 1,
    }


def test_snapshot_endpoint_uses_average_price_when_price_missing() -> None:
    app = create_app()

    app.state.container.position_manager.apply_execution(
        symbol="NIFTY",
        side=OrderSide.BUY,
        quantity=10,
        price=100.0,
        report=ExecutionReport(
            order_id="ORDER-1",
            status=OrderStatus.FILLED,
            filled_quantity=10,
            remaining_quantity=0,
            average_price=100.0,
        ),
    )

    client = TestClient(app)

    response = client.post(
        "/portfolio/snapshot",
        json={
            "prices": {},
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["unrealized_pnl"] == 0.0
    assert data["total_pnl"] == 0.0
    assert data["open_position_count"] == 1