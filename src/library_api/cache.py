"""Cache-related utilities."""

from typing import Any

from cachetools.keys import hashkey, typedkey


def key_id_hashkey(*_: Any, kid: str | None = None, **__: Any) -> tuple:  # pylint: disable=unused-argument # noqa: ANN002,ANN401
    """Hit the cache for a given key ID and ignore other args & kwargs."""
    return typedkey(kid)


def ignore_args_hashkey(*_: Any, **__: Any) -> tuple:  # pylint: disable=unused-argument # noqa: ANN002,ANN401
    """Hit the cache even if the function arguments are different."""
    return hashkey("_")
