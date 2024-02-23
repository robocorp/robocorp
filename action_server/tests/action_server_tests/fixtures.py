import os
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

import pytest

from robocorp.action_server._selftest import (
    ActionServerClient,
    ActionServerProcess,
    robocorp_action_server_run,
)


@pytest.fixture
def action_server_datadir(tmpdir) -> Path:
    return Path(str(tmpdir)) / ".robocorp_action_server"


@pytest.fixture(scope="session")
def rcc_config_location(temp_directory_session) -> Path:
    ret = Path(temp_directory_session) / ".rcc_config"
    ret.mkdir(parents=True, exist_ok=True)
    ret = ret / "rcc.yaml"
    os.environ["RC_ACTION_SERVER_RCC_CONFIG_LOCATION"] = str(ret)
    return ret


@pytest.fixture(scope="session", autouse=True)
def disable_feedback(temp_directory_session, rcc_config_location) -> None:
    from robocorp.action_server._download_rcc import get_default_rcc_location
    from robocorp.action_server._rcc import Rcc

    robocorp_home = temp_directory_session / ".robocorp_home"
    robocorp_home.mkdir(parents=True, exist_ok=True)

    rcc_location = get_default_rcc_location()
    rcc = Rcc(rcc_location, robocorp_home)
    result = rcc._run_rcc(
        "configure identity --do-not-track --config".split()
        + [str(rcc_config_location)]
    )

    assert result.success
    result_msg = result.result
    assert result_msg
    if "disabled" not in result_msg:
        raise AssertionError(f"Did not expect {result_msg}")


@pytest.fixture
def action_server_process(action_server_datadir) -> Iterator[ActionServerProcess]:
    ret = ActionServerProcess(action_server_datadir)

    yield ret
    ret.stop()


CURDIR = Path(__file__).parent.absolute()


def get_in_resources(*parts) -> Path:
    curr = CURDIR / "resources"
    for part in parts:
        curr = curr / part
    return curr


@dataclass
class CaseInfo:
    action_server_process: ActionServerProcess
    db_path: Path


@pytest.fixture(scope="session")
def temp_directory_session(tmp_path_factory):
    temp_dir = tmp_path_factory.mktemp("temp_dir")

    # Can be used to customize a directory that's always the same across runs
    # (this way some tests can be speed-up by not having to recreate the db from
    # scratch).
    # temp_dir = Path("c:/temp")

    yield temp_dir


@pytest.fixture
def base_case(
    action_server_process: ActionServerProcess, tmpdir, temp_directory_session
) -> Iterator[CaseInfo]:
    from robocorp.action_server._database import Database
    from robocorp.action_server._models import (
        Action,
        ActionPackage,
        get_all_model_classes,
    )

    p = Path(str(tmpdir)) / ".robocorp_action_server"
    p.mkdir(parents=True, exist_ok=True)
    db_path = p / "server.db"
    assert not db_path.exists()

    persistent_dir = Path(temp_directory_session) / ".robocorp_action_server"
    persistent_dir.mkdir(parents=True, exist_ok=True)

    initial_db_version = persistent_dir / "initial.db"
    if not os.path.exists(initial_db_version):
        pack1 = get_in_resources("calculator")
        pack2 = get_in_resources("greeter")
        # Will have to generate the environment...

        robocorp_action_server_run(
            [
                "import",
                f"--dir={pack1}",
                f"--dir={pack2}",
                "--db-file=server.db",
                "-v",
                "--datadir",
                p,
            ],
            returncode=0,
        )
        shutil.copy(db_path, initial_db_version)
    else:
        shutil.copy(initial_db_version, db_path)

    assert db_path.exists()
    db = Database(db_path)
    db.register_classes(get_all_model_classes())
    with db.connect():
        assert set(x.name for x in db.all(ActionPackage)) == {"calculator", "greeter"}
        found = set(x.name for x in db.all(Action))
        assert found == {"calculator_sum", "greet", "broken_action"}

    action_server_process.start(
        db_file="server.db",
        timeout=500,
    )
    yield CaseInfo(action_server_process, db_path)


@pytest.fixture
def client(action_server_process: ActionServerProcess) -> Iterator[ActionServerClient]:
    yield ActionServerClient(action_server_process)


@pytest.fixture
def database_v0(tmpdir):
    from robocorp.action_server._database import Database

    db_path = Path(tmpdir) / "temp.db"
    initial_sql = [
        """
CREATE TABLE IF NOT EXISTS migration(
    id INTEGER NOT NULL PRIMARY KEY,
    name TEXT NOT NULL  
)
""",
        """
CREATE TABLE IF NOT EXISTS action_package(
    id TEXT NOT NULL PRIMARY KEY,
    name TEXT NOT NULL,
    directory TEXT NOT NULL,
    conda_hash TEXT NOT NULL,
    env_json TEXT NOT NULL  
)
""",
        """
CREATE UNIQUE INDEX action_package_id_index ON action_package(id);
""",
        """
CREATE UNIQUE INDEX action_package_name_index ON action_package(name);
""",
        """
CREATE TABLE IF NOT EXISTS action(
    id TEXT NOT NULL PRIMARY KEY,
    action_package_id TEXT NOT NULL,
    name TEXT NOT NULL,
    docs TEXT NOT NULL,
    file TEXT NOT NULL,
    lineno INTEGER NOT NULL,
    input_schema TEXT NOT NULL,
    output_schema TEXT NOT NULL,
    FOREIGN KEY (action_package_id) REFERENCES action_package(id)  
)
""",
        """
CREATE UNIQUE INDEX action_id_index ON action(id);
""",
        """
CREATE TABLE IF NOT EXISTS run(
    id TEXT NOT NULL PRIMARY KEY,
    status INTEGER NOT NULL,
    action_id TEXT NOT NULL,
    start_time TEXT NOT NULL,
    run_time REAL,
    inputs TEXT NOT NULL,
    result TEXT,
    error_message TEXT,
    relative_artifacts_dir TEXT NOT NULL,
    numbered_id INTEGER NOT NULL,
    FOREIGN KEY (action_id) REFERENCES action(id)  
)
""",
        """
CREATE UNIQUE INDEX run_id_index ON run(id);
""",
        """
CREATE UNIQUE INDEX run_numbered_id_index ON run(numbered_id);
""",
        """
CREATE TABLE IF NOT EXISTS counter(
    id TEXT NOT NULL PRIMARY KEY,
    value INTEGER NOT NULL  
)
""",
        """
CREATE UNIQUE INDEX counter_id_index ON counter(id);
""",
    ]

    db = Database(db_path)
    with db.connect():
        with db.transaction():
            db.execute("PRAGMA foreign_keys = ON")
            for sql in initial_sql:
                db.execute(sql)

            db.execute(
                "INSERT INTO action_package\n    (id, name, directory, conda_hash, env_json)\nVALUES\n    (?, ?, ?, ?, ?)\n",
                [
                    "ap-001-e8efd343-ccd5-470c-84bf-a32b9752e324",
                    "greeter",
                    "C:/temp/greeter",
                    "7c7a3dc1af2ba64fd30b9512f8e9c44405f57be8b609de9859173bf55f28b943",
                    '{"PYTHON_EXE": "c:/temp/python.exe"}',
                ],
            )
            db.execute(
                "INSERT INTO action\n    (id, action_package_id, name, docs, file, lineno, input_schema, output_schema)\nVALUES\n    (?, ?, ?, ?, ?, ?, ?, ?)\n",
                [
                    "act-001-bed9c7fd-9615-4bbe-a59a-5f35cb1c0f11",
                    "ap-001-e8efd343-ccd5-470c-84bf-a32b9752e324",
                    "greet",
                    "Provides a greeting for a person.",
                    "greeter_action.py",
                    4,
                    '{"additionalProperties": false, "properties": {"name": {"type": "string", "description": "The name of the person to greet.", "title": "Name"},"title": {"type": "string", "description": "The title for the persor (Mr., Mrs., ...).", "title": "Title", "default": "Mr."}}, "type": "object", "required": ["name"]}',
                    '{"type": "string", "description": "The greeting for the person."}',
                ],
            )
            db.execute(
                (
                    "INSERT INTO run "
                    "    (id, status, action_id, start_time, run_time, inputs, result, error_message, relative_artifacts_dir, numbered_id)"
                    "    VALUES\n    (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
                ),
                [
                    "run-001-usanoth-uosnthuo-uneothu-usneoth",
                    0,
                    "act-001-bed9c7fd-9615-4bbe-a59a-5f35cb1c0f11",
                    "2023-11-25T00:00:00+00:00",
                    None,
                    '{"name": "foo", "title": "Mr."}',
                    '"Hello Mr. foo."',
                    None,
                    "artifacts-dir-run1",
                    1,
                ],
            )
            db.execute(
                (
                    "INSERT INTO run "
                    "    (id, status, action_id, start_time, run_time, inputs, result, error_message, relative_artifacts_dir, numbered_id)"
                    "    VALUES\n    (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
                ),
                [
                    "run-002-usanoth-uosnthuo-uneothu-usneoth",
                    0,
                    "act-001-bed9c7fd-9615-4bbe-a59a-5f35cb1c0f11",
                    "2023-11-26T00:00:00+00:00",
                    None,
                    '{"name": "bar", "title": "Mr."}',
                    '"Hello Mr. bar."',
                    None,
                    "artifacts-dir-run2",
                    2,
                ],
            )

            db.execute(
                ("INSERT INTO counter     (id, value)    VALUES\n    (?, ?)"),
                [
                    "run_id",
                    2,
                ],
            )

            db.execute(
                ("INSERT INTO migration     (id, name)    VALUES\n    (?, ?)"),
                [
                    1,
                    "initial",
                ],
            )

    return db_path
