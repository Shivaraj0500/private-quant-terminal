from fastapi.testclient import TestClient

from private_quant_terminal.api.app import create_app


class TestPortfolioSummaryApi:
    def test_returns_empty_portfolio_summary(self) -> None:
        client = TestClient(create_app())

        response = client.post(
            "/portfolio/summary",
            json={
                "prices": {},
            },
        )

        assert response.status_code == 200

        data = response.json()

        assert data["realized_pnl"] == 0.0
        assert data["unrealized_pnl"] == 0.0
        assert data["total_pnl"] == 0.0
        assert data["open_position_count"] == 0
        assert data["closed_trade_count"] == 0

        assert data["gross_exposure"] == 0.0
        assert data["net_exposure"] == 0.0
        assert data["long_exposure"] == 0.0
        assert data["short_exposure"] == 0.0
        assert data["largest_position_weight"] == 0.0

        assert data["winning_trades"] == 0
        assert data["losing_trades"] == 0
        assert data["win_rate"] == 0.0
        assert data["average_win"] == 0.0
        assert data["average_loss"] == 0.0
        assert data["profit_factor"] == 0.0
