"""Configuration for the Library API application."""

from functools import lru_cache
from typing import Annotated

import httpx
from fastapi.params import Depends
from pydantic_settings import BaseSettings, SettingsConfigDict


class AuthenticationSettings(BaseSettings):
    """Settings for authentication with Auth0."""

    model_config = SettingsConfigDict(frozen=True)

    tenant_base_url: str = "https://fabien-sh.eu.auth0.com"
    audience: str = "library-api"

    jwks_path: str = "/.well-known/jwks.json"

    authorization_path: str = "/authorize"
    token_path: str = "/oauth/token"

    @property
    def authorization(self) -> str:
        """Get the authorization URL with audience."""
        return f"{self.authorization_path}?audience={self.audience}"


@lru_cache
def get_auth_settings() -> AuthenticationSettings:
    """Get the authentication settings."""
    return AuthenticationSettings()


@lru_cache
def get_auth_client(auth_settings: Annotated[AuthenticationSettings, Depends(get_auth_settings)]) -> httpx.Client:
    """Get the HTTP client for authentication."""
    return httpx.Client(base_url=auth_settings.tenant_base_url, timeout=5)
