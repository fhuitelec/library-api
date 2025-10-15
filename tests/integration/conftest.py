"""Pytest configuration for integration tests."""

import uuid
from datetime import datetime, timezone, timedelta
from typing import Mapping, Tuple

import jwt as pyjwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey
from jwt.algorithms import RSAAlgorithm
from jwt.types import JWKDict
from pydantic import ConfigDict, BaseModel
from pytest_httpx import HTTPXMock
from starlette.testclient import TestClient

from library_api.api.kernel import app
from library_api.api.security import Permission, JWT


@pytest.fixture(name="jwk_kid", scope="package")
def jwk_kid() -> str:
    """Generate a random key ID for a Json Web Key."""
    return str(uuid.uuid4())


class JWK(BaseModel):
    """A Json Web Key."""

    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    key_id: str
    public_key: JWKDict
    private_key: RSAPrivateKey

    @property
    def to_jwk(self) -> Mapping[str, list[Mapping[str, str]]]:
        """Get the public key as a JSON Web Key dictionary."""
        return {
            "keys": [
                {
                    "kid": self.key_id,
                    **self.public_key,
                }
            ]
        }


@pytest.fixture(scope="package")
def jwk(jwk_kid: str) -> JWK:
    """Generate a Json Web Key."""
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = RSAAlgorithm.to_jwk(private_key.public_key(), as_dict=True)

    return JWK(key_id=jwk_kid, public_key=public_key, private_key=private_key)


def craft_jwt(
    jwk: JWK,
    issued_at: datetime | None = None,
    expired_at: datetime | None = None,
    permissions: set[Permission] | None = None,
) -> Tuple[JWT, str]:
    """Craft a tailor-made Json Web Token signed with an authorized JWK."""
    if issued_at is None:
        issued_at = datetime.now(tz=timezone.utc)

    if expired_at is None:
        expired_at = issued_at + timedelta(hours=1)

    if permissions is None:
        permissions = set()

    jwt = JWT(
        issuer="https://fabien-sh.eu.auth0.com/",
        subjet="auth0|e653d123e9687d9c90d11d92",
        audience="library-api",
        issued_at=issued_at,
        expires_at=expired_at,
        authorized_party="SL49RJ9JLIIGyKS139tyGbWPAZpwrw",
        permissions=permissions or set(),
    )

    return jwt, pyjwt.encode(
        headers={"kid": jwk.key_id},
        payload={
            "iss": jwt.issuer,
            "sub": jwt.subjet,
            "aud": jwt.audience,
            "iat": int(jwt.issued_at.timestamp()),
            "exp": int(jwt.expires_at.timestamp()),
            "azp": jwt.authorized_party,
            "permissions": [permission.value for permission in jwt.permissions],
        },
        algorithm="RS256",
        key=jwk.private_key,
    )


@pytest.fixture(name="auth_client", scope="function")
def auth_client(httpx_mock: HTTPXMock, jwk: JWK) -> HTTPXMock:
    """Mock the Auth0 client to return the JWK."""
    httpx_mock.add_response(
        url="https://fabien-sh.eu.auth0.com/.well-known/jwks.json",
        status_code=200,
        json=jwk.to_jwk,
        is_optional=True,
    )
    return httpx_mock


@pytest.fixture(name="_cached_test_client", scope="package")
def _cached_test_client() -> TestClient:
    """Create a bare TestClient on a "package" scope for tests performances."""
    return TestClient(app)


@pytest.fixture(name="client", scope="function")
def client(_cached_test_client: TestClient, auth_client: HTTPXMock) -> TestClient:
    """Create a TestClient with mocked authentication HTTP calls."""
    return _cached_test_client
