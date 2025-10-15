"""Exceptions for the security package."""

from http import HTTPStatus

from jwt import PyJWTError
from library_api.security.http import AuthenticationError
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import Response, JSONResponse


async def jwt_exception_handler(_: Request, exc: PyJWTError) -> Response:
    """Handle JWT-related exceptions."""
    return JSONResponse(AuthenticationError.jwt_error(exc).model_dump(), status_code=HTTPStatus.UNAUTHORIZED)


async def unauthorized_exception_handler(_: Request, exc: HTTPException) -> Response:
    """Handle FastAPI native authentication exceptions."""
    if exc.status_code == HTTPStatus.UNAUTHORIZED:
        return JSONResponse(AuthenticationError.unauthenticated(exc).model_dump(), status_code=HTTPStatus.UNAUTHORIZED)

    raise RuntimeError(f"Unhandled exception: {exc}")
