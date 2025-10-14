"""Authentication using OAuth2."""

import json
import logging
from datetime import timedelta
from typing import Annotated, Any, Mapping

import httpx
import jwt as pyjwt
import jwt.algorithms as pyjwt_algorithms
from cachetools import cached, TTLCache
from cachetools.keys import hashkey
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
from fastapi import Depends
from fastapi.security import OAuth2AuthorizationCodeBearer
from jwt import InvalidSignatureError

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl="https://fabien-sh.eu.auth0.com/authorize?audience=library-api",
    refreshUrl="https://fabien-sh.eu.auth0.com/authorize?audience=library-api",
    tokenUrl="https://fabien-sh.eu.auth0.com/oauth/token",
)


def ignore_args_hashkey(*args, **kwargs: Any) -> tuple:  # pylint: disable=unused-argument # noqa: ANN002,ANN401
    """Hit the cache even if the function arguments are different."""
    return hashkey("_")


@cached(cache=TTLCache(maxsize=128, ttl=3600), key=ignore_args_hashkey)
def _get_json_web_key(httpx_client: httpx.Client, kid: str | None = None) -> RSAPublicKey | None:
    """Fetch the fedid public keys."""
    if not kid:
        return None

    url = "https://fabien-sh.eu.auth0.com/.well-known/jwks.json"
    try:
        response = httpx_client.get(
            url=url,
            timeout=5,
        )
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


def authentication(jwt: Annotated[str, Depends(oauth2_scheme)]) -> Mapping[str, Any]:
    """Authenticate a request using a JWT token."""
    kid = pyjwt.get_unverified_header(jwt)["kid"]
    public_key = _get_json_web_key(httpx.Client(), kid)

    if public_key is None:
        msg = f"No public key found for the given kid '{kid}'."
        raise InvalidSignatureError(msg)

    # Todo: handle errors here (expired token, invalid signature, etc.)
    jwt_data = pyjwt.decode(
        jwt=jwt,
        key=public_key,
        audience="library-api",
        algorithms=["RS256"],
        leeway=timedelta(seconds=10),
    )

    return jwt_data  # pyright: ignore [reportReturnType]
