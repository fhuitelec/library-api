"""Security module for the Library API."""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class Permission(StrEnum):
    """List of available permissions."""

    BOOK_READ = "book:read"
    BOOK_MANAGE = "book:manage"
    LOAN_APPROVE = "loan:approve"
    LOAN_REQUEST = "loan:request"
    LOAN_READ = "loan:read"


class JWT(BaseModel):
    """Representation of a JSON Web Token."""

    issuer: str = Field(validation_alias="iss")
    subjet: str = Field(validation_alias="sub")
    audience: str = Field(validation_alias="aud")
    issued_at: datetime = Field(validation_alias="iat")
    expires_at: datetime = Field(validation_alias="exp")
    authorized_party: str = Field(validation_alias="azp")
    permissions: set["Permission"]
