"""Root module of library-api package."""

from typing import Union

from fastapi import FastAPI
import uvicorn

app = FastAPI()


@app.get("/")
def read_root() -> dict[str, str]:
    """Return a greeting message."""
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(
    item_id: int, q: Union[str, None] = None
) -> dict[str, Union[str, int, None]]:
    """Read items."""
    return {"item_id": item_id, "q": q}


def server() -> None:
    """Run the ASGI server."""
    uvicorn.run(app, host="0.0.0.0", port=8000)
