"""Kernel of the FastAPI HTTP application."""

import uvicorn
from fastapi import FastAPI

from library_api.api.config import get_auth_settings
from library_api.api.routers.auth import router as auth_router
from library_api.api.routers.loans import router as loans_router

app = FastAPI(
    swagger_ui_init_oauth={
        "usePkceWithAuthorizationCodeGrant": True,
        "clientId": get_auth_settings().swagger_client_id,
    },
)

app.include_router(auth_router)
app.include_router(loans_router)


def server() -> None:
    """Run the ASGI server."""
    uvicorn.run("library_api.api.kernel:app", host="0.0.0.0", port=8000, reload=True, server_header=False)
