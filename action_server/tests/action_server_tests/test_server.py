import json
import sys
import time
from pathlib import Path

import pytest
from action_server_tests.fixtures import ActionServerClient, ActionServerProcess


def test_action_server_starts(action_server_process: ActionServerProcess, tmpdir):
    action_server_process.start(db_file="server.db")
    assert action_server_process.port > 0
    assert action_server_process.host == "localhost"

    p = Path(str(tmpdir)) / ".robocorp_action_server"
    assert p.exists()
    assert (p / "server.db").exists()


def test_action_server_in_memory_db(action_server_process: ActionServerProcess, tmpdir):
    action_server_process.start()  # Default is starting in-memory
    assert action_server_process.port > 0
    assert action_server_process.host == "localhost"

    p = Path(str(tmpdir)) / ".robocorp_action_server"
    assert p.exists()
    assert not (p / "server.db").exists()


def test_schema_request_no_actions_registered(
    client: ActionServerClient, data_regression
) -> None:
    openapi_json = client.get_openapi_json()
    data_regression.check(json.loads(openapi_json))


def test_bad_return_on_no_conda(
    action_server_process: ActionServerProcess,
    client: ActionServerClient,
) -> None:
    from action_server_tests.fixtures import get_in_resources

    calculator = get_in_resources("no_conda", "calculator")
    action_server_process.start(
        db_file="server.db",
        cwd=calculator,
        actions_sync=True,
        timeout=300,
    )
    found = client.post_error("api/actions/calculator/bad-return-none/run", 500)
    assert found.json()["message"] == (
        "Error in action. Expected return type: string. "
        "Found return type: <class 'NoneType'> (value: None)."
    )


def test_run_id_in_response_header(
    action_server_process: ActionServerProcess,
    client: ActionServerClient,
) -> None:
    from action_server_tests.fixtures import get_in_resources
    from robocorp.log._log_formatting import pretty_format_logs_from_log_html_contents

    calculator = get_in_resources("no_conda", "calculator")
    action_server_process.start(
        db_file="server.db",
        cwd=calculator,
        actions_sync=True,
        timeout=300,
    )
    import requests

    result = requests.post(
        client.build_full_url("api/actions/calculator/calculator-sum/run"),
        json={"v1": 1, "v2": 2},
    )
    assert result.status_code == 200
    assert json.loads(result.text) == 3
    run_id = result.headers["X-Action-Server-Run-Id"]

    result = requests.get(
        client.build_full_url(f"api/runs/{run_id}"),
    )

    run_info = result.json()
    assert json.loads(run_info["inputs"]) == {"v1": 1, "v2": 2}
    assert json.loads(run_info["result"]) == 3
    assert run_info["id"] == run_id

    artifacts_response = client.get_json(
        f"api/runs/{run_id}/artifacts/text-content",
        params={
            "artifact_names": [
                "log.html",
            ]
        },
    )
    log_html_contents = artifacts_response["log.html"]
    log_pretty_printed = pretty_format_logs_from_log_html_contents(log_html_contents)

    # Note: there are more contents, but the ones below are the ones we cane about
    expected = """
SR: calculator_tasks.py - calculator_sum
    ST: Collect tasks
    ET: PASS
    ST: calculator_sum
        SE: METHOD: calculator_sum
            EA: float: v1: 1.0
            EA: float: v2: 2.0
            R: float: 3.0
        EE: METHOD: PASS
        SE: METHOD: on_teardown_save_result
        EE: METHOD: PASS
    ET: PASS
    ST: Teardown tasks
    ET: PASS
ER: PASS
"""

    for line in expected:
        assert line in log_pretty_printed, f"'{line}' not in:\n{log_pretty_printed}"


def test_global_return_reuse_process(
    action_server_process: ActionServerProcess,
    client: ActionServerClient,
) -> None:
    from action_server_tests.fixtures import get_in_resources

    calculator = get_in_resources("no_conda", "calculator")
    action_server_process.start(
        db_file="server.db",
        cwd=calculator,
        actions_sync=True,
        timeout=300,
        min_processes=1,
        max_processes=1,
        reuse_processes=True,
    )
    found = client.post_get_str(
        "api/actions/calculator/global-return-reuse-process/run", {}
    )
    assert found == '"1"'
    found = client.post_get_str(
        "api/actions/calculator/global-return-reuse-process/run", {}
    )
    assert found == '"2"'


@pytest.mark.parametrize("strategy", ["action-server.yaml", "conda.yaml", "no-conda"])
def test_import_action_server_strategies(
    action_server_datadir: Path,
    strategy: str,
) -> None:
    from action_server_tests.fixtures import (
        get_in_resources,
        robocorp_action_server_run,
    )

    from robocorp.action_server._models import Action, ActionPackage, load_db

    if strategy == "conda.yaml":
        root_dir = get_in_resources("calculator")
    elif strategy == "action-server.yaml":
        root_dir = get_in_resources("greeter")
    else:
        assert strategy == "no-conda"
        root_dir = get_in_resources("no_conda", "greeter")

    robocorp_action_server_run(
        [
            "import",
            f"--dir={root_dir}",
            "--db-file=server.db",
            "-v",
            "--datadir",
            action_server_datadir,
        ],
        returncode=0,
    )

    db_path = action_server_datadir / "server.db"
    with load_db(db_path) as db:
        with db.connect():
            actions = db.all(Action)
            action_packages = db.all(ActionPackage)

            assert len(action_packages) == 1
            action_package = next(iter(action_packages))
            env = json.loads(action_package.env_json)

            if strategy == "conda.yaml":
                # calculator
                assert env.get("PYTHON_EXE") not in (
                    None,
                    "",
                    sys.executable,
                ), "Expected custom env"
                assert len(actions) == 2
            elif strategy == "action-server.yaml":
                # greeter
                assert len(actions) == 1
                assert env.get("PYTHON_EXE") not in (
                    None,
                    "",
                    sys.executable,
                ), "Expected custom env"
            else:
                # no_conda/greeter
                assert env.get("PYTHON_EXE") in (
                    None,
                    "",
                    sys.executable,
                ), "Expected current env"
                assert strategy == "no-conda"
                assert len(actions) == 1


def test_import_no_conda(
    action_server_process: ActionServerProcess,
    data_regression,
    str_regression,
    tmpdir,
    action_server_datadir: Path,
    client: ActionServerClient,
) -> None:
    from action_server_tests.fixtures import robocorp_action_server_run

    from robocorp.action_server._database import Database
    from robocorp.action_server._models import Action, load_db

    action_server_datadir.mkdir(parents=True, exist_ok=True)
    db_path = action_server_datadir / "server.db"
    assert not db_path.exists()

    calculator = Path(tmpdir) / "v1" / "calculator" / "action_calculator.py"
    calculator.parent.mkdir(parents=True, exist_ok=True)
    calculator.write_text(
        """
from robocorp.actions import action

@action
def calculator_sum(v1: float, v2: float) -> float:
    return v1 + v2
"""
    )

    robocorp_action_server_run(
        [
            "import",
            f"--dir={calculator.parent}",
            "--db-file=server.db",
            "-v",
            "--datadir",
            action_server_datadir,
        ],
        returncode=0,
    )

    db: Database
    with load_db(db_path) as db:
        with db.connect():
            actions = db.all(Action)
            assert len(actions) == 1

    calculator.write_text(
        """
from robocorp.actions import action

@action
def calculator_sum(v1: str, v2: str) -> str:
    return v1 + v2
    
@action
def another_action(a1: str, a2: str) -> str:
    return a1 + a2
"""
    )

    robocorp_action_server_run(
        [
            "import",
            f"--dir={calculator.parent}",
            "--db-file=server.db",
            "-v",
            "--datadir",
            action_server_datadir,
        ],
        returncode=0,
    )

    with load_db(db_path) as db:
        action_name_to_schema = {}
        with db.connect():
            actions = db.all(Action)
            assert len(actions) == 2
            for action in actions:
                action_name_to_schema[action.name] = action.input_schema
                assert action.enabled

    data_regression.check(
        action_name_to_schema, basename="test_import_no_conda_schema1"
    )

    calculator.write_text(
        """
from robocorp.actions import action

@action
def calculator_sum(v1: float, v2: float) -> float:
    return v1 + v2
"""
    )

    action_server_process.start(
        actions_sync=True, cwd=calculator.parent, db_file="server.db"
    )
    # At this point the `another_action` is in the db, but it should be
    # disabled.

    # Check that it doesn't appear in the open api spec.
    str_regression.check(json.dumps(json.loads(client.get_openapi_json()), indent=4))

    action_server_process.stop()

    with load_db(db_path) as db:
        action_name_to_enabled = {}
        with db.connect():
            actions = db.all(Action)
            assert len(actions) == 2
            for action in actions:
                action_name_to_enabled[action.name] = action.enabled

    assert action_name_to_enabled == {"calculator_sum": True, "another_action": False}


def test_import(
    action_server_process: ActionServerProcess,
    data_regression,
    base_case,
    client: ActionServerClient,
) -> None:
    from robocorp.action_server._database import Database, str_to_datetime
    from robocorp.action_server._models import Run, RunStatus, load_db

    openapi_json = client.get_openapi_json()
    data_regression.check(json.loads(openapi_json))

    db_path = base_case.db_path

    found = client.post_get_str("api/actions/greeter/greet/run", {"name": "Foo"})
    assert found == '"Hello Mr. Foo."', f"{found} != '\"Hello Mr. Foo.\"'"

    # 500 seems appropriate here as the user task didn't complete properly.
    client.post_error("api/actions/calculator/broken-action/run", 500)

    db: Database
    with load_db(db_path) as db:
        with db.connect():
            runs = db.all(Run)
            assert len(runs) == 2
            assert runs[0].status == RunStatus.PASSED
            assert runs[0].inputs == '{"name": "Foo", "title": "Mr."}'
            assert runs[0].result == '"Hello Mr. Foo."'

            assert runs[1].status == RunStatus.FAILED
            assert runs[1].inputs == "{}"
            assert runs[1].result is None

            for run in runs:
                assert (
                    run.run_time is not None and run.run_time > 0 and run.run_time < 100
                )

                # Just check that it works.
                str_to_datetime(run.start_time)

            # Check for the first run (where we write a custom artifact).
            run = runs[0]

            found = client.get_json(f"api/runs/{run.id}/artifacts")
            assert sorted(x["name"] for x in found) == sorted(
                (
                    "__action_server_inputs.json",
                    "log.html",
                    "output.robolog",
                    "__action_server_output.txt",
                    "__action_server_result.json",
                    "subdir/myfile.txt",
                )
            )

            # Multiple text files
            found = client.get_json(
                f"api/runs/{run.id}/artifacts/text-content",
                params={
                    "artifact_names": [
                        "__action_server_output.txt",
                        "output.robolog",
                    ]
                },
            )
            assert len(found) == 2
            assert (
                "Collecting task greet from: greeter_task.py"
                in found["__action_server_output.txt"]
            )
            assert '"PASS"' in found["output.robolog"]

            # Multiple given regexp
            found = client.get_json(
                f"api/runs/{run.id}/artifacts/text-content",
                params={"artifact_name_regexp": "__action_server.*"},
            )
            assert len(found) == 3

            # Just a single binary artifact
            found = client.get_str(
                f"api/runs/{run.id}/artifacts/binary-content",
                params={
                    "artifact_name": [
                        "__action_server_output.txt",
                    ]
                },
            )

            assert "Collecting task greet from: greeter_task.py" in found


def test_routes(action_server_process: ActionServerProcess, data_regression):
    from action_server_tests.sample_data import ACTION, ACTION_PACKAGE, RUN, RUN2

    from robocorp.action_server._database import Database
    from robocorp.action_server._models import create_db

    action_server_process.datadir.mkdir(parents=True, exist_ok=True)
    db_path = action_server_process.datadir / "server.db"
    db: Database
    with create_db(db_path) as db:
        with db.transaction():
            db.insert(ACTION_PACKAGE)
            db.insert(ACTION)
            db.insert(RUN)
            db.insert(RUN2)

    action_server_process.start(db_file="server.db")

    client = ActionServerClient(action_server_process)
    openapi_json = client.get_openapi_json()
    spec = json.loads(openapi_json)
    data_regression.check(spec)

    runs = client.get_json("/api/runs")
    assert len(runs) == 2
    run0 = client.get_json(f"/api/runs/{runs[0]['id']}")
    assert run0["id"] == runs[0]["id"]

    client.get_error("/api/runs/bad-run-id", 404)


def test_server_url_flag(action_server_process: ActionServerProcess, data_regression):
    action_server_process.start(additional_args=["--server-url=https://foo.bar"])

    client = ActionServerClient(action_server_process)
    openapi_json = client.get_openapi_json()
    spec = json.loads(openapi_json)
    data_regression.check(spec)


def test_server_full_openapi_flag(
    action_server_process: ActionServerProcess, data_regression
):
    action_server_process.start(additional_args=["--full-openapi-spec"])

    client = ActionServerClient(action_server_process)
    openapi_json = client.get_openapi_json()
    spec = json.loads(openapi_json)
    data_regression.check(spec)


def test_auth_routes(action_server_process: ActionServerProcess, data_regression):
    from action_server_tests.fixtures import get_in_resources

    pack = get_in_resources("no_conda", "greeter")
    action_server_process.start(
        cwd=pack,
        actions_sync=True,
        db_file="server.db",
        additional_args=["--api-key=Foo"],
    )

    client = ActionServerClient(action_server_process)
    openapi_json = client.get_openapi_json()
    spec = json.loads(openapi_json)
    data_regression.check(spec)

    client.post_error("api/actions/greeter/greet/run", 403)

    found = client.post_get_str(
        "api/actions/greeter/greet/run",
        {"name": "Foo"},
        {"Authorization": "Bearer Foo"},
    )
    assert found == '"Hello Mr. Foo."', f"{found} != '\"Hello Mr. Foo.\"'"


def test_server_process_pool(
    action_server_process: ActionServerProcess, data_regression
):
    from action_server_tests.fixtures import get_in_resources

    no_conda_dir = get_in_resources("no_conda")

    action_server_process.start(
        cwd=no_conda_dir,
        actions_sync=True,
        db_file="server.db",
        add_shutdown_api=True,
        min_processes=1,
        max_processes=2,
        reuse_processes=True,
    )


def test_subprocesses_killed(
    action_server_process: ActionServerProcess, client: ActionServerClient
):
    from concurrent.futures import TimeoutError

    import requests
    from action_server_tests.fixtures import get_in_resources

    from robocorp.action_server._robo_utils.run_in_thread import run_in_thread

    no_conda_dir = get_in_resources("no_conda")
    action_server_process.start(
        cwd=no_conda_dir, actions_sync=True, db_file="server.db", add_shutdown_api=True
    )

    def request_in_thread():
        return requests.post(
            client.build_full_url("api/actions/no-conda/neverending-action/run"),
            json={},
        )

    fut = run_in_thread(request_in_thread)
    with pytest.raises(TimeoutError):
        fut.result(0.5)

    import psutil

    p = psutil.Process(action_server_process.process.pid)
    children_processes = list(p.children(recursive=True))

    # The first shutdown will not really shutdown while there are connections
    # open, so, a timeout is given to forcefully do the shutdown.
    requests.post(client.build_full_url("api/shutdown/"), params={"timeout": 5})
    request_result = fut.result(10)
    assert request_result.status_code == 500

    times = 4
    for i in range(times):

        def is_process_alive(pid):
            # Note: the process may be a zombie process in Linux
            # (althought it's killed it remains in that state
            # because we're monitoring it).
            try:
                proc = psutil.Process(pid)
                if proc.status() == psutil.STATUS_ZOMBIE:
                    return False
            except psutil.NoSuchProcess:
                return False
            return True

        for process in children_processes:
            if is_process_alive(process.pid):
                if i == times - 1:
                    raise AssertionError(
                        f"Process: {process} - {process.cmdline()} is still running."
                    )
                else:
                    time.sleep(0.2)
                    break
        else:
            return  # Ok, everything worked


def test_import_task_options(
    action_server_process: ActionServerProcess,
    data_regression,
    str_regression,
    tmpdir,
    action_server_datadir: Path,
    client: ActionServerClient,
) -> None:
    from action_server_tests.fixtures import robocorp_action_server_run

    from robocorp.action_server._database import Database
    from robocorp.action_server._models import Action, load_db

    action_server_datadir.mkdir(parents=True, exist_ok=True)
    db_path = action_server_datadir / "server.db"
    assert not db_path.exists()

    calculator = Path(tmpdir) / "v1" / "calculator" / "action_calculator.py"
    calculator.parent.mkdir(parents=True, exist_ok=True)
    calculator.write_text(
        """
from robocorp.actions import action

@action
def calculator_sum(v1: float, v2: float) -> float:
    return v1 + v2
"""
    )

    robocorp_action_server_run(
        [
            "import",
            f"--dir={calculator.parent}",
            "--db-file=server.db",
            "-v",
            "--datadir",
            action_server_datadir,
        ],
        returncode=0,
    )

    db: Database
    with load_db(db_path) as db:
        with db.connect():
            actions = db.all(Action)
            assert len(actions) == 1
            assert actions[0].is_consequential is None

    calculator.write_text(
        """
from robocorp.actions import action

@action(is_consequential=True)
def calculator_sum(v1: str, v2: str) -> str:
    return v1 + v2
"""
    )

    robocorp_action_server_run(
        [
            "import",
            f"--dir={calculator.parent}",
            "--db-file=server.db",
            "-v",
            "--datadir",
            action_server_datadir,
        ],
        returncode=0,
    )

    with load_db(db_path) as db:
        with db.connect():
            actions = db.all(Action)
            assert len(actions) == 1
            assert actions[0].is_consequential is True

    calculator.write_text(
        """
from robocorp.actions import action

@action(is_consequential=False)
def calculator_sum(v1: str, v2: str) -> str:
    return v1 + v2
"""
    )

    robocorp_action_server_run(
        [
            "import",
            f"--dir={calculator.parent}",
            "--db-file=server.db",
            "-v",
            "--datadir",
            action_server_datadir,
        ],
        returncode=0,
    )

    with load_db(db_path) as db:
        with db.connect():
            actions = db.all(Action)
            assert len(actions) == 1
            assert actions[0].is_consequential is False
