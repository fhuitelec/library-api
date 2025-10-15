"""Typing definitions for authentication & authorization."""

from __future__ import annotations

from typing import (
    Awaitable,
    Protocol,
    ParamSpec,
    TypeVar,
    TypeAlias,
)

from library_api.api.security import JWT

EndpointArguments = ParamSpec("EndpointArguments")
EndpointReturn = TypeVar("EndpointReturn", covariant=True)


class HandlerWithJWT(Protocol[EndpointArguments, EndpointReturn]):
    """Define a FastAPI handler that must accept a `jwt` parameter.

    Type parameters:
        EndpointArguments: Capture positional and keyword argument specifications.
        EndpointReturn: Represent the return type of the async handler.

    Ensure that any decorated endpoint explicitly defines
    a `jwt: JWT` parameter in its signature.

    If your encounter any error like below...
    > cannot be assigned to parameter of type "EndpointFunction[..., Unknown]"

    ...you must add a `jwt: JWT` parameter to your endpoint, for example:
        async def endpoint(jwt: JWT): ...
    """

    def __call__(
        self, jwt: JWT, *args: EndpointArguments.args, **kwargs: EndpointArguments.kwargs
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
