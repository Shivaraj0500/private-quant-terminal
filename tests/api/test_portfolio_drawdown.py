from fastapi.testclient import TestClient

from private_quant_terminal.api.app import create_app


class TestPortfolioDrawdownApi:
    def test_returns_drawdown_metrics(self) -> None:
        client = TestClient(create_app())

        response = client.post(
            "/portfolio/drawdown",
            json={
                "peak_value": 100000.0,
                "current_value": 85000.0,
            },
        )

        assert response.status_code == 200
        assert response.json() == {
            "peak_value": 100000.0,
            "current_value": 85000.0,
            "drawdown": 15000.0,
            "drawdown_percent": 15.0,
        }

    def test_returns_zero_drawdown_at_peak(self) -> None:
        client = TestClient(create_app())

        response = client.post(
            "/portfolio/drawdown",
            json={
                "peak_value": 100000.0,
                "current_value": 100000.0,
            },
        )

        assert response.status_code == 200

        data = response.json()

        assert data["drawdown"] == 0.0
        assert data["drawdown_percent"] == 0.0

    def test_returns_validation_error_for_zero_peak_value(self) -> None:
        client = TestClient(create_app())

        response = client.post(
            "/portfolio/drawdown",
            json={
                "peak_value": 0.0,
                "current_value": 1000.0,
            },
        )

        assert response.status_code == 422
        assert response.json()["detail"] == (
            "peak_value must be greater than zero"
        )

    def test_returns_validation_error_for_negative_peak_value(
        self,
    ) -> None:
        client = TestClient(create_app())

        response = client.post(
            "/portfolio/drawdown",
            json={
                "peak_value": -100000.0,
                "current_value": 85000.0,
            },
        )

        assert response.status_code == 422
        assert response.json()["detail"] == (
            "peak_value must be greater than zero"
        )
