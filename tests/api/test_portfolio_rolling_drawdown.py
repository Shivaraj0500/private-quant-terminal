import pytest
from fastapi.testclient import TestClient

from private_quant_terminal.api.app import create_app


class TestPortfolioRollingDrawdownApi:
    def test_returns_rolling_drawdown_metrics(self) -> None:
        client = TestClient(create_app())

        response = client.post(
            "/portfolio/rolling-drawdown",
            json={
                "values": [
                    100.0,
                    120.0,
                    90.0,
                    110.0,
                ],
                "window": 3,
            },
        )

        assert response.status_code == 200

        data = response.json()

        assert data["rolling_drawdown"] == pytest.approx(
            [
                -0.25,
                -0.08333333333333333,
            ]
        )
        assert data["rolling_max_drawdown"] == pytest.approx(
            [
                -0.25,
                -0.25,
            ]
        )

    def test_rejects_empty_values(self) -> None:
        client = TestClient(create_app())

        response = client.post(
            "/portfolio/rolling-drawdown",
            json={
                "values": [],
                "window": 1,
            },
        )

        assert response.status_code == 422
        assert response.json()["detail"] == (
            "values must not be empty"
        )

    def test_rejects_non_positive_values(self) -> None:
        client = TestClient(create_app())

        response = client.post(
            "/portfolio/rolling-drawdown",
            json={
                "values": [
                    100.0,
                    0.0,
                ],
                "window": 2,
            },
        )

        assert response.status_code == 422
        assert response.json()["detail"] == (
            "values must be greater than zero"
        )

    def test_rejects_window_larger_than_values(self) -> None:
        client = TestClient(create_app())

        response = client.post(
            "/portfolio/rolling-drawdown",
            json={
                "values": [
                    100.0,
                    120.0,
                ],
                "window": 3,
            },
        )

        assert response.status_code == 422
        assert response.json()["detail"] == (
            "window must not exceed the number of values"
        )
