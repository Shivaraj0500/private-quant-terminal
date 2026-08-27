import pytest
from fastapi.testclient import TestClient

from private_quant_terminal.api.app import create_app


class TestPortfolioRollingPerformanceApi:
    def test_returns_rolling_performance_metrics(self) -> None:
        client = TestClient(create_app())

        response = client.post(
            "/portfolio/rolling-performance",
            json={
                "returns": [
                    0.10,
                    -0.05,
                    0.15,
                ],
                "window": 2,
            },
        )

        assert response.status_code == 200

        data = response.json()

        assert data["rolling_returns"] == pytest.approx(
            [
                0.045,
                0.0925,
            ]
        )
        assert data["rolling_average"] == pytest.approx(
            [
                0.025,
                0.05,
            ]
        )
        assert data["rolling_volatility"] == pytest.approx(
            [
                0.075,
                0.1,
            ]
        )
        assert data["rolling_drawdown"] == pytest.approx(
            [
                -0.05,
                0.0,
            ]
        )
        assert data["rolling_max_drawdown"] == pytest.approx(
            [
                -0.05,
                0.0,
            ]
        )

    def test_rejects_invalid_window(self) -> None:
        client = TestClient(create_app())

        response = client.post(
            "/portfolio/rolling-performance",
            json={
                "returns": [
                    0.10,
                    0.05,
                ],
                "window": 0,
            },
        )

        assert response.status_code == 422
        assert response.json()["detail"] == (
            "window must be greater than zero"
        )

    def test_rejects_window_larger_than_returns(self) -> None:
        client = TestClient(create_app())

        response = client.post(
            "/portfolio/rolling-performance",
            json={
                "returns": [
                    0.10,
                    0.05,
                ],
                "window": 3,
            },
        )

        assert response.status_code == 422
        assert response.json()["detail"] == (
            "window cannot be greater than the number of values"
        )
