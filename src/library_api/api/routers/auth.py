"""Authentication related routes."""

from typing import Annotated

from fastapi import APIRouter, Depends

from library_api.api.security import JWT
from library_api.api.security.authentication import authentication

router = APIRouter(
    prefix="/auth",
    tags=["authentication"],
)


@router.get("/introspection")
async def authentication_introspection(jwt: Annotated[JWT, Depends(authentication)]) -> JWT:
    """Return the JWT payload content."""
    return jwt
