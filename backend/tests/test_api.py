from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_demo_generation_consumes_roll() -> None:
    roll = client.post("/api/v1/roll").json()
    payload = {"prompt": "Объясни, что такое фикстура pytest", "roll_id": roll["roll_id"], "demo": True}

    response = client.post("/api/v1/generate", json=payload)
    repeated = client.post("/api/v1/generate", json=payload)

    assert response.status_code == 200
    assert response.json()["rolls"] == roll["rolls"]
    assert repeated.status_code == 410

