import json
import os.path


def _fix_file(entry):
    entry["file"] = os.path.basename(entry["file"])


def test_actions_list_relative_import(datadir, data_regression):
    from devutils.fixtures import robocorp_actions_run

    result = robocorp_actions_run(["list"], returncode=0, cwd=str(datadir))
    found = json.loads(result.stdout)
    for entry in found:
        _fix_file(entry)
    data_regression.check(
        sorted(found, key=lambda entry: (entry["name"], entry["line"]))
    )
