import typing
from functools import lru_cache

if typing.TYPE_CHECKING:
    from ._config import Config
    from ._desktop import Desktop


@lru_cache  # Always return the same instance.
def desktop() -> "Desktop":
    from ._desktop import Desktop

    return Desktop()


@lru_cache
def config() -> "Config":
    from ._config import Config

    return Config()
