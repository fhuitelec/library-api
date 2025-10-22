"""Security module for the Library API."""

from datetime import datetime

from pydantic import BaseModel, Field, AliasChoices


class JWT(BaseModel):
    """Representation of a JSON Web Token."""

    issuer: str = Field(validation_alias=AliasChoices("iss", "issuer"))
    subject: str = Field(validation_alias=AliasChoices("sub", "subject"))
    audience: str | list[str] = Field(validation_alias=AliasChoices("aud", "audience"))
    issued_at: datetime = Field(validation_alias=AliasChoices("iat", "issued_at"))
    expires_at: datetime = Field(validation_alias=AliasChoices("exp", "expires_at"))
    authorized_party: str = Field(validation_alias=AliasChoices("azp", "authorized_party"))
    permissions: set[str]
