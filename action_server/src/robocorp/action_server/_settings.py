import logging
import sys
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, Optional

from pydantic import BaseModel

log = logging.getLogger(__name__)


class Settings(BaseModel):
    title: str = "Robocorp Actions Server"

    address: str = "localhost"
    port: int = 8080
    verbose: bool = False
    db_file: str = "server.db"
    expose_url: str = "robocorp.link"

    artifacts_dir: Path
    datadir: Path

    class Config:
        # pylint: disable=too-few-public-methods
        validate_assignment = True

    @classmethod
    def defaults(cls):
        props = cls.model_json_schema()["properties"]
        return {key: value.get("default") for key, value in props.items()}

    def __init__(self, args):
        user_specified_datadir = args.datadir
        if not user_specified_datadir:
            import hashlib

            curr_cwd_dir = Path(".").absolute()
            name = curr_cwd_dir.name
            as_posix = curr_cwd_dir.as_posix()
            if sys.platform == "win32":
                as_posix = as_posix.lower()

            # Not secure, but ok for our purposes
            short_hash = hashlib.sha256(as_posix.encode()).hexdigest()[:8]
            datadir_name = f"~/.robocorp_action_server/{name}_{short_hash}"

            log.info(f"Using datadir (scoped to the current directory): {datadir_name}")
            user_expanded_datadir = Path(datadir_name).expanduser()

        else:
            log.info(f"Using user-specified datadir: {user_specified_datadir}")
            user_expanded_datadir = Path(user_specified_datadir).expanduser()

        datadir = user_expanded_datadir.absolute()
        super().__init__(datadir=datadir, artifacts_dir=datadir / "artifacts")
        # Optional (just in 'start' command, not in 'import')
        if hasattr(args, "address"):
            self.address = args.address

        if hasattr(args, "port"):
            self.port = args.port

        # Used in either import or start commands.
        self.verbose = args.verbose
        self.db_file = args.db_file

    def to_uvicorn(self):
        return {
            "host": self.address,
            "port": self.port,
            "reload": False,
            "log_config": None,
        }


_global_settings: Optional[Settings] = None


@contextmanager
def setup_settings(args) -> Iterator[Settings]:
    global _global_settings
    settings = Settings(args)
    _global_settings = settings
    try:
        yield settings
    finally:
        _global_settings = None


def get_settings() -> Settings:
    if _global_settings is None:
        raise AssertionError("It seems that the settings have not been setup yet.")
    return _global_settings
