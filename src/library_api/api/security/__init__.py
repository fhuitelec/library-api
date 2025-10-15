"""Security module for the Library API."""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field, AliasChoices


class Permission(StrEnum):
    """List of available permissions."""

    BOOK_READ = "book:read"
    BOOK_MANAGE = "book:manage"
    LOAN_APPROVE = "loan:approve"
    LOAN_REQUEST = "loan:request"
    LOAN_READ = "loan:read"


class JWT(BaseModel):
    """Representation of a JSON Web Token."""

    issuer: str = Field(validation_alias=AliasChoices("iss", "issuer"))
    subjet: str = Field(validation_alias=AliasChoices("sub", "subjet"))
    audience: str = Field(validation_alias=AliasChoices("aud", "audience"))
    issued_at: datetime = Field(validation_alias=AliasChoices("iat", "issued_at"))
    expires_at: datetime = Field(validation_alias=AliasChoices("exp", "expires_at"))
    authorized_party: str = Field(validation_alias=AliasChoices("azp", "authorized_party"))
    permissions: set["Permission"]
