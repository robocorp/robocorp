import typing
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, Optional, Union

from pydantic.dataclasses import dataclass

if typing.TYPE_CHECKING:
    from robocorp.action_server._database import Database


@dataclass
class ActionPackage:  # Table name: action_package
    id: str  # primary key (uuid)
    name: str  # The name for the action package

    # The directory where the action package is (may be stored relative
    # to the datadir or as an absolute path).
    # When relative starts with `./`, otherwise it's absolute.
    directory: str

    # The sha256 hash of the conda.yaml (based only on the actual content
    # not considering spaces and comments).
    conda_hash: str

    # The environment to be used for launches (as json).
    env_json: str


@dataclass
class Action:
    id: str  # primary key (uuid)
    action_package_id: str  # foreign key to the action package
    name: str  # The action name
    docs: str  # Docs for the action

    # File for the action (relative to the directory in the ActionPackage).
    file: str

    lineno: int  # Line for the action
    input_schema: str  # The json content for the schema input
    output_schema: str  # The json content for the schema output


@dataclass
class Run:
    id: str  # primary key (uuid)
    status: int  # 0=not run, 1=running, 2=passed, 3=failed
    action_id: str  # foreign key to the action
    start_time: str  # The time of the run creation.
    run_time: Optional[
        float
    ]  # The time from the run creation to the run finish (in seconds)
    inputs: str  # The json content with the variables used as an input
    result: Optional[str]  # The json content of the output that the run generated
    error_message: Optional[str]  # If the status=failed, this may have an error message

    # The path (relative to the datadir) of the artifacts generated in the run
    relative_artifacts_dir: Optional[str]


class RunStatus:
    NOT_RUN = 0
    RUNNING = 1
    PASSED = 2
    FAILED = 3


def get_all_model_classes():
    return [ActionPackage, Action, Run]


_global_db: Optional["Database"] = None


@contextmanager
def initialize_db(db_path: Union[Path, str]) -> Iterator["Database"]:
    from robocorp.action_server._database import Database

    global _global_db

    if _global_db is not None:
        raise AssertionError("There is already a global initialized database.")

    db = Database(db_path)
    with db.connect():
        db.initialize(get_all_model_classes())
        _global_db = db
        try:
            yield db
        finally:
            _global_db = None


def get_db() -> "Database":
    assert _global_db is not None, "DB not initialized"
    return _global_db


def get_action_package_from_action(action: Action) -> ActionPackage:
    db = get_db()
    return db.first(
        ActionPackage,
        "SELECT * FROM action_package WHERE id = ?",
        [action.action_package_id],
    )
