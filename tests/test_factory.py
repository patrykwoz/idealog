from idealog import create_app

def test_config():
    """Test create_app without passing test config."""
    assert not create_app().testing
    assert create_app({"TESTING": True}).testing

def test_hello(client):
    response = client.get("/docs")
    assert response.status_code == 200
    assert b"docs" in response.data