"""Root module of library-api package."""

import datetime
import uuid
from typing import Union, Annotated, Mapping, Any

from fastapi import FastAPI, Depends
import uvicorn
from library_api.security.authentication import authentication
from library_api.security.authorization import requires_permissions, Permission
from pydantic import BaseModel

app = FastAPI()


@app.get("/")
@requires_permissions([Permission.BOOK_READ, Permission.LOAN_APPROVE], match="all")
async def read_root(jwt: Annotated[Mapping[str, Any], Depends(authentication)]) -> dict[str, str | Mapping[str, Any]]:
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
    uvicorn.run(app, host="0.0.0.0", port=8000)


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
