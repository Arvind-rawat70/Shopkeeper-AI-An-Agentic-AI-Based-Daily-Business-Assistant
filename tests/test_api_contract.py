from fastapi.testclient import TestClient

from ml import api as ml_api


def test_predict_demand_uses_predicted_demand_field(monkeypatch):
    monkeypatch.setattr(ml_api, "predict_item_demand", lambda *args, **kwargs: 59.21)
    monkeypatch.setattr(ml_api, "write_api_log", lambda *args, **kwargs: None)

    client = TestClient(ml_api.app)
    response = client.post(
        "/predict-demand",
        json={
            "item_id": "HOBBIES_1_001",
            "target_week": "2026-09-21",
            "current_sell_price": 99.5,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["predicted_demand"] == 59.21
    assert "predicted_demand_accuracy" not in payload


def test_reorder_recommendation_uses_predicted_demand_field(monkeypatch):
    monkeypatch.setattr(ml_api, "predict_item_demand", lambda *args, **kwargs: 59.21)
    monkeypatch.setattr(ml_api, "write_api_log", lambda *args, **kwargs: None)

    client = TestClient(ml_api.app)
    response = client.post(
        "/reorder-recommendation",
        json={
            "item_id": "HOBBIES_1_001",
            "target_week": "2026-09-21",
            "current_sell_price": 99.5,
            "safe_stock": 10,
            "current_stock": 5,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["predicted_demand"] == 59.21
    assert "predicted_demand_accuracy" not in payload
