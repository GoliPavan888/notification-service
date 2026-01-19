from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


def test_invalid_payload():
    response = client.post("/api/v1/notifications/publish", json={})
    assert response.status_code == 422


def test_valid_payload(monkeypatch):
    def mock_publish(*args, **kwargs):
        return {}

    monkeypatch.setattr("src.app.sns_client.publish", mock_publish)

    response = client.post(
        "/api/v1/notifications/publish",
        json={
            "recipientId": "user-1",
            "type": "email",
            "messageBody": "Hello",
        },
    )

    assert response.status_code == 202
