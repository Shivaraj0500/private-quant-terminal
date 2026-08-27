import pytest
from fastapi.testclient import TestClient

from private_quant_terminal.api.app import create_app


class TestPortfolioRiskAdjustedApi:
    def test_returns_risk_adjusted_metrics(self) -> None:
        client = TestClient(create_app())

        response = client.post(
            "/portfolio/risk-adjusted",
            json={
                "returns": [
                    0.10,
                    -0.05,
                    0.15,
                    0.00,
                ],
                "risk_free_rate": 0.0,
                "target_return": 0.0,
                "max_drawdown": 0.10,
            },
        )

        assert response.status_code == 200

        data = response.json()

        assert data["sharpe_ratio"] == pytest.approx(
            0.6324555320,
        )
        assert data["sortino_ratio"] == pytest.approx(2.0)
        assert data["downside_deviation"] == pytest.approx(
            0.025,
        )
        assert data["calmar_ratio"] == pytest.approx(2.0)

    def test_returns_zero_metrics_for_empty_returns(
        self,
    ) -> None:
        client = TestClient(create_app())

        response = client.post(
            "/portfolio/risk-adjusted",
            json={},
        )

        assert response.status_code == 200

        assert response.json() == {
            "sharpe_ratio": 0.0,
            "sortino_ratio": 0.0,
            "downside_deviation": 0.0,
            "calmar_ratio": 0.0,
        }

    def test_uses_optional_risk_adjusted_parameters(
        self,
    ) -> None:
        client = TestClient(create_app())

        response = client.post(
            "/portfolio/risk-adjusted",
            json={
                "returns": [
                    0.10,
                    0.00,
                ],
                "risk_free_rate": 0.02,
                "target_return": 0.01,
                "max_drawdown": -0.05,
            },
        )

        assert response.status_code == 200

        data = response.json()

        assert data["sharpe_ratio"] > 0.0
        assert data["sortino_ratio"] > 0.0
        assert data["downside_deviation"] > 0.0
        assert data["calmar_ratio"] == pytest.approx(2.0)
