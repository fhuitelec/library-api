"""HTTP models for security responses."""

from typing import ClassVar

from pydantic import BaseModel, Field
from starlette.exceptions import HTTPException


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
