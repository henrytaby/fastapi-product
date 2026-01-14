from fastapi.testclient import TestClient


def test_create_task(client: TestClient, superuser_token_headers: dict[str, str]):
    response = client.post(
        "/api/tasks/",
        json={
            "title": "Test Task",
            "description": "This is a test task",
            "completed": False,
        },
        headers=superuser_token_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Task"
    assert "id" in data


def test_read_tasks(client: TestClient, superuser_token_headers: dict[str, str]):
    # Create a task first
    client.post(
        "/api/tasks/",
        json={
            "title": "Task 1",
            "description": "Task 1 description",
            "completed": False,
        },
        headers=superuser_token_headers,
    )
    client.post(
        "/api/tasks/",
        json={
            "title": "Task 2",
            "description": "Task 2 description",
            "completed": True,
        },
        headers=superuser_token_headers,
    )

    response = client.get("/api/tasks/", headers=superuser_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2


def test_read_task(client: TestClient, superuser_token_headers: dict[str, str]):
    response = client.post(
        "/api/tasks/",
        json={"title": "Test Task", "description": "Desc", "completed": False},
        headers=superuser_token_headers,
    )
    task_id = response.json()["id"]

    response = client.get(f"/api/tasks/{task_id}", headers=superuser_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Task"
    assert data["id"] == task_id


def test_read_task_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
):
    response = client.get("/api/tasks/999999", headers=superuser_token_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"
