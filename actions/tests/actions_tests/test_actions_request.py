import json
from pathlib import Path


def test_actions_request_list(datadir, data_regression):
    from devutils.fixtures import robocorp_actions_run

    result = robocorp_actions_run(
        ["list", "--skip-lint"], returncode=0, cwd=str(datadir)
    )
    found = json.loads(result.stdout)
    assert len(found) == 1
    # Note: the request does not appear in the schema!
    data_regression.check(found[0]["input_schema"])


def test_actions_request_run(datadir: Path):
    from devutils.fixtures import robocorp_actions_run

    # Specifies the request in the json input.
    json_output = datadir / "json.output"
    json_input_contents = {
        "custom_cls": {"filename": str(json_output), "price": 100},
        "request": {"headers": {"x-custom-header": "value-in-header"}},
    }

    input_json = datadir / "json.input"
    input_json.write_text(json.dumps(json_input_contents))

    args = [
        "run",
        "-a",
        "action_with_request",
        datadir,
        f"--json-input={input_json}",
    ]

    robocorp_actions_run(args, returncode=0, cwd=str(datadir))
    assert json_output.read_text() == "value-in-header"
