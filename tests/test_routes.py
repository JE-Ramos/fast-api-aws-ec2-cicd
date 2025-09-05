import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestItemRoutes:
    def test_get_items_returns_list(self):
        response = client.get("/api/v1/items")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert isinstance(data["items"], list)
        assert len(data["items"]) == 3
        
    def test_get_items_structure(self):
        response = client.get("/api/v1/items")
        items = response.json()["items"]
        for item in items:
            assert "id" in item
            assert "name" in item
            assert isinstance(item["id"], int)
            assert isinstance(item["name"], str)
    
    def test_get_single_item_success(self):
        response = client.get("/api/v1/items/5")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 5
        assert data["name"] == "Item 5"
    
    def test_get_single_item_not_found(self):
        response = client.get("/api/v1/items/101")
        assert response.status_code == 404
        assert response.json()["detail"] == "Item not found"
    
    def test_get_item_boundary_values(self):
        response = client.get("/api/v1/items/100")
        assert response.status_code == 200
        
        response = client.get("/api/v1/items/0")
        assert response.status_code == 200
        
        response = client.get("/api/v1/items/-1")
        assert response.status_code == 200
    
    def test_create_item_success(self):
        new_item = {"id": 10, "name": "Test Item", "description": "A test item"}
        response = client.post("/api/v1/items", json=new_item)
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["message"] == "Item created"
        assert "item" in data
        assert data["item"] == new_item
    
    def test_create_item_empty_payload(self):
        response = client.post("/api/v1/items", json={})
        assert response.status_code == 200
        data = response.json()
        assert data["item"] == {}
    
    def test_create_item_complex_payload(self):
        complex_item = {
            "id": 20,
            "name": "Complex Item",
            "nested": {
                "field1": "value1",
                "field2": [1, 2, 3]
            },
            "tags": ["tag1", "tag2"]
        }
        response = client.post("/api/v1/items", json=complex_item)
        assert response.status_code == 200
        assert response.json()["item"] == complex_item