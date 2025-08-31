import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestAPIIntegration:
    def test_full_api_flow(self):
        response = client.get("/")
        assert response.status_code == 200
        
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
        
        response = client.get("/api/v1/items")
        assert response.status_code == 200
        items = response.json()["items"]
        
        if items:
            first_item_id = items[0]["id"]
            response = client.get(f"/api/v1/items/{first_item_id}")
            assert response.status_code == 200
        
        new_item = {"id": 999, "name": "Integration Test Item"}
        response = client.post("/api/v1/items", json=new_item)
        assert response.status_code == 200
        assert response.json()["item"] == new_item
    
    @pytest.mark.integration
    def test_api_error_handling(self):
        response = client.get("/nonexistent-endpoint")
        assert response.status_code == 404
        
        response = client.get("/api/v1/items/999999")
        assert response.status_code == 404
        
        response = client.post("/api/v1/items", data="invalid json")
        assert response.status_code == 422
    
    @pytest.mark.integration
    def test_cors_headers(self):
        response = client.options(
            "/api/v1/items",
            headers={
                "Origin": "http://example.com",
                "Access-Control-Request-Method": "GET"
            }
        )
        assert "access-control-allow-origin" in response.headers
        assert response.headers["access-control-allow-origin"] == "*"
    
    def test_api_versioning(self):
        response = client.get("/api/v1/items")
        assert response.status_code == 200
        
        response = client.get("/api/v2/items")
        assert response.status_code == 404