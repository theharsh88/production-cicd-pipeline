from fastapi.testclient import TestClient


def create_task(client: TestClient) -> dict[str, object]:
    response = client.post(
        "/api/tasks",
        json={
            "title": "Build pipeline",
            "description": "Use immutable images",
            "priority": 1,
        },
    )
    assert response.status_code == 201
    return response.json()


def test_create_and_list_tasks(client: TestClient) -> None:
    created = create_task(client)
    assert created["title"] == "Build pipeline"
    assert created["completed"] is False
    listed = client.get("/api/tasks")
    assert listed.status_code == 200
    assert len(listed.json()) == 1


def test_read_update_and_delete_task(client: TestClient) -> None:
    created = create_task(client)
    task_id = created["id"]
    assert client.get(f"/api/tasks/{task_id}").json()["id"] == task_id
    updated = client.put(
        f"/api/tasks/{task_id}", json={"completed": True, "priority": 2}
    )
    assert updated.status_code == 200
    assert updated.json()["completed"] is True
    assert updated.json()["priority"] == 2
    assert client.delete(f"/api/tasks/{task_id}").status_code == 204
    assert client.get(f"/api/tasks/{task_id}").status_code == 404


def test_validation_failure(client: TestClient) -> None:
    response = client.post("/api/tasks", json={"title": "", "priority": 99})
    assert response.status_code == 422


def test_unknown_task_is_not_found(client: TestClient) -> None:
    response = client.get("/api/tasks/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"
