"""Exceptions for the security package."""

from http import HTTPStatus
from typing import ClassVar

from jwt import PyJWTError
from pydantic import BaseModel, Field
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import Response, JSONResponse


class AuthenticationError(BaseModel):
    """Error during the authentication process."""

    UNAUTHENTICATED_RESOLUTION: ClassVar[str] = "You must add a bearer 'Authorization' header with a valid JWT token."

    detail: str = Field(examples=["Cannot decode JWT"], description="Details about the authentication issue")
    resolution: str | None = Field(
        default=None, examples=["Add X-Example header"], description="Hints on how to resolve the issue"
    )

    @classmethod
    def jwt_error(cls, exc: Exception, resolution: str | None = None) -> "AuthenticationError":
        """Create an AuthenticationResponse from an exception."""
        return AuthenticationError(detail=str(exc), resolution=resolution or cls.UNAUTHENTICATED_RESOLUTION)

    @classmethod
    def unauthenticated(cls, exc: HTTPException) -> "AuthenticationError":
        """Create an AuthenticationResponse from an exception."""
        return AuthenticationError(detail=exc.detail, resolution=cls.UNAUTHENTICATED_RESOLUTION)


async def jwt_exception_handler(_: Request, exc: PyJWTError) -> Response:
    """Handle JWT-related exceptions."""
    return JSONResponse(AuthenticationError.jwt_error(exc).model_dump(), status_code=HTTPStatus.UNAUTHORIZED)


async def unauthorized_exception_handler(_: Request, exc: HTTPException) -> Response:
    """Handle FastAPI native authentication exceptions."""
    if exc.status_code == HTTPStatus.UNAUTHORIZED:
        return JSONResponse(AuthenticationError.unauthenticated(exc).model_dump(), status_code=HTTPStatus.UNAUTHORIZED)

    raise RuntimeError(f"Unhandled exception: {exc}")
