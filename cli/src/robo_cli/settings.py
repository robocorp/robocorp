from functools import lru_cache

from pydantic import BaseModel


class Settings(BaseModel):
    verbose: bool = False

    class Config:
        # pylint: disable=too-few-public-methods
        validate_assignment = True


@lru_cache
def get_settings():
    return Settings()
