from fastapi.testclient import TestClient


def test_failure_demo_is_safe_by_default(client: TestClient) -> None:
    response = client.get("/api/demo/failure")
    assert response.status_code == 200
    assert response.json()["status"] == "disabled"
