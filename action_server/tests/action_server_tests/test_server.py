import json
from pathlib import Path

import pytest
from action_server_tests.fixtures import ActionServerClient, ActionServerProcess


def test_action_server_starts(action_server_process: ActionServerProcess, tmpdir):
    action_server_process.start(("--db-file=server.db",))
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


def test_import(
    action_server_process: ActionServerProcess,
    data_regression,
    base_case,
) -> None:
    from robocorp.action_server._database import Database, str_to_datetime
    from robocorp.action_server._models import Run, RunStatus, load_db

    client = ActionServerClient(action_server_process)
    openapi_json = client.get_openapi_json()
    data_regression.check(json.loads(openapi_json))

    db_path = base_case.db_path

    found = client.post_get_str(
        "api/actions/greeter/greet/run", {"name": "Foo", "title": "Mr."}
    )
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

    action_server_process.start(("--db-file=server.db",))

    client = ActionServerClient(action_server_process)
    openapi_json = client.get_openapi_json()
    spec = json.loads(openapi_json)
    data_regression.check(spec)

    runs = client.get_json("/api/runs")
    assert len(runs) == 2
    run0 = client.get_json(f"/api/runs/{runs[0]['id']}")
    assert run0["id"] == runs[0]["id"]

    client.get_error("/api/runs/bad-run-id", 404)
