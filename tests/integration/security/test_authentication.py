"""Integration tests for authentication."""

from typing import Annotated

import pytest
from fastapi import Depends
from fastapi.testclient import TestClient

from library_api.api.kernel import app
from library_api.api.security import Permission, JWT
from library_api.api.security.authentication import authentication
from tests.integration.conftest import craft_jwt, JWK


@app.get("/test/authn")
async def authentication_introspection(jwt: Annotated[JWT, Depends(authentication)]) -> JWT:
    """Return the JWT payload content."""
    return jwt


def test_no_authorization_header(client: TestClient) -> None:
    """Test an unauthenticated request returns an HTTP/401."""
    response = client.get("/test/authn")
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
    response = client.get("/test/authn", headers={"Authorization": "Bearer malformed.jwt.token"})
    assert response.status_code == 401


def test_valid_jwt(client: TestClient, jwk: JWK) -> None:
    """Test an unauthenticated request returns an HTTP/401."""
    jwt, raw_jwt = craft_jwt(jwk=jwk, permissions={Permission.BOOK_READ})
    response = client.get("/test/authn", headers={"Authorization": f"Bearer {raw_jwt}"})
    assert response.status_code == 200

    body = response.json()
    assert body["issuer"] == jwt.issuer
    assert body["audience"] == jwt.audience
    assert body["subject"] == jwt.subject
    assert body["issued_at"] == jwt.issued_at.strftime("%Y-%m-%dT%H:%M:%SZ")
    assert body["expires_at"] == jwt.expires_at.strftime("%Y-%m-%dT%H:%M:%SZ")
    assert body["authorized_party"] == jwt.authorized_party
    assert body["permissions"] == [Permission.BOOK_READ]
