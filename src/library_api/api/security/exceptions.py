"""Exceptions for the security package."""

from http import HTTPStatus

from jwt import PyJWTError
from pydantic import BaseModel, Field
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import Response, JSONResponse


class AuthenticationError(BaseModel):
    """Error during the authentication process."""

    detail: str | None = Field(examples=["Cannot decode JWT"], description="Details about the authentication issue")


async def jwt_exception_handler(_: Request, exc: PyJWTError) -> Response:
    """Handle JWT-related exceptions."""
    return JSONResponse(AuthenticationError(detail=str(exc)).model_dump(), status_code=HTTPStatus.UNAUTHORIZED)


async def unauthorized_exception_handler(_: Request, exc: HTTPException) -> Response:
    """Handle FastAPI native authentication exceptions."""
    if exc.status_code == HTTPStatus.UNAUTHORIZED:
        return JSONResponse(AuthenticationError(detail=exc.detail).model_dump(), status_code=HTTPStatus.UNAUTHORIZED)

    raise RuntimeError(f"Unhandled exception: {exc}")
