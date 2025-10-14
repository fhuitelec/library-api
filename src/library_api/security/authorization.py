"""Authorization utilities for FastAPI endpoints."""

from __future__ import annotations

from enum import StrEnum, auto
from functools import wraps
from typing import (
    Callable,
)

from fastapi import HTTPException, status
from library_api.security import Permission
from library_api.security.authentication import JWT
from library_api.security.typing import EndpointFunction, HandlerWithJWT, EndpointArguments, EndpointReturn


class PermissionMatcher(StrEnum):
    """Define how to match required permissions against granted permissions."""

    ALL = auto()
    ANY = auto()

    def enforce(self, required: set[Permission], granted: set[Permission]) -> bool:
        """Check if the granted permissions satisfy the required permissions."""
        if self == PermissionMatcher.ALL:
            return required.issubset(granted)

        return not required.isdisjoint(granted)


def requires_permissions(
    required: set[Permission],
    matcher: PermissionMatcher = PermissionMatcher.ALL,
) -> Callable[[EndpointFunction], EndpointFunction]:
    """Enforce presence of a `jwt` parameter and validate required permissions.

    Args:
        required: Specify the permissions required to access the endpoint.
                  Example: {Permission.BOOK_READ, Permission.BOOK_MANAGE}.
        matcher: Set to ALL to require all permissions, or ANY to require at least one.

    Returns:
        Return a decorator that checks user permissions from the provided JWT claims.

    Examples:
        @requires_permissions({Permission.BOOK_READ})
        async def get_book(jwt: JWT, book_id: str):
            ...

        @requires_permissions({Permission.BOOK_MANAGE, Permission.LOAN_APPROVE}, PermissionMatcher.ANY)
        async def admin_endpoint(jwt: JWT):
            ...

    """
    if len(required) < 1:
        raise ValueError("At least one permission must be specified.")

    if not all(isinstance(perm, Permission) for perm in required):
        raise ValueError("All required permissions must be valid Permission enum values.")

    def decorator(
        func: HandlerWithJWT[EndpointArguments, EndpointReturn],
    ) -> HandlerWithJWT[EndpointArguments, EndpointReturn]:
        """Apply the authorization logic to the FastAPI endpoint.

        Ensure that:
        - The endpoint defines a `jwt` parameter (enforced by typing).
        - Runtime validation confirms that `jwt` is provided and is a JWT instance.
        - The user's permissions match the required permissions.
        """

        @wraps(func)
        async def wrapper(
            jwt: JWT, *args: EndpointArguments.args, **kwargs: EndpointArguments.kwargs
        ) -> EndpointReturn:
            """Perform runtime authorization checks before executing the handler.

            1. Retrieve the `jwt` argument from the endpoint call.
            2. Verify its presence and structure.
            3. Compare user permissions against the required set.
            4. Raise HTTP 403 if authorization fails.
            5. Invoke the wrapped handler if checks pass.
            """
            if jwt is None:
                raise TypeError(
                    "requires_permissions() decorator needs an argument "
                    "'jwt: library_api.security.authentication.JWT' in the endpoint signature."
                )

            if not matcher.enforce(required, jwt.permissions):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail={
                        "error": "insufficient_permissions",
                        "required": sorted(required),
                        "granted": sorted(jwt.permissions),
                        "match": matcher,
                    },
                )

            return await func(jwt, *args, **kwargs)

        return wrapper

    return decorator
