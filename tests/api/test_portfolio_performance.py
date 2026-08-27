from math import isclose

from fastapi.testclient import TestClient

from private_quant_terminal.api.app import create_app


def test_performance_endpoint_returns_zero_metrics_for_empty_returns() -> None:
    app = create_app()
    client = TestClient(app)

    response = client.post(
        "/portfolio/performance",
        json={
            "returns": [],
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total_return"] == 0.0
    assert data["average_return"] == 0.0
    assert data["best_return"] == 0.0
    assert data["worst_return"] == 0.0
    assert data["volatility"] == 0.0


def test_performance_endpoint_calculates_metrics() -> None:
    app = create_app()
    client = TestClient(app)

    response = client.post(
        "/portfolio/performance",
        json={
            "returns": [
                0.10,
                -0.05,
                0.15,
                0.0,
            ],
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert isclose(
        data["total_return"],
        0.20,
        rel_tol=1e-9,
    )
    assert isclose(
        data["average_return"],
        0.05,
        rel_tol=1e-9,
    )
    assert isclose(
        data["best_return"],
        0.15,
        rel_tol=1e-9,
    )
    assert isclose(
        data["worst_return"],
        -0.05,
        rel_tol=1e-9,
    )
    assert isclose(
        data["volatility"],
        0.0790569415,
        rel_tol=1e-9,
    )


def test_performance_endpoint_calculates_single_return_metrics() -> None:
    app = create_app()
    client = TestClient(app)

    response = client.post(
        "/portfolio/performance",
        json={
            "returns": [
                0.10,
            ],
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total_return"] == 0.10
    assert data["average_return"] == 0.10
    assert data["best_return"] == 0.10
    assert data["worst_return"] == 0.10
    assert data["volatility"] == 0.0


def test_performance_endpoint_defaults_to_empty_returns() -> None:
    app = create_app()
    client = TestClient(app)

    response = client.post(
        "/portfolio/performance",
        json={},
    )

    assert response.status_code == 200

    data = response.json()

    assert data == {
        "total_return": 0.0,
        "average_return": 0.0,
        "best_return": 0.0,
        "worst_return": 0.0,
        "volatility": 0.0,
    }
