"""Authentication using OAuth2."""

from typing import Annotated
import jwt as pyjwt

from fastapi import Depends

from library_api.api.config import oauth
from library_api.api.security import JWT


def authentication(raw_jwt: Annotated[str, Depends(oauth())]) -> JWT:
    """Return the JWT payload content."""
    jwt = pyjwt.decode(
        jwt=raw_jwt,
        verify=False,
        audience="library-api",
        algorithms=["HS256"],
        options={"verify_signature": False},
    )

    return JWT(**jwt)
