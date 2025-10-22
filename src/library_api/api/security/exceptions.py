"""Exceptions for the security package."""

from http import HTTPStatus

from jwt import PyJWTError
from pydantic import BaseModel, Field
from starlette.requests import Request
from starlette.responses import Response, JSONResponse


class AuthenticationError(BaseModel):
    """Error during the authentication process."""

    detail: str = Field(examples=["Cannot decode JWT"], description="Details about the authentication issue")


async def jwt_exception_handler(_: Request, exc: PyJWTError) -> Response:
    """Handle JWT-related exceptions."""
    return JSONResponse(AuthenticationError(detail=str(exc)).model_dump(), status_code=HTTPStatus.UNAUTHORIZED)
