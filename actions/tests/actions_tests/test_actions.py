import json
import os


def _fix_file(entry):
    entry["file"] = os.path.basename(entry["file"])


def test_actions_list(datadir, data_regression):
    from devutils.fixtures import robocorp_actions_run

    result = robocorp_actions_run(
        ["list", "--skip-lint"], returncode=0, cwd=str(datadir)
    )
    found = json.loads(result.stdout)
    for entry in found:
        _fix_file(entry)
    data_regression.check(
        sorted(found, key=lambda entry: (entry["name"], entry["line"]))
    )


def test_actions_run(datadir, data_regression):
    from devutils.fixtures import robocorp_actions_run

    result = robocorp_actions_run(
        [
            "run",
            "-a",
            "greet",
            "--console-colors=plain",
            "--",
            "--name",
            "NAME",
            "--title",
            "TITLE",
        ],
        returncode=0,
        cwd=str(datadir),
    )
    output = result.stdout.decode("utf-8")
    assert "my_cached_session called" in output
    assert "my_cached_action before" in output
    assert "my_cached_action after" in output
    assert "greet status: PASS" in output
    assert "before greet" in output
    assert "after greet" in output
