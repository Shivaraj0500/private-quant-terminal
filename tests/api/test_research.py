from datetime import UTC, datetime

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

    response = client.get(
        f"/research/runs/{run_id}",
    )

    assert response.status_code == 200

    data = response.json()

    assert data["run"]["run_id"] == run_id
    assert data["run"]["status"] == "COMPLETED"

    assert "execution" in data
    assert "performance" in data

    assert data["execution"]["run_id"] == run_id
    assert isinstance(data["execution"]["events"], list)
    assert isinstance(data["execution"]["trades"], list)
    assert isinstance(data["execution"]["equity_curve"], list)

    assert data["execution"]["final_equity"] == 100000.0
    assert isinstance(data["performance"]["returns"], list)


def test_get_unknown_research_run_returns_404() -> None:
    client = make_client()

    response = client.get(
        "/research/runs/does-not-exist",
    )

    assert response.status_code == 404
