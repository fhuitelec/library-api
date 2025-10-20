"""Authorization utilities for FastAPI endpoints."""

from dataclasses import dataclass, field
from enum import StrEnum, auto
from typing import (
    Annotated,
)

from fastapi import HTTPException, status, Depends

from library_api.api.security import JWT
from library_api.api.security import Permission
from library_api.api.security.authentication import authentication


class PermissionMatcher(StrEnum):
    """Define how to match required permissions against granted permissions."""

    ALL = auto()
    ANY = auto()

    def enforce(self, required: frozenset[Permission], granted: set[Permission]) -> bool:
        """Check if the granted permissions satisfy the required permissions."""
        if self == PermissionMatcher.ALL:
            return required.issubset(granted)

        return not required.isdisjoint(granted)


@dataclass(frozen=True)
class RequirePermissions:
    """Enforce presence of a `jwt` parameter and validate required permissions.

    Args:
        required: Specify the permissions required to access the endpoint.
                  Example: {Permission.BOOK_READ, Permission.BOOK_MANAGE}.
        matcher: Set to ALL to require all permissions, or ANY to require at least one.

    Returns:
        Return a FastAPI dependency function that checks user permissions from the provided JWT claims.

    Examples:
        @router.post(
            "/example",
            dependencies=[
                require_permissions(required={Permission.LOAN_APPROVE}, matcher=PermissionMatcher.ANY)
            ]
        )

    """

    matcher: PermissionMatcher = PermissionMatcher.ALL
    required: frozenset[Permission] = field(default_factory=frozenset)

    def __post_init__(self) -> None:
        """Validate the object consistency."""
        if len(self.required) < 1:
            raise ValueError("At least one permission must be specified.")

    def __call__(self, jwt: Annotated[JWT, Depends(authentication)]) -> None:
        """Enforce required permissions against the JWT claims."""
        if self.matcher.enforce(self.required, jwt.permissions):
            return

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "insufficient_permissions",
                "required": sorted(self.required),
                "granted": sorted(jwt.permissions),
                "match": self.matcher,
            },
        )


def require_permissions(
    required: set[Permission],
    matcher: PermissionMatcher = PermissionMatcher.ALL,
) -> Depends:  # pyright: ignore[reportGeneralTypeIssues]
    """Syntactic sugar to declare a RequirePermissions dependency."""
    return Depends(RequirePermissions(required=frozenset(required), matcher=matcher))
