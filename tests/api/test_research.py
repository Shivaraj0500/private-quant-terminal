
from fastapi.testclient import TestClient

from private_quant_terminal.api.app import create_app


def make_client() -> TestClient:
    return TestClient(create_app())


def make_payload() -> dict:
    return {
        "strategy_id": "frontend-live-test",
        "strategy_version": 1,
        "symbol": "RELIANCE",
        "timeframe": "5m",
        "initial_equity": 100000.0,
        "parameters": {},
    }


def test_list_research_runs_returns_history() -> None:
    client = make_client()

    create_response = client.post(
        "/research/runs",
        json=make_payload(),
    )

    assert create_response.status_code == 200

    response = client.get("/research/runs")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert data

    run_ids = {item["run_id"] for item in data}

    assert create_response.json()["run"]["run_id"] in run_ids


def test_get_research_run_returns_complete_persisted_evidence() -> None:
    client = make_client()

    create_response = client.post(
        "/research/runs",
        json=make_payload(),
    )

    assert create_response.status_code == 200

    created = create_response.json()
    run_id = created["run"]["run_id"]

    assert "integrity" in created
    assert created["integrity"]["status"] == "WARN"
    assert created["integrity"]["passed"] is False
    assert created["integrity"]["warnings"] == 1
    assert created["integrity"]["failures"] == 0
    assert created["integrity"]["findings"]
    assert created["integrity"]["findings"][0]["code"] == "OPEN_POSITION"

    response = client.get(
        f"/research/runs/{run_id}",
    )

    assert response.status_code == 200

    data = response.json()

    assert data["run"]["run_id"] == run_id
    assert data["run"]["status"] == "COMPLETED"

    assert "execution" in data
    assert "performance" in data
    assert "intelligence" in data
    assert "integrity" in data

    assert data["intelligence"]["evidence"]
    intelligence_references = {
        (item["category"], item["code"])
        for item in data["intelligence"]["evidence"]
    }

    assert ("INTEGRITY", "INTEGRITY_OK") not in intelligence_references
    assert ("EXECUTION", "OPEN_POSITION") in intelligence_references
    assert ("INTEGRITY", "OPEN_POSITION") in intelligence_references

    assert data["integrity"]["status"] == "WARN"
    assert data["integrity"]["passed"] is False
    assert data["integrity"]["warnings"] == 1
    assert data["integrity"]["failures"] == 0
    assert data["integrity"]["findings"]
    assert data["integrity"]["findings"][0]["code"] == "OPEN_POSITION"

    assert data["execution"]["run_id"] == run_id
    assert isinstance(data["execution"]["events"], list)
    assert isinstance(data["execution"]["trades"], list)
    assert isinstance(data["execution"]["equity_curve"], list)

    assert data["execution"]["final_equity"] == 100000.0
    assert isinstance(data["performance"]["returns"], list)

    assert "risk_diagnostics" in data["performance"]
    assert data["performance"]["risk_diagnostics"]["observation_count"] == 0
    assert "risk_findings" in data["performance"]
    assert data["performance"]["risk_findings"]
    assert data["performance"]["risk_findings"][0]["category"] == "data_availability"

    assert "option_diagnostics" in data["performance"]
    option_diagnostics = data["performance"]["option_diagnostics"]

    assert option_diagnostics["option_fill_count"] == 0
    assert option_diagnostics["option_trade_count"] == 0
    assert option_diagnostics["call_trade_count"] == 0
    assert option_diagnostics["put_trade_count"] == 0
    assert option_diagnostics["winning_option_trade_count"] == 0
    assert option_diagnostics["losing_option_trade_count"] == 0
    assert option_diagnostics["option_net_pnl"] == 0.0
    assert option_diagnostics["average_option_trade"] == 0.0
    assert option_diagnostics["expiry_day_trade_count"] == 0
    assert option_diagnostics["expiry_day_net_pnl"] == 0.0
    assert option_diagnostics["pre_expiry_trade_count"] == 0
    assert option_diagnostics["pre_expiry_net_pnl"] == 0.0
    assert option_diagnostics["strike_distribution"] == []
    assert option_diagnostics["expiry_distribution"] == []
    assert option_diagnostics["trades"] == []


def test_get_unknown_research_run_returns_404() -> None:
    client = make_client()

    response = client.get(
        "/research/runs/does-not-exist",
    )

    assert response.status_code == 404
