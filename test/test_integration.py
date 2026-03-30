def test_full_workflow(client):
    # register
    client.post("/auth/register", json={
        "username": "integration",
        "password": "1234"
    })

    # login
    client.post("/auth/login", json={
        "username": "integration",
        "password": "1234"
    })

    # add task
    response = client.post("/tasks", json={
        "text": "Test task"
    })
    assert response.status_code == 201

    # get tasks
    response = client.get("/tasks")
    assert response.status_code == 200
    assert len(response.json) > 0
