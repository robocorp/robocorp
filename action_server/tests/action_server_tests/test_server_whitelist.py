import json
from pathlib import Path

from robocorp.action_server._selftest import ActionServerClient, ActionServerProcess
from robocorp.action_server._whitelist import accept_action


def test_whitelist_exact_match():
    """Tests if an exact match is accepted."""
    assert accept_action("action1", "package", "action1")
    assert not accept_action("action1", "any-package-name", "action2")


def test_whitelist_package_match():
    """Tests if an action in a specific package is accepted."""
    assert accept_action("package1/action1", "package1", "action1")
    assert not accept_action("package1/action1", "package2", "action1")


def test_whitelist_wildcard_match():
    """Tests if an action is accepted using wildcards."""
    assert accept_action("action*", "any-name", "action1")
    assert accept_action("action*", "any-name", "action_name")
    assert not accept_action("other_action*", "any-name", "action1")


def test_whitelist_multiple_patterns():
    """Tests if multiple patterns separated by comma are accepted."""
    assert accept_action("action1,action2", "any-name", "action1")
    assert accept_action("action1,action2", "any-name", "action2")
    assert not accept_action("action1,action2", "any-name", "action3")


def test_whitelist_hyphen_underscore_match():
    """Tests if hyphens and underscores are treated interchangeably."""
    assert accept_action("action_1", "any-name", "action-1")
    assert accept_action("action-2", "any-name", "action_2")


def test_whitelist_on_import(
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
    
@action
def calculator_subtract(v1: float, v2: float) -> float:
    return v1 - v2
"""
    )

    robocorp_action_server_run(
        [
            "import",
            f"--dir={calculator.parent}",
            "--db-file=server.db",
            "-v",
            "--skip-lint",
            "--datadir",
            action_server_datadir,
            "--whitelist",
            "calculator_sum",
        ],
        returncode=0,
    )

    db: Database
    with load_db(db_path) as db:
        with db.connect():
            actions = db.all(Action)
            assert len(actions) == 1


def test_whitelist_on_start(
    action_server_process: ActionServerProcess,
    str_regression,
    tmpdir,
    client: ActionServerClient,
) -> None:
    calculator = Path(tmpdir) / "v1" / "calculator" / "action_calculator.py"
    calculator.parent.mkdir(parents=True, exist_ok=True)
    calculator.write_text(
        """
from robocorp.actions import action

@action
def calculator_sum(v1: float, v2: float) -> float:
    return v1 + v2
    
@action
def calculator_subtract(v1: float, v2: float) -> float:
    return v1 - v2
"""
    )

    action_server_process.start(
        db_file="server.db",
        cwd=calculator.parent,
        timeout=50,
        actions_sync=True,
        additional_args=["--whitelist", "calculator_sum"],
    )

    str_regression.check(json.dumps(json.loads(client.get_openapi_json()), indent=4))
