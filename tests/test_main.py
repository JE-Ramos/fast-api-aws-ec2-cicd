from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()
    assert response.json()["message"] == "Welcome to FastAPI AWS App with PR Checks"


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_get_items():
    response = client.get("/api/v1/items")
    assert response.status_code == 200
    assert "items" in response.json()
    assert len(response.json()["items"]) == 2


def test_get_item():
    response = client.get("/api/v1/items/1")
    assert response.status_code == 200
    assert response.json() == {"id": 1, "name": "Item 1"}


def test_get_item_not_found():
    response = client.get("/api/v1/items/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Item not found"}


def test_create_item():
    new_item = {"id": 3, "name": "New Item"}
    response = client.post("/api/v1/items", json=new_item)
    assert response.status_code == 200
    assert response.json()["item"] == new_item