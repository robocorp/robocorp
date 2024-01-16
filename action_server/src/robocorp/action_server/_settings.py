import logging
import os
import sys
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, Optional

log = logging.getLogger(__name__)


def is_frozen():
    if getattr(sys, "frozen", False):
        return True
    try:
        __file__
    except NameError:
        return True

    return False


def get_python_exe_from_env(env):
    python = env.get("PYTHON_EXE")
    if not python:
        if is_frozen():
            raise RuntimeError(
                "Unable to run because no 'conda.yaml' was present to bootstrap the environment\n"
                "(note: when the action server is distributed without sources, a 'conda.yaml' for "
                "the target environment is always required)."
            )
        else:
            python = sys.executable

    return python


def get_default_settings_dir() -> Path:
    if sys.platform == "win32":
        localappdata = os.environ.get("LOCALAPPDATA")
        if not localappdata:
            raise RuntimeError("Error. LOCALAPPDATA not defined in environment!")
        path = Path(localappdata) / "robocorp" / ".action_server"
    else:
        # Linux/Mac
        path = Path("~/robocorp/.action_server").expanduser()

    path.mkdir(parents=True, exist_ok=True)
    return path


@dataclass(slots=True, kw_only=True)
class Settings:
    artifacts_dir: Path
    datadir: Path

    title: str = "Robocorp Actions Server"

    address: str = "localhost"
    port: int = 8080
    verbose: bool = False
    db_file: str = "server.db"
    expose_url: str = "robocorp.link"
    server_url: str = "http://localhost:8080"

    @classmethod
    def defaults(cls):
        fields = cls.__dataclass_fields__
        ret = {}
        SENTINEL = []
        for name, field in fields.items():
            v = getattr(field, "default", SENTINEL)
            if v is not SENTINEL:
                ret[name] = v
        return ret

    @classmethod
    def create(cls, args) -> "Settings":
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
            datadir_name = f"{get_default_settings_dir()}/{name}_{short_hash}"

            log.info(f"Using datadir (scoped to the current directory): {datadir_name}")
            user_expanded_datadir = Path(datadir_name).expanduser()

        else:
            log.info(f"Using user-specified datadir: {user_specified_datadir}")
            user_expanded_datadir = Path(user_specified_datadir).expanduser()

        datadir = user_expanded_datadir.absolute()

        settings = Settings(datadir=datadir, artifacts_dir=datadir / "artifacts")
        # Optional (just in 'start' command, not in 'import')
        if hasattr(args, "address"):
            settings.address = args.address

        if hasattr(args, "port"):
            settings.port = args.port

        if hasattr(args, "server_url") and args.server_url is not None:
            settings.server_url = args.server_url
        else:
            settings.server_url = f"http://{settings.address}:{settings.port}"

        # Used in either import or start commands.
        settings.verbose = args.verbose
        settings.db_file = args.db_file
        return settings

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
    settings = Settings.create(args)
    _global_settings = settings
    try:
        yield settings
    finally:
        _global_settings = None


def get_settings() -> Settings:
    if _global_settings is None:
        raise AssertionError("It seems that the settings have not been setup yet.")
    return _global_settings
