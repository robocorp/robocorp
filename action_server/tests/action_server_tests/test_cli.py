import os
import sys

from action_server_tests.fixtures import ActionServerClient, ActionServerProcess


def test_version() -> None:
    from action_server_tests.fixtures import robocorp_action_server_run

    from robocorp.action_server import __version__

    result = robocorp_action_server_run(["version"], returncode=0)
    assert result.stdout.strip() == __version__


def test_download_rcc(tmpdir) -> None:
    from action_server_tests.fixtures import robocorp_action_server_run

    rcc_location = tmpdir / "rcc.exe" if sys.platform == "win32" else "rcc"
    robocorp_action_server_run(["download-rcc", "--file", rcc_location], returncode=0)
    assert os.path.exists(rcc_location)


def test_new(
    tmpdir, action_server_process: ActionServerProcess, client: ActionServerClient
) -> None:
    from action_server_tests.fixtures import robocorp_action_server_run

    curdir = os.path.abspath(".")
    try:
        os.chdir(str(tmpdir))
        robocorp_action_server_run(["new", "--name=my_project"], returncode=0)
        assert os.path.exists(str(tmpdir / "my_project" / "conda.yaml"))

        # Note: timeout is big because it'll use rcc to bootstrap the env here.
        action_server_process.start(
            db_file="server.db",
            cwd=str(tmpdir / "my_project"),
            actions_sync=True,
            timeout=300,
        )
        action_packages = client.get_json("api/actionPackages")
        assert len(action_packages) == 1
        action_package = next(iter(action_packages))
        actions = action_package["actions"]
        action_names = tuple(action["name"] for action in actions)
        assert "compare_time_zones" in action_names

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
    finally:
        os.chdir(curdir)


# def test_schema(str_regression, tmpdir) -> None:
#     from action_server_tests.fixtures import robocorp_action_server_run
#
#     result = robocorp_action_server_run(["schema"], returncode=0)
#     output = result.stdout
#     str_regression.check(output)
#
#     out_json = Path(tmpdir / "out.json")
#     robocorp_action_server_run(["schema", "--file", str(out_json)], returncode=0)
#     contents = out_json.read_text()
#     assert output.strip() == contents.strip()


def test_help(str_regression):
    from action_server_tests.fixtures import robocorp_action_server_run

    result = robocorp_action_server_run(["-h"], returncode=0)
    str_regression.check(result.stdout)


def test_migrate(database_v0):
    from action_server_tests.fixtures import robocorp_action_server_run

    from robocorp.action_server.migrations import db_migration_pending

    db_path = database_v0
    if db_migration_pending(db_path):
        robocorp_action_server_run(
            [
                "migrate",
                "--datadir",
                str(db_path.parent),
                "--db-file",
                str(db_path.name),
            ],
            returncode=0,
        )

        assert not db_migration_pending(db_path)


def test_default_datadir(tmpdir):
    from pathlib import Path

    from robocorp.action_server._settings import setup_settings
    from robocorp.action_server.cli import _create_parser

    use_dir = Path(tmpdir) / "foobar"
    curdir = Path(".").absolute()

    try:
        use_dir.mkdir(parents=True, exist_ok=True)
        os.chdir(str(use_dir.absolute()))
        parser = _create_parser()
        base_args = parser.parse_args(["start"])

        with setup_settings(base_args) as settings:
            assert settings.datadir.name.startswith("foobar_")
    finally:
        os.chdir(str(curdir))


def test_datadir_user_specified(tmpdir):
    from pathlib import Path

    from robocorp.action_server._settings import setup_settings
    from robocorp.action_server.cli import _create_parser

    use_dir = Path(tmpdir) / "foobar"

    parser = _create_parser()
    base_args = parser.parse_args(["start", "--datadir", str(use_dir)])

    with setup_settings(base_args) as settings:
        assert Path(settings.datadir) == use_dir
