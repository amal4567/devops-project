import pytest
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_home_page(client):
    response = client.get("/")
    assert response.status_code == 200


def test_register_user(client):
    response = client.post("/auth/register", json={
        "username": "testuser",
        "password": "1234"
    })
    assert response.status_code == 201


def test_login_user(client):
    client.post("/auth/register", json={
        "username": "user1",
        "password": "1234"
    })

    response = client.post("/auth/login", json={
        "username": "user1",
        "password": "1234"
    })
    assert response.status_code == 200
