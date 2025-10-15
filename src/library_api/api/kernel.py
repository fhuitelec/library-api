"""Kernel of the FastAPI HTTP application."""

from http import HTTPStatus

import uvicorn
from fastapi import FastAPI
from fastapi.exception_handlers import http_exception_handler
from jwt import PyJWTError
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import Response

from library_api.api.config import get_auth_settings
from library_api.api.routers.auth import router as auth_router
from library_api.api.routers.temporary import router as temporary_router
from library_api.api.routers.loans import router as loans_router
from library_api.api.security.exceptions import (
    AuthenticationError,
    jwt_exception_handler,
    unauthorized_exception_handler,
)


async def native_http_exception_dispatcher_handler(request: Request, exc: HTTPException) -> Response:
    """Dispatch native HTTP exceptions to specialized handlers."""
    if exc.status_code == HTTPStatus.UNAUTHORIZED:
        return await unauthorized_exception_handler(request, exc)

    return await http_exception_handler(request, exc)


app = FastAPI(
    exception_handlers={PyJWTError: jwt_exception_handler, HTTPException: native_http_exception_dispatcher_handler},
    responses={HTTPStatus.UNAUTHORIZED: {"model": AuthenticationError}},
    swagger_ui_init_oauth={
        "usePkceWithAuthorizationCodeGrant": True,
        "clientId": get_auth_settings().swagger_client_id,
    },
)

app.include_router(auth_router)
app.include_router(temporary_router)
app.include_router(loans_router)


def server() -> None:
    """Run the ASGI server."""
    uvicorn.run("library_api.api.kernel:app", host="0.0.0.0", port=8000, reload=True, server_header=False)
