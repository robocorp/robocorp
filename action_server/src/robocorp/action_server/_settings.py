from functools import cache
from pathlib import Path

from pydantic import BaseModel


class Settings(BaseModel):
    title: str = "Robocorp Actions Server"

    address: str = "localhost"
    port: int = 8080
    verbose: bool = False
    datadir: Path = Path("~/.robocorp_action_server")
    db_file: str = "server.db"
    artifacts_dir: Path = Path(".robocorp_action_server") / "artifacts"

    class Config:
        # pylint: disable=too-few-public-methods
        validate_assignment = True

    @classmethod
    def defaults(cls):
        props = cls.model_json_schema()["properties"]
        return {key: value.get("default") for key, value in props.items()}

    def from_args(self, args):
        # Optional (just in 'start' command, not in 'import')
        if hasattr(args, "address"):
            self.address = args.address

        if hasattr(args, "port"):
            self.port = args.port

        # Used in either import or start commands.
        self.verbose = args.verbose
        self.datadir = Path(args.datadir).expanduser().absolute()
        self.db_file = args.db_file

        self.artifacts_dir = self.datadir / "artifacts"

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
