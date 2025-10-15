"""Integration tests for authentication."""

import pytest
from fastapi.testclient import TestClient

from tests.integration.conftest import craft_jwt, JWK


def test_no_authorization_header(client: TestClient) -> None:
    """Test an unauthenticated request returns an HTTP/401."""
    response = client.get("/")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


@pytest.mark.parametrize(
    "jwt",
    [
        "malformed_jwt_token",
        "malformed.jwt.token",
    ],
)
def test_malformed_jwt(client: TestClient, jwk: JWK, jwt: str) -> None:
    """Test an unauthenticated request returns an HTTP/401."""
    response = client.get("/auth/introspection", headers={"Authorization": "Bearer malformed.jwt.token"})
    assert response.status_code == 401


def test_valid_jwt(client: TestClient, jwk: JWK) -> None:
    """Test an unauthenticated request returns an HTTP/401."""
    jwt, raw_jwt = craft_jwt(jwk=jwk)
    response = client.get("/auth/introspection", headers={"Authorization": f"Bearer {raw_jwt}"})
    assert response.status_code == 200

    body = response.json()
    assert body["issuer"] == jwt.issuer
    assert body["audience"] == jwt.audience
    assert body["subjet"] == jwt.subjet
    assert body["issued_at"] == jwt.issued_at.strftime("%Y-%m-%dT%H:%M:%SZ")
    assert body["expires_at"] == jwt.expires_at.strftime("%Y-%m-%dT%H:%M:%SZ")
    assert body["authorized_party"] == jwt.authorized_party
    assert body["permissions"] == list(jwt.permissions)
