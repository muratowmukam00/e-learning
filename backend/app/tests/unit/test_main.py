# app/tests/integration/test_main.py
def test_root_endpoint(client):
    """Test the root '/' endpoint"""
    response = client.get("/")
    assert response.status_code == 200

    data = response.json()
    assert data["message"] == "Welcome to Entrepreneurship Learning Platform API"
    assert data["version"] == "1.0.0"
    assert data["docs"] == "/docs"
    assert data["redoc"] == "/redoc"


def test_health_check(client):
    """Test the '/health' endpoint"""
    response = client.get("/health")
    assert response.status_code == 200

    data = response.json()
    assert data == {"status": "healthy"}
