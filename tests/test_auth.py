"""Test module for the main logic."""

from fastapi.testclient import TestClient

from library_api.api.kernel import app

client = TestClient(app)


def test_auth_introspection() -> None:
    """Test the /auth/introspection endpoint."""
    response = client.get("/auth/introspection")
    assert response.status_code == 401
    assert response.json() == {"detail": "No access token can be found in the Authorization header"}
