from functools import cache
from pathlib import Path

from pydantic import BaseModel


class Settings(BaseModel):
    title: str = "Task Server"

    address: str = "localhost"
    port: int = 8080
    watch: bool = False
    verbose: bool = False
    metadata: Path = Path(".robocorp")
    tasks: Path = Path("tasks.py")

    class Config:
        # pylint: disable=too-few-public-methods
        validate_assignment = True

    @classmethod
    def defaults(cls):
        props = cls.model_json_schema()["properties"]
        return {key: value.get("default") for key, value in props.items()}

    def from_args(self, args):
        self.address = args.address
        self.port = args.port
        self.watch = args.watch
        self.verbose = args.verbose

    def to_uvicorn(self):
        return {
            "host": self.address,
            "port": self.port,
            "reload": False,
            "log_config": None,
        }


@cache
def get_settings() -> Settings:
    return Settings()
