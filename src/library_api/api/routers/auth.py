"""Authentication related routes."""

from http import HTTPStatus

from fastapi import APIRouter, HTTPException

router = APIRouter(
    prefix="/auth",
    tags=["authentication"],
)


@router.get("/introspection")
async def authentication_introspection() -> None:
    """Return the JWT payload content."""
    raise HTTPException(
        status_code=HTTPStatus.UNAUTHORIZED, detail="No access token can be found in the Authorization header"
    )
