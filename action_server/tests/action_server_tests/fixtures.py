import json
import os
import re
import subprocess
import sys
import time
import typing
from concurrent.futures import TimeoutError
from pathlib import Path
from subprocess import CompletedProcess
from typing import Dict, Iterator, Literal, Optional, Tuple, Union

import pytest

if typing.TYPE_CHECKING:
    from robocorp.action_server._robo_utils.process import Process


def robocorp_action_server_run(
    cmdline,
    returncode: Union[Literal["error"], int],
    cwd=None,
    additional_env: Optional[Dict[str, str]] = None,
    timeout=None,
) -> CompletedProcess:
    return run_python_module(
        "robocorp.action_server", cmdline, returncode, cwd, additional_env, timeout
    )


def run_python_module(
    python_module: str,
    cmdline,
    returncode: Union[Literal["error"], int],
    cwd=None,
    additional_env: Optional[Dict[str, str]] = None,
    timeout=None,
) -> CompletedProcess:
    cp = os.environ.copy()
    cp["PYTHONPATH"] = os.pathsep.join([x for x in sys.path if x])
    if additional_env:
        cp.update(additional_env)
    args = [sys.executable, "-m", python_module] + cmdline
    result = subprocess.run(
        args, capture_output=True, text=True, env=cp, cwd=cwd, timeout=timeout
    )

    if returncode == "error" and result.returncode:
        return result

    if result.returncode == returncode:
        return result

    env_str = "\n".join(str(x) for x in sorted(cp.items()))

    raise AssertionError(
        f"""Expected returncode: {returncode}. Found: {result.returncode}.
=== stdout:
{result.stdout}

=== stderr:
{result.stderr}

=== Env:
{env_str}

=== Args:
{args}

"""
    )


class ActionServerProcess:
    SHOW_OUTPUT = True

    def __init__(self, datadir: Path) -> None:
        self._datadir = datadir.absolute()
        self._process: Optional["Process"] = None
        self._host: str = ""
        self._port: int = -1
        self.started: bool = False

    @property
    def datadir(self) -> Path:
        return self._datadir

    @property
    def host(self) -> str:
        if not self.started:
            self.start()

        assert (
            self._host
        ), "The action server was not properly started (no host available)"
        return self._host

    @property
    def port(self) -> int:
        if not self.started:
            self.start()

        assert (
            self._port > 0
        ), "The action server was not properly started (no port available)"
        return self._port

    @property
    def process(self) -> "Process":
        assert (
            self._process is not None
        ), "The action server was not properly started (process is None)."
        return self._process

    def start(self, args=("--db-file=:memory:",), timeout=10) -> None:
        from robocorp.action_server._robo_utils.process import Process

        if self.started:
            raise RuntimeError("The action process was already started.")

        self.started = True
        from concurrent.futures import Future

        new_args = (
            sys.executable,
            "-m",
            "robocorp.action_server",
            "start",
            "--port=0",
            "--verbose",
            f"--datadir={str(self._datadir)}",
        ) + args
        process = self._process = Process(new_args)

        compiled = re.compile(r"http://([\w.-]+):(\d+)")
        future: Future[Tuple[str, str]] = Future()

        def collect_port_from_stdout(line):
            # Note: this is called in a thread.
            matches = re.findall(compiled, line)

            if matches:
                host, port = matches[0]
                future.set_result((host, port))

        def on_stdout(line):
            if self.SHOW_OUTPUT:
                sys.stdout.write(f"stdout: {line.rstrip()}\n")

        def on_stderr(line):
            # Note: this is called in a thread.
            sys.stderr.write(f"stderr: {line.rstrip()}\n")

        process.on_stderr.register(on_stderr)
        process.on_stdout.register(on_stdout)

        with process.on_stdout.register(collect_port_from_stdout):
            process.start()
            if timeout > 1:
                initial_time = time.monotonic()
                while True:
                    try:
                        host, port = future.result(1)
                        break
                    except TimeoutError:
                        if time.monotonic() - initial_time >= timeout:
                            raise TimeoutError()
                        if not process.is_alive():
                            raise RuntimeError(
                                f"The process already exited with returncode: "
                                f"{process.returncode}"
                            )
            else:
                host, port = future.result(timeout)
        assert host
        self._host = host
        assert int(port) > 0, f"Expected port to be > 0. Found: {port}"
        self._port = int(port)

    def stop(self):
        if self._process is not None:
            self._process.stop()
            self._process = None


@pytest.fixture
def action_server_process(tmpdir) -> Iterator[ActionServerProcess]:
    ret = ActionServerProcess(Path(str(tmpdir)) / ".robocorp_action_server")
    yield ret
    ret.stop()


class ActionServerClient:
    def __init__(self, action_server_process: ActionServerProcess):
        self.action_server_process = action_server_process

    def build_full_url(self, url):
        host = self.action_server_process.host
        port = self.action_server_process.port
        if url.startswith("/"):
            url = url[1:]
        return f"http://{host}:{port}/{url}"

    def get_str(self, url, params: Optional[dict] = None) -> str:
        import requests

        result = requests.get(self.build_full_url(url), params=(params or {}))
        assert result.status_code == 200
        return result.text

    def get_openapi_json(self):
        return self.get_str("openapi.json")

    def get_json(self, url, params: Optional[dict] = None):
        contents = self.get_str(url, params=params)
        try:
            return json.loads(contents)
        except Exception:
            raise AssertionError(f"Unable to load: {contents!r}")

    def post_get_str(self, url, data):
        import requests

        result = requests.post(self.build_full_url(url), json=data)
        assert result.status_code == 200
        return result.text

    def post_error(self, url, status_code, data=None):
        import requests

        result = requests.post(self.build_full_url(url), json=data or {})
        assert result.status_code == status_code

    def get_error(self, url, status_code):
        import requests

        result = requests.get(self.build_full_url(url))
        assert result.status_code == status_code


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
                    "greeter_task.py",
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
