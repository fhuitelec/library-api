"""Authentication related routes."""

from typing import Annotated, Union

from fastapi import APIRouter, Depends

from library_api.api.security import JWT, Permission
from library_api.api.security.authentication import authentication
from library_api.api.security.authorization import requires_permissions, PermissionMatcher

router = APIRouter(
    prefix="/tmp",
    tags=["temporary"],
)


@router.get("/")
@requires_permissions({Permission.BOOK_READ, Permission.LOAN_APPROVE}, matcher=PermissionMatcher.ANY)
async def read_root(jwt: Annotated[JWT, Depends(authentication)]) -> dict[str, str]:
    """Return a greeting message."""
    return {
        "Hello": "World",
    }


@router.get("/items/{item_id}")
async def read_item(item_id: int, q: Union[str, None] = None) -> dict[str, Union[str, int, None]]:
    """Read items."""
    return {"item_id": item_id, "q": q}
