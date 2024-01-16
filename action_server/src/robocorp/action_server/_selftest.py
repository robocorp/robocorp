"""
This module contains utilities for testing and to do a 'selftest' of the 
executable even in release mode.
"""

import os
import re
import subprocess
import sys
import time
import typing
from concurrent.futures import TimeoutError
from contextlib import contextmanager
from pathlib import Path
from subprocess import CompletedProcess
from typing import Dict, Iterator, Literal, Optional, Tuple, Union

if typing.TYPE_CHECKING:
    from robocorp.action_server._robo_utils.process import Process


def is_debugger_active() -> bool:
    try:
        import pydevd  # type:ignore
    except ImportError:
        return False

    return bool(pydevd.get_global_debugger())


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

    def start(
        self,
        *,
        timeout: int = 10,
        db_file=":memory:",
        actions_sync=False,
        cwd: Optional[Path | str] = None,
        add_shutdown_api: bool = False,
        additional_args: Optional[list[str]] = None,
    ) -> None:
        from robocorp.action_server._robo_utils.process import Process
        from robocorp.action_server._settings import is_frozen

        if self.started:
            raise RuntimeError("The action process was already started.")

        self.started = True
        from concurrent.futures import Future

        if actions_sync:
            assert cwd, "cwd must be passed when synchronizing the actions."

        if is_frozen():
            base_args = [sys.executable]
        else:
            base_args = [
                sys.executable,
                "-m",
                "robocorp.action_server",
            ]
        new_args = base_args + [
            "start",
            "--actions-sync=false" if not actions_sync else "--actions-sync=true",
            "--port=0",
            "--verbose",
            f"--datadir={str(self._datadir)}",
            f"--db-file={db_file}",
        ]

        if additional_args:
            new_args = new_args + additional_args

        env = {}
        if add_shutdown_api:
            env["RC_ADD_SHUTDOWN_API"] = "1"
        process = self._process = Process(new_args, cwd=cwd, env=env)

        compiled = re.compile(r"Uvicorn running on http://([\w.-]+):(\d+)")
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
                        if is_debugger_active():
                            continue
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
        import json

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


def robocorp_action_server_run(
    cmdline,
    returncode: Union[Literal["error"], int],
    cwd=None,
    additional_env: Optional[Dict[str, str]] = None,
    timeout=None,
) -> CompletedProcess:
    from robocorp.action_server._settings import is_frozen

    if is_frozen():
        # i.e.: The entry point is our own executable.
        return run_command_line(
            [sys.executable] + cmdline, returncode, cwd, additional_env, timeout
        )
    else:
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
    return run_command_line(
        [sys.executable, "-m", python_module] + cmdline,
        returncode=returncode,
        cwd=cwd,
        additional_env=additional_env,
        timeout=timeout,
    )


def run_command_line(
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
    result = subprocess.run(
        cmdline, capture_output=True, text=True, env=cp, cwd=cwd, timeout=timeout
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
{cmdline}

"""
    )


def check_new_template(
    tmpdir: Path,
    action_server_process: ActionServerProcess,
    client: ActionServerClient,
    verbose: bool = False,
) -> None:
    from robocorp.action_server._settings import is_frozen

    curdir = os.path.abspath(".")
    try:
        os.chdir(str(tmpdir))
        if verbose:
            print(f"is_frozen(): {is_frozen()}")
            print(f"Creating template project in: {tmpdir}")

        output = robocorp_action_server_run(
            ["new", "--name=my_project"], returncode=0, cwd=str(tmpdir)
        )
        if verbose:
            print("Template creation stdout: ", output.stdout)
            print("Template creation stderr: ", output.stderr)

        my_project_dir = tmpdir / "my_project"
        my_project_dir_conda = my_project_dir / "conda.yaml"

        if verbose:
            print(my_project_dir, "exists", my_project_dir.exists())
            print(my_project_dir_conda, "exists", my_project_dir_conda.exists())

        if not my_project_dir_conda.exists():
            raise RuntimeError(f"Expected {my_project_dir_conda} to exist.")

        # Note: timeout is big because it'll use rcc to bootstrap the env here.
        if verbose:
            print("Starting action-server in template project.")
        action_server_process.start(
            db_file="server.db",
            cwd=str(tmpdir / "my_project"),
            actions_sync=True,
            timeout=300,
        )

        if verbose:
            print("Querying action packages available.")

        action_packages = client.get_json("api/actionPackages")
        assert len(action_packages) == 1
        action_package = next(iter(action_packages))
        actions = action_package["actions"]
        action_names = tuple(action["name"] for action in actions)
        assert "compare_time_zones" in action_names

        if verbose:
            print("Using post to call action.")

        found = client.post_get_str(
            "/api/actions/my-project/compare-time-zones/run",
            {
                "user_timezone": "Europe/Helsinki",
                "compare_to_timezones": "America/New_York, Asia/Kolkata",
            },
        )
        assert "Current time in Europe/Helsinki" in found
        assert "Current time in America/New_York" in found
        assert "Current time in Asia/Kolkata" in found

        if verbose:
            print("Test finished with success.")
    finally:
        os.chdir(curdir)


@contextmanager
def make_tmpdir() -> Iterator[Path]:
    import shutil
    import tempfile

    temp_dir = tempfile.mkdtemp()
    try:
        yield Path(temp_dir)
    finally:
        retry = 4
        for i in range(retry):
            try:
                shutil.rmtree(temp_dir)
                break
            except Exception:
                # It's possible that the process takes a bit longer to cleanup,
                # so, wait a bit and retry.
                time.sleep(0.4)
                if i == retry - 1:
                    raise


@contextmanager
def make_action_server_process(tmpdir: Path) -> Iterator[ActionServerProcess]:
    action_server_datadir = tmpdir / ".robocorp_action_server"
    ret = ActionServerProcess(action_server_datadir)
    try:
        yield ret
    finally:
        ret.stop()


@contextmanager
def make_client(
    action_server_process: ActionServerProcess,
) -> Iterator[ActionServerClient]:
    yield ActionServerClient(action_server_process)


def do_selftest():
    print("Running selftest...")
    retcode = 0

    from robocorp.action_server._download_rcc import get_default_rcc_location

    rcc_location = get_default_rcc_location()
    assert rcc_location.exists(), f"Expected rcc to be available in: {rcc_location}."
    print(f"Permissions for: {rcc_location}: {oct(os.stat(rcc_location).st_mode)[-3:]}")
    if not os.access(str(rcc_location), os.X_OK):
        raise AssertionError("Expected rcc to have the executable bit set.")

    try:
        with make_tmpdir() as tmpdir:
            with make_action_server_process(tmpdir) as action_server_process:
                with make_client(action_server_process) as client:
                    check_new_template(
                        tmpdir, action_server_process, client, verbose=True
                    )
    except Exception:
        print("selftest failed with error!")
        import traceback

        traceback.print_exc()
        retcode = 1

    if retcode != 0:
        print("Action server selftest failed!")
    else:
        print("Action server selftest worked!")
    return retcode
