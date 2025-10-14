"""Root module of library-api package."""

import datetime
import uuid
from http import HTTPStatus
from typing import Union, Annotated

import uvicorn
from fastapi import FastAPI, Depends
from fastapi.exception_handlers import http_exception_handler
from jwt import PyJWTError
from library_api.security.authentication import authentication, JWT
from library_api.security.authorization import requires_permissions, Permission, PermissionMatcher
from library_api.security.exceptions import jwt_exception_handler, unauthorized_exception_handler
from library_api.security.http import AuthenticationResponse
from pydantic import BaseModel
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import Response


async def native_http_exception_dispatcher_handler(request: Request, exc: HTTPException) -> Response:
    """Dispatch native HTTP exceptions to specialized handlers."""
    if exc.status_code == HTTPStatus.UNAUTHORIZED:
        return await unauthorized_exception_handler(request, exc)

    return await http_exception_handler(request, exc)


app = FastAPI(
    exception_handlers={PyJWTError: jwt_exception_handler, HTTPException: native_http_exception_dispatcher_handler},
    responses={HTTPStatus.UNAUTHORIZED: {"model": AuthenticationResponse}},
    swagger_ui_init_oauth={
        "usePkceWithAuthorizationCodeGrant": True,
        "clientId": "woDXg79hSdK9DAhmFFunvehAtlvArr8D",  # Todo: add settings
    },
)


@app.get("/")
@requires_permissions({Permission.BOOK_READ, Permission.LOAN_APPROVE}, matcher=PermissionMatcher.ANY)
async def read_root(jwt: Annotated[JWT, Depends(authentication)]) -> dict[str, str | JWT]:
    """Return a greeting message."""
    return {
        "Hello": "World",
        "jwt": jwt,
    }


@app.get("/items/{item_id}")
async def read_item(item_id: int, q: Union[str, None] = None) -> dict[str, Union[str, int, None]]:
    """Read items."""
    return {"item_id": item_id, "q": q}


def server() -> None:
    """Run the ASGI server."""
    uvicorn.run("library_api.main:app", host="0.0.0.0", port=8000, reload=True, server_header=False)


class Book(BaseModel):
    """Book model."""

    id: uuid.UUID
    human_id: str  # EDITOR-TITLE-ID, eg. ALI-FEELGOOD-001
    issue: int
    isbn: str
    title: str
    title: str
    author: str
    publisher: str
    publish_date: datetime.datetime


# uuid.uuid7() -> passer à Python 3.14 -> https://docs.python.org/3/library/uuid.html#uuid.uuid7
# Primary key indexation en UUIDv7
# Constraint on human_id + copy: https://stackoverflow.com/a/14221810
