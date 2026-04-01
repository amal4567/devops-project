def test_full_workflow(client):
    client.post("/auth/register", json={
        "username": "integration",
        "password": "1234"
    })

    client.post("/auth/login", json={
        "username": "integration",
        "password": "1234"
    })

    response = client.post("/tasks", json={
        "text": "Test task"
    })
    assert response.status_code == 201

    response = client.get("/tasks")
    assert response.status_code == 200
    assert len(response.json) > 0
