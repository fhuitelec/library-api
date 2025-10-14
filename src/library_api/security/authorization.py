"""Authorization utilities for FastAPI endpoints."""

from __future__ import annotations

from enum import StrEnum
from functools import wraps
from typing import (
    Callable,
    Iterable,
    Literal,
    Any,
    Awaitable,
    Protocol,
    ParamSpec,
    TypeVar,
    Mapping,
    TypeAlias,
)

from fastapi import HTTPException, status

EndpointArguments = ParamSpec("EndpointArguments")
EndpointReturn = TypeVar("EndpointReturn", covariant=True)


class HandlerWithJWT(Protocol[EndpointArguments, EndpointReturn]):
    """Define a FastAPI handler that must accept a `jwt` parameter.

    Type parameters:
        EndpointArguments: Capture positional and keyword argument specifications.
        EndpointReturn: Represent the return type of the async handler.

    Ensure that any decorated endpoint explicitly defines
    a `jwt: Mapping[str, Any]` parameter in its signature.

    If your encounter any error like below...
    > cannot be assigned to parameter of type "EndpointFunction[..., Unknown]"

    ...you must add a `jwt: Mapping[str, Any]` parameter to your endpoint, for example:
        async def endpoint(jwt: Mapping[str, Any]): ...
    """

    def __call__(
        self, jwt: Mapping[str, Any], *args: EndpointArguments.args, **kwargs: EndpointArguments.kwargs
    ) -> Awaitable[EndpointReturn]:
        """Define the callable signature for FastAPI handlers requiring a `jwt` argument.

        Args:
            jwt: Provide a mapping of decoded JWT claims.
            *args: Accept positional arguments for the handler.
            **kwargs: Accept additional keyword arguments.

        Returns:
            Return an awaitable result of type `R` produced by the handler.

        """
        ...


EndpointFunction: TypeAlias = HandlerWithJWT[EndpointArguments, EndpointReturn]


class Permission(StrEnum):
    """List of available permissions."""

    BOOK_READ = "book:read"
    BOOK_MANAGE = "book:manage"
    LOAN_APPROVE = "loan:approve"
    LOAN_REQUEST = "loan:request"
    LOAN_READ = "loan:read"


def requires_permissions(
    required: Iterable[Permission],
    *,
    match: Literal["all", "any"] = "all",
) -> Callable[[EndpointFunction], EndpointFunction]:
    """Enforce presence of a `jwt` parameter and validate required permissions.

    Args:
        required: Specify the permissions required to access the endpoint.
                  Example: ["read:books", "write:books"].
        match: Set to "all" to require all permissions, or "any" to require at least one.

    Returns:
        Return a decorator that checks user permissions from the provided JWT claims.

    """
    required_set = set(required)

    def decorator(
        func: HandlerWithJWT[EndpointArguments, EndpointReturn],
    ) -> HandlerWithJWT[EndpointArguments, EndpointReturn]:
        """Apply the authorization logic to the FastAPI endpoint.

        Ensure that:
        - The endpoint defines a `jwt` parameter (enforced by typing).
        - Runtime validation confirms that `jwt` is provided and is a Mapping.
        - The user's permissions match the required permissions.
        """

        @wraps(func)
        async def wrapper(
            jwt: Mapping[str, Any], *args: EndpointArguments.args, **kwargs: EndpointArguments.kwargs
        ) -> EndpointReturn:
            """Perform runtime authorization checks before executing the handler.

            1. Retrieve the `jwt` argument from the endpoint call.
            2. Verify its presence and structure.
            3. Compare user permissions against the required set.
            4. Raise HTTP 403 if authorization fails.
            5. Invoke the wrapped handler if checks pass.
            """
            if jwt is None:
                raise RuntimeError(
                    "requires_permissions() decorator needs an argument 'jwt: dict' in the endpoint signature."
                )

            user_perms = set(jwt.get("permissions", []))
            if match == "all":
                ok = required_set.issubset(user_perms)
            else:
                ok = not required_set.isdisjoint(user_perms)

            if not ok:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail={
                        "error": "insufficient_permissions",
                        "required": sorted(required_set),
                        "granted": sorted(user_perms),
                        "match": match,
                    },
                )

            return await func(jwt, *args, **kwargs)

        return wrapper

    return decorator
