from fastapi.testclient import TestClient

from private_quant_terminal.api.app import app


def test_generate_buy_signal() -> None:
    client = TestClient(app)

    response = client.post(
        "/technical-analysis/signal",
        json={
            "trend_score": 1,
            "momentum_score": 1,
            "volume_score": 0,
            "volatility_score": -1,
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "trend_score": 1,
        "momentum_score": 1,
        "volume_score": 0,
        "volatility_score": -1,
        "overall_score": 1,
        "signal": "BUY",
    }


def test_generate_sell_signal() -> None:
    client = TestClient(app)

    response = client.post(
        "/technical-analysis/signal",
        json={
            "trend_score": -1,
            "momentum_score": -1,
            "volume_score": 0,
            "volatility_score": 0,
        },
    )

    assert response.status_code == 200
    assert response.json()["overall_score"] == -2
    assert response.json()["signal"] == "SELL"


def test_generate_neutral_signal() -> None:
    client = TestClient(app)

    response = client.post(
        "/technical-analysis/signal",
        json={
            "trend_score": 1,
            "momentum_score": -1,
            "volume_score": 0,
            "volatility_score": 0,
        },
    )

    assert response.status_code == 200
    assert response.json()["overall_score"] == 0
    assert response.json()["signal"] == "NEUTRAL"


def test_rejects_missing_component_score() -> None:
    client = TestClient(app)

    response = client.post(
        "/technical-analysis/signal",
        json={
            "trend_score": 1,
            "momentum_score": 1,
            "volume_score": 0,
        },
    )

    assert response.status_code == 422