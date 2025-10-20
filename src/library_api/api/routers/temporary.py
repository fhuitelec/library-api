"""Authentication related routes."""

from typing import Union

from fastapi import APIRouter

from library_api.api.security import Permission
from library_api.api.security.authorization import require_permissions

router = APIRouter(
    prefix="/tmp",
    tags=["temporary"],
)


@router.get("/")
@router.get(
    "/",
    dependencies=[require_permissions(required={Permission.BOOK_READ, Permission.LOAN_APPROVE})],
)
async def read_root() -> dict[str, str]:
    """Return a greeting message."""
    return {
        "Hello": "World",
    }


@router.get("/items/{item_id}")
async def read_item(item_id: int, q: Union[str, None] = None) -> dict[str, Union[str, int, None]]:
    """Read items."""
    return {"item_id": item_id, "q": q}
