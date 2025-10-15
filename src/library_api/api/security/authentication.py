"""Authentication using OAuth2."""

import json
import logging
from datetime import timedelta
from typing import Annotated

import httpx
import jwt as pyjwt
import jwt.algorithms as pyjwt_algorithms
from cachetools import cached, TTLCache
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
from fastapi import Depends
from fastapi.security import OAuth2AuthorizationCodeBearer
from jwt import InvalidSignatureError

from library_api.api.caching import key_id_hashkey
from library_api.api.config import AuthenticationSettings, get_auth_settings, get_auth_client
from library_api.api.security import JWT

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl="https://fabien-sh.eu.auth0.com/authorize?audience=library-api",
    refreshUrl="https://fabien-sh.eu.auth0.com/authorize?audience=library-api",
    tokenUrl="https://fabien-sh.eu.auth0.com/oauth/token",
)


@cached(cache=TTLCache(maxsize=128, ttl=3600), key=key_id_hashkey)
def _get_json_web_key(httpx_client: httpx.Client, jwks_path: str, kid: str | None = None) -> RSAPublicKey | None:
    """Fetch the fedid public keys."""
    if not kid:
        return None

    try:
        response = httpx_client.get(url=jwks_path)
        response.raise_for_status()
    except httpx.HTTPStatusError as e:
        if e.response:
            logging.log(msg=e.response.text, level=logging.ERROR)
        raise
    jwks = response.json()

    for jwk in jwks["keys"]:
        if jwk["kid"] == kid:
            return pyjwt_algorithms.RSAAlgorithm.from_jwk(json.dumps(jwk))  # pyright: ignore [reportReturnType]

    return None


def authentication(
    raw_jwt: Annotated[str, Depends(oauth2_scheme)],
    auth_client: Annotated[httpx.Client, Depends(get_auth_client)],
    auth_settings: Annotated[AuthenticationSettings, Depends(get_auth_settings)],
) -> JWT:
    """Authenticate a request using a JWT token."""
    kid = pyjwt.get_unverified_header(raw_jwt)["kid"]
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
