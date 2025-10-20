"""Authorization utilities for FastAPI endpoints."""

from dataclasses import dataclass, field
from typing import (
    Annotated,
)

from fastapi import HTTPException, status, Depends

from library_api.api.security import JWT
from library_api.api.security import Permission
from library_api.api.security.authentication import authentication


@dataclass(frozen=True)
class RequirePermissions:
    """Enforce presence of a `jwt` parameter and validate required permissions.

    Args:
        required: Specify the permissions required to access the endpoint.
                  Example: {Permission.BOOK_READ, Permission.BOOK_MANAGE}.

    Returns:
        Return a FastAPI dependency function that checks user permissions from the provided JWT claims.

    Examples:
        @router.post(
            "/example",
            dependencies=[
                require_permissions(required={Permission.LOAN_APPROVE})
            ]
        )

    """

    required: frozenset[Permission] = field(default_factory=frozenset)

    def __post_init__(self) -> None:
        """Validate the object consistency."""
        if len(self.required) < 1:
            raise ValueError("At least one permission must be specified.")

    def __call__(self, jwt: Annotated[JWT, Depends(authentication)]) -> None:
        """Enforce required permissions against the JWT claims."""
        if self.required.issubset(jwt.permissions):
            return

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "insufficient_permissions",
                "required": sorted(self.required),
                "granted": sorted(jwt.permissions),
            },
        )


def require_permissions(required: set[Permission]) -> Depends:  # pyright: ignore[reportGeneralTypeIssues]
    """Syntactic sugar to declare a RequirePermissions dependency."""
    return Depends(RequirePermissions(required=frozenset(required)))
