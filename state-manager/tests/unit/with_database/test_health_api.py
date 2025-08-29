from app.main import health

def test_health_api():
    """Test the health API endpoint function."""
    response = health()
    assert response == {"message": "OK"}