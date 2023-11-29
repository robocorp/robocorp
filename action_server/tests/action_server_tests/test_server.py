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
    datadir,
    tmpdir,
    data_regression,
    fast_local_test_path,
) -> None:
    from action_server_tests.fixtures import robocorp_action_server_run

    from robocorp.action_server._database import Database
    from robocorp.action_server._models import (
        Action,
        ActionPackage,
        get_all_model_classes,
    )

    p = Path(str(tmpdir)) / ".robocorp_action_server"
    db_path = p / "server.db"
    assert not db_path.exists()

    pack1 = datadir / "calculator"
    pack2 = datadir / "greeter"
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

    assert db_path.exists()
    db = Database(db_path)
    db.register_classes(get_all_model_classes())
    with db.connect():
        assert set(x.name for x in db.all(ActionPackage)) == {"calculator", "greeter"}
        found = set(x.name for x in db.all(Action))
        assert found == {"calculator_sum", "greet", "broken_action"}
        if fast_local_test_path:
            Path(fast_local_test_path).write_text(
                json.dumps(db.list_whole_db(), indent=4)
            )

    return
    action_server_process.start(
        ("--db-file=server.db",),
        timeout=500,
    )
    client = ActionServerClient(action_server_process)
    openapi_json = client.get_openapi_json()
    data_regression.check(json.loads(openapi_json))

    check_runs_after_import_db(client, db_path)


def check_runs_after_import_db(client: ActionServerClient, db_path):
    from robocorp.action_server._database import Database, str_to_datetime
    from robocorp.action_server._models import Run, RunStatus, initialize_db

    found = client.post_get_str(
        "api/actions/greeter/greet/run", {"name": "Foo", "title": "Mr."}
    )
    assert found == '"Hello Mr. Foo."', f"{found} != '\"Hello Mr. Foo.\"'"

    # 500 seems appropriate here as the user task didn't complete properly.
    client.post_error("api/actions/calculator/broken-task/run", 500)

    db: Database
    with initialize_db(db_path) as db:
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


def test_fast(action_server_process: ActionServerProcess, db_from_test_import):
    action_server_process.start(("--db-file=server.db",))

    check_runs_after_import_db(
        ActionServerClient(action_server_process), db_from_test_import
    )


@pytest.fixture(scope="session")
def fast_local_test_path(pytestconfig):
    # When `test_import` is executed, if `FAST_LOCAL_TEST_PATH` is defined,
    # it'll dump the database to it. In this case we can do just the part
    # of the test with the database loaded here.
    return pytestconfig.getoption("path_to_store_json_db")


@pytest.fixture
def db_from_test_import(
    action_server_process: ActionServerProcess, fast_local_test_path
):
    if not fast_local_test_path:
        pytest.skip(reason="Requires --path-to-store-json-db in the command line")
    # Initialize the db from what was saved in the 'FAST_LOCAL_TEST_PATH'.
    from robocorp.action_server._database import Database
    from robocorp.action_server._models import initialize_db

    action_server_process.datadir.mkdir(parents=True, exist_ok=True)
    db_path = action_server_process.datadir / "server.db"
    db: Database
    with initialize_db(db_path) as db:
        data = json.loads(Path(fast_local_test_path).read_text())
        db.load_whole_db(data)
    return db_path


def test_routes(action_server_process: ActionServerProcess, data_regression):
    from action_server_tests.sample_data import ACTION, ACTION_PACKAGE, RUN, RUN2

    from robocorp.action_server._database import Database
    from robocorp.action_server._models import initialize_db

    action_server_process.datadir.mkdir(parents=True, exist_ok=True)
    db_path = action_server_process.datadir / "server.db"
    db: Database
    with initialize_db(db_path) as db:
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
