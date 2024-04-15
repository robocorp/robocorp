import os
import sys

import pytest
from action_server_tests.fixtures import ActionServerClient, ActionServerProcess


def test_version() -> None:
    from action_server_tests.fixtures import robocorp_action_server_run

    from robocorp.action_server import __version__

    result = robocorp_action_server_run(["version"], returncode=0)
    assert result.stdout.strip() == __version__


def test_download_rcc(tmpdir) -> None:
    from action_server_tests.fixtures import robocorp_action_server_run

    rcc_location = tmpdir / ("rcc.exe" if sys.platform == "win32" else "rcc")
    robocorp_action_server_run(["download-rcc", "--file", rcc_location], returncode=0)
    assert os.path.exists(rcc_location)


def test_new(
    tmpdir, action_server_process: ActionServerProcess, client: ActionServerClient
) -> None:
    from robocorp.action_server._selftest import check_new_template

    check_new_template(tmpdir, action_server_process, client)


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


@pytest.mark.parametrize(
    "op", ["dry_run.backup", "dry_run.no_backup", "update.backup", "update.no_backup"]
)
def test_package_update(tmpdir, str_regression, op):
    from pathlib import Path

    from action_server_tests.fixtures import robocorp_action_server_run

    tmp = Path(tmpdir)

    robot_yaml = tmp / "robot.yaml"
    robot_yaml.write_text(
        """
environmentConfigs:
  - environment_windows_amd64_freeze.yaml
  - environment_linux_amd64_freeze.yaml
  - environment_darwin_amd64_freeze.yaml
  - conda.yaml
"""
    )

    conda_yaml = tmp / "conda.yaml"
    conda_yaml.write_text(
        """
channels:
  - conda-forge

dependencies:
  - python=3.10.12
  - pip=23.2.1
  - robocorp-truststore=0.8.0
  - foo>3
  - bar>=3
  - pip:
      - robocorp==1.4.0
      - robocorp-actions==0.0.7
      - playwright>1.1
      - pytz==2023.3
"""
    )

    assert (
        "Command for package operation not specified."
        in robocorp_action_server_run(["package"], returncode=1).stderr
    )

    if op == "dry_run.no_backup":
        result = robocorp_action_server_run(
            ["package", "update", "--dry-run", "--no-backup"], returncode=0, cwd=tmp
        )
        assert (tmp / "robot.yaml").exists()
        assert (tmp / "conda.yaml").exists()
        assert not (tmp / "package.yaml").exists()

    elif op == "dry_run.backup":
        result = robocorp_action_server_run(
            ["package", "update", "--dry-run"], returncode=0, cwd=tmp
        )
        assert (tmp / "robot.yaml").exists()
        assert (tmp / "conda.yaml").exists()
        assert not (tmp / "package.yaml").exists()

    elif op == "update.backup":
        result = robocorp_action_server_run(
            ["package", "update"], returncode=0, cwd=tmp
        )
        assert (tmp / "robot.yaml.bak").exists()
        assert (tmp / "conda.yaml.bak").exists()
        assert (tmp / "package.yaml").exists()

    elif op == "update.no_backup":
        result = robocorp_action_server_run(
            ["package", "update", "--no-backup"], returncode=0, cwd=tmp
        )
        assert not (tmp / "robot.yaml.bak").exists()
        assert not (tmp / "conda.yaml.bak").exists()
        assert not (tmp / "robot.yaml").exists()
        assert not (tmp / "conda.yaml").exists()
        assert (tmp / "package.yaml").exists()

    str_regression.check(result.stdout)
