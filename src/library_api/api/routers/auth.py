"""Authentication related routes."""

from typing import Annotated

from fastapi import APIRouter, Depends

from library_api.api.security import JWT
from library_api.api.security.authentication import authentication

router = APIRouter(
    prefix="/auth",
    tags=["authentication"],
)

######
# 1. #
######

# @router.get("/introspection")
# async def authentication_introspection(jwt: Annotated[str, Depends(oauth())]) -> str:
#     """Return the JWT payload content."""
#     return jwt


######
# 2. #
######

# @router.get("/introspection")
# async def authentication_introspection(raw_jwt: Annotated[str, Depends(oauth())]) -> dict:
#     """Return the JWT payload content."""
#     import jwt as pyjwt
#
#     jwt = pyjwt.decode(
#         jwt=raw_jwt,
#         verify=False,
#         audience="library-api",
#         algorithms=["HS256"],
#         options={"verify_signature": False},
#     )
#
#     return jwt

######
# 3. #
######


@router.get("/introspection")
async def authentication_introspection(jwt: Annotated[JWT, Depends(authentication)]) -> JWT:
    """Return the JWT payload content."""
    return jwt
