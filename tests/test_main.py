"""Test module for the main logic."""

from fastapi.testclient import TestClient

from library_api.main import app

client = TestClient(app)


def test_read_main() -> None:
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}
