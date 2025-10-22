"""Authentication using OAuth2."""

import json
from datetime import timedelta
from typing import Annotated

import httpx
import jwt as pyjwt
import jwt.algorithms as pyjwt_algorithms
from cachetools import cached, TTLCache
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
from fastapi import Depends
from jwt import InvalidSignatureError

from library_api.api.caching import key_id_hashkey
from library_api.api.config import AuthenticationSettings, get_auth_settings, get_auth_client, oauth
from library_api.api.security import JWT


@cached(cache=TTLCache(maxsize=128, ttl=3600), key=key_id_hashkey)
def _get_json_web_key(httpx_client: httpx.Client, jwks_path: str, kid: str) -> RSAPublicKey:
    """Fetch the JWK."""
    response = httpx_client.get(url=jwks_path)
    response.raise_for_status()

    jwks = response.json()

    for jwk in jwks["keys"]:
        if jwk["kid"] == kid:
            return pyjwt_algorithms.RSAAlgorithm.from_jwk(json.dumps(jwk))  # pyright: ignore [reportReturnType]

    raise InvalidSignatureError(f"No public key found for the given kid '{kid}'")


def authentication(
    raw_jwt: Annotated[str, Depends(oauth())],
    auth_client: Annotated[httpx.Client, Depends(get_auth_client)],
    auth_settings: Annotated[AuthenticationSettings, Depends(get_auth_settings)],
) -> JWT:
    """Return the JWT payload content."""
    kid = pyjwt.get_unverified_header(raw_jwt).get("kid")
    if kid is None:
        msg = "No 'kid' found in the JWT header"
        raise InvalidSignatureError(msg)

    public_key = _get_json_web_key(auth_client, auth_settings.jwks_path, kid)

    if public_key is None:
        msg = f"No public key found for the given kid '{kid}'."
        raise InvalidSignatureError(msg)

    jwt = pyjwt.decode(
        jwt=raw_jwt,
        key=public_key,
        audience="library-api",
        algorithms=["RS256"],
        leeway=timedelta(seconds=10),
    )

    return JWT(**jwt)
