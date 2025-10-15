"""Router for book-related operations."""

from typing import Annotated

from fastapi import APIRouter, Depends

from library_api.api.security import JWT
from library_api.api.security.authentication import authentication

router = APIRouter(
    prefix="/books",
    tags=["books"],
)


@router.get("/{book_id}")
async def authentication_introspection(book_id: str, jwt: Annotated[JWT, Depends(authentication)]) -> JWT:
    """Return the JWT payload content."""
    return jwt
