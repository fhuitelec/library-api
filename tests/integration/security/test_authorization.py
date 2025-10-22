"""Integration tests for authentication."""

from fastapi.testclient import TestClient

from library_api.api.kernel import app
from library_api.api.security import Permission
from library_api.api.security.authorization import require_permissions
from tests.integration.conftest import craft_jwt, JWK


@app.get("/test/authz", dependencies=[require_permissions(required={Permission.BOOK_READ})])
async def authorization_introspection() -> None:
    """Return the JWT payload content."""
    ...


def test_valid_permissions(client: TestClient, jwk: JWK) -> None:
    """Test an unauthenticated request returns an HTTP/401."""
    jwt, raw_jwt = craft_jwt(jwk=jwk, permissions={Permission.BOOK_READ})
    response = client.get("/test/authz", headers={"Authorization": f"Bearer {raw_jwt}"})
    assert response.status_code == 200


def test_no_permission(client: TestClient, jwk: JWK) -> None:
    """Test an authenticated request with no permission returns an HTTP/403."""
    jwt, raw_jwt = craft_jwt(jwk=jwk, permissions=None)
    response = client.get("/test/authz", headers={"Authorization": f"Bearer {raw_jwt}"})
    assert response.status_code == 403

    body = response.json()
    assert isinstance(body, dict)
    detail = body.get("detail")
    assert isinstance(detail, dict)
    assert detail.get("reason") == "Insufficient permissions"
    assert detail.get("required") == [Permission.BOOK_READ]
    assert detail.get("granted") == []


def test_permission_mismatch(client: TestClient, jwk: JWK) -> None:
    """Test an authenticated request with granted permissions not matching required ones returns an HTTP/403."""
    granted = [Permission.BOOK_MANAGE, Permission.LOAN_APPROVE]
    jwt, raw_jwt = craft_jwt(jwk=jwk, permissions=set(granted))
    response = client.get("/test/authz", headers={"Authorization": f"Bearer {raw_jwt}"})
    assert response.status_code == 403

    body = response.json()
    assert isinstance(body, dict)
    detail = body.get("detail")
    assert isinstance(detail, dict)
    assert detail.get("reason") == "Insufficient permissions"
    assert detail.get("required") == [Permission.BOOK_READ]
    assert detail.get("granted") == granted
