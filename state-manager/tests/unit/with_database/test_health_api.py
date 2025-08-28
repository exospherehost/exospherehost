from fastapi.testclient import TestClient

class TestHealthAPI:
    """Test the health API."""

    def test_health_api(self, app_fixture):
        """Test the health API."""
        client = TestClient(app_fixture)
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"message": "OK"}