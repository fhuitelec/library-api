"""HTTP models for security responses."""

from typing import ClassVar

from pydantic import BaseModel, Field
from starlette.exceptions import HTTPException


class AuthenticationResponse(BaseModel):
    """Response model for authentication."""

    UNAUTHENTICATED_RESOLUTION: ClassVar[str] = "You must add a bearer 'Authorization' header with a valid JWT token."

    detail: str = Field(examples=["Cannot decode JWT"], description="Details about the authentication issue")
    resolution: str | None = Field(
        default=None, examples=["Add X-Example header"], description="Hints on how to resolve the issue"
    )

    @staticmethod
    def jwt_error(exc: Exception, resolution: str | None = None) -> "AuthenticationResponse":
        """Create an AuthenticationResponse from an exception."""
        return AuthenticationResponse(detail=str(exc), resolution=resolution)

    @classmethod
    def unauthenticated(cls, exc: HTTPException) -> "AuthenticationResponse":
        """Create an AuthenticationResponse from an exception."""
        return AuthenticationResponse(detail=exc.detail, resolution=cls.UNAUTHENTICATED_RESOLUTION)
